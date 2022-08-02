from __future__ import annotations
import os
import numpy as np
import re
import json
from pdf2image import convert_from_bytes

from dataclasses import dataclass
from typing import Dict, List, Any, Optional, Tuple
import io
from tqdm import tqdm
import base64
from uuid import uuid4

from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter, resolve1
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox, LTTextLine, LTChar, LTImage, LTFigure, LTAnno
from pdfminer.pdffont import PDFCIDFont, PDFUnicodeNotDefined, PDFTrueTypeFont

from PIL import Image
import matplotlib.pyplot as plt


############################ Data Types ##################################
##########################################################################

@dataclass
class Bbox:
    left: float
    top: float
    width: float
    height: float

    @staticmethod
    def merge(bs):
        left = min(b.left for b in bs)
        top = min(b.top for b in bs)
        return Bbox(
            left, top,
            max(b.left+b.width for b in bs) - left,
            max(b.top+b.height for b in bs) - top
        )

    def overlap(b1, b2):
        area = min(b1.width*b1.height, b2.width*b2.height)
        a = (min(b1.left+b1.width, b2.left+b2.width) - max(b1.left, b2.left))
        b = (min(b1.top+b1.height, b2.top+b2.height)) - max(b1.top, b2.top)
        return a*b / area

@dataclass
class BoundObject:
    bbox: Bbox

class Font:
    def __init__(self, name):
        parts = name.split("-")
        self.title = parts[0]
        if len(parts) == 2:
            meta = parts[1].lower()
            self.bold = "bold" in meta or "bd" in meta or "semibold" in meta
            self.italic = "italic" in meta
        else:
            self.bold = False
            self.italic = False

@dataclass
class SpanFormat:
    font: int
    size: float
    bold: bool
    italic: bool
    h2: bool
    h1: bool

@dataclass
class Span:
    format: SpanFormat
    text: str

@dataclass
class OutlineItem:
    level: int
    text: str
    ref: Any

@dataclass
class Line:
    spans: List[Span]

@dataclass
class Box(BoundObject):
    lines: List[Line]

@dataclass
class Figure(BoundObject):
    image: Any

@dataclass
class Container(BoundObject):
    type: str
    children: List[BoundObject]

@dataclass
class Page(Container):
    page_image : Any
    images: List[BoundObject]

@dataclass
class Document:
    title: str
    author: str
    outline: List[Any]
    pages: List[Page]
    dps: DocumentParseState

############################# Overrides ##################################
##########################################################################

def fixed_get_filters(self) -> List[Tuple[Any, Any]]:
        filters = self.get_any(("F", "Filter"))
        params = self.get_any(("DP", "DecodeParms", "FDecodeParms"), {})
        if not filters:
            return []
        if not isinstance(filters, list):
            filters = [filters]
        if not isinstance(params, list):
            # Make sure the parameters list is the same as filters.
            params = [params] * len(filters)
        # resolve filter if possible
        _filters = []
        for fltr in filters:
            if hasattr(fltr, "resolve"):
                fltr = fltr.resolve()
                try:
                    fltr = fltr[0]
                except:
                    pass
            _filters.append(fltr)
        # return list solves https://github.com/pdfminer/pdfminer.six/issues/15
        return list(zip(_filters, params))


LIGATURE_MAP = {
    "\ufb00": "ff",
    "\ufb01": "fi",
    "\ufb02": "fl",
    "\ufb03": "ffi",
    "\ufb04": "ffl",
    "\ufb05": "ft",
    "\ufb06": "st",
}

FONT_OVERRIDES = {
    "Calibri": {
        332:"ft",
        415:"ti",
        425:"t",
        427:"t",
        976:'f',
        980:"st",
    },
    "Cambria": {
        332:"ft",
        415:"ti",
        425:"t",
        427:"t",
        976:'f',
        980:"st",
    },
    "AlegrayaSans-Regular": {
        143: "f",
        145: "fi",
        155: "f"
    }
}

def override_render_char(self, matrix, font, fontsize, scaling, rise, cid, ncs=None,
                    graphicstate=None):
        try:
            text = font.to_unichr(cid)
            assert isinstance(text, str), str(type(text))
        except PDFUnicodeNotDefined:
            text = self.handle_undefined_char(font, cid)
        textwidth = font.char_width(cid)
        textdisp = font.char_disp(cid)

        err = False

        if isinstance(font, PDFTrueTypeFont) or isinstance(font, PDFCIDFont):
            font_title = font.basefont.split("-")[0]

            if text == "\x00":
                if font_title in FONT_OVERRIDES and cid in FONT_OVERRIDES[font_title]:
                    text = FONT_OVERRIDES[font_title][cid]
                else:
                    err = True

        if text in LIGATURE_MAP:
            text = LIGATURE_MAP[text]

        item = LTChar(matrix, font, fontsize, scaling, rise, text, textwidth,
                      textdisp, ncs, graphicstate)

        self.cur_item.add(item)

        return item.adv

############################ Processing ##################################
##########################################################################



class DocumentParseState:
    def __init__(self, page_size):
        self.page_size = page_size
        self.fonts = []
        self.font_lookup = {}
        self.font_sizes = {}
        self.large_font = None
        self.very_large_font = None

    def finalise(self):
        arr = np.zeros(shape=(max(self.font_sizes.values())+1))
        for size,count in self.font_sizes.items():
            arr[int(size)] = count

        for val in range(arr.argmax()+1, 30):
            if arr[val-1] == 0 and arr[val] > 0.001:
                if not self.large_font:
                    self.large_font = val
                    self.very_large_font = val+1
                    continue
                else:
                    self.very_large_font = val
                    break 

def get_size(dps: DocumentParseState, lt):
    s = round(lt.size, 0)
    if s in dps.font_sizes:
        dps.font_sizes[s] += 1
    else:
        dps.font_sizes[s] = 1
    return s

def get_font(dps: DocumentParseState, lt):
    if lt.fontname in dps.font_lookup:
        return dps.font_lookup[lt.fontname]
    else:
        dps.fonts.append(Font(lt.fontname))
        dps.font_lookup[lt.fontname] = len(dps.fonts) - 1
        return dps.font_lookup[lt.fontname]
      
def get_box(dps: DocumentParseState, lt):
    return Bbox(
        round(lt.bbox[0]                       / dps.page_size[0],  2), 
        round((dps.page_size[1] - lt.bbox[1])  / dps.page_size[1],  2), 
        round(min(1., (lt.bbox[2]-lt.bbox[0])  / dps.page_size[0]), 2), 
        round(min(1, (lt.bbox[3] - lt.bbox[1]) / dps.page_size[1]), 2)
    )

def to_line(dps: DocumentParseState, lt):
    if isinstance(lt, LTTextLine):
        chars = [c for c in lt._objs if isinstance(c, LTChar)]
    elif isinstance(lt, LTChar):
        chars = [lt]

    if len(chars) < 1:
        return None
    
    spans = []
    span = [chars[0].get_text()]
    font = get_font(dps, chars[0])
    size = get_size(dps, chars[0])
    written = False
    for c in chars[1:]:
        new_font = get_font(dps, c)
        new_size = get_size(dps, c)
        if (font == new_font and size == new_size):
            span.append(c.get_text())
            written = False
        else:
            spans.append(Span(SpanFormat(font, size, False, False, False, False), "".join(span)))
            font = new_font
            size = new_size
            span = [c.get_text()]
            written = True
    if not written:
        spans.append(Span(SpanFormat(font, size, False, False, False, False), "".join(span)))

    return Line(spans)

def filter_overlapping_lines(lts: List[Any]):
    filtered = []
    for lt in lts:
        if not isinstance(lt, LTTextLine):
            continue
        
        add = True
        for f in filtered:
            overlap = [False, False]
            if lt.is_voverlap(f):
                overlap[0] = True
            if lt.is_hoverlap(f):
                overlap[1] = True
            if overlap[0] and overlap[1]:
                add = False
                break
        if add:
            filtered.append(lt)
    return filtered

def merge_parallel_spans(boxes):

    if len(boxes) > 0:
        merged = boxes[0]
        final = []
        for box in boxes[1:]:
            if len(box.lines) == len(merged.lines) and abs(box.bbox.top - merged.bbox.top) < 0.01:
                for bl, ml in zip(box.lines, merged.lines):
                    ml.spans += [Span(bl.spans[0].format, "\t")] + bl.spans
                merged.bbox = Bbox.merge([merged.bbox, box.bbox])
            else:
                final.append(merged)
                merged = box
        final.append(merged)
        return final
    else:
        return []

def recursive_parse_page(dps: DocumentParseState, lt: Any):
    results = []
    images = []

    if isinstance(lt, LTTextBox):
        lines = filter_overlapping_lines(lt._objs)
        box = Box(get_box(dps, lt), [to_line(dps, l) for l in lines])
        if box.bbox.left < 0.95 and box.bbox.top < 0.95 and box.bbox.top > 0.04:
            results.append(box)
    elif isinstance(lt, LTTextLine) or isinstance(lt, LTChar):
        box = Box(get_box(dps, lt), [to_line(dps, lt)])
        if box.bbox.left < 0.95 and box.bbox.top < 0.95 and box.bbox.top > 0.04:
            results.append(box)
    elif isinstance(lt, LTImage):
        image_data = handle_lt_image(lt)
        if image_data:
            images.append(Figure(get_box(dps, lt), image_data))
    else:
        if hasattr(lt, "_objs"):
            for o in lt._objs:
                rs, ims = recursive_parse_page(dps, o)
                results += rs
                images += ims

    #### Merge boxes that are separated horizontally
    results = merge_parallel_spans(results)

    return results, images
    
def parse_page(dps, page_layout, page_size, page_image):
    text, images = recursive_parse_page(dps, page_layout)
    page = Page(get_box(dps, page_layout), "page", text, page_image, images)
    return page

def extract_outline(document):
    try:
        outline = document.get_outlines()
        parsed_outline = []
        for o in outline:
            destination = resolve1(o[3])['D']
            if isinstance(destination, list):
                destination = destination[0]

            parsed_outline.append(OutlineItem(o[0], o[1].strip(), destination))
    except Exception as e:
        print(e)
        return []

    return parsed_outline

def extract_content(dps, document, page_images, page_start, num_pages, overrides):
    if not document.is_extractable:
        raise PDFTextExtractionNotAllowed

    rsrcmgr = PDFResourceManager()
    laparams = LAParams(all_texts=False, detect_vertical=True, boxes_flow=-1)

    device = PDFPageAggregator(rsrcmgr, laparams=laparams)

    ### Hacky monkey patching to handle missing CID entries for various fonts
    device.render_char = lambda *args, **kwargs: override_render_char(device, *args, **kwargs)

    interpreter = PDFPageInterpreter(rsrcmgr, device)   
    pages = []
    num_pages = resolve1(document.catalog['Pages'])['Count'] if not num_pages else num_pages
    pages = PDFPage.create_pages(document)

    page_layouts = []

    for j, page_and_page_image in enumerate(tqdm(zip(pages, page_images), total=num_pages)):
        if j < page_start:
            continue
        if j  == page_start + num_pages:
            break

        page = page_and_page_image[0]
        page_image = page_and_page_image[1]

        interpreter.process_page(page)
        page_data = device.get_result() 

        size = (page.mediabox[2], max(page.mediabox[1], page.mediabox[3]))
        print(size, page.mediabox)
        dps.page_size = size
        page_layouts.append(parse_page(dps, page_data, size, page_image))

    return page_layouts


def get_default_config():
    return {
        "overrides": {
            "ligatures":{},
            "cid_overrides":{}
        }
    }

def parse_document(pdf, page_start=0, pages=-1):

    if os.path.exists("config.json"):
        with open("config.json", 'r') as f:
            config = json.load(f)
    else:
        config = get_default_config()

    parser = PDFParser(pdf)
    document = PDFDocument(parser)
    
    pdf.seek(0)
    dps = DocumentParseState(None)
    print("Page Images")
    page_images = extract_page_images(pdf, page_start, pages)
    #page_images = [None for i in range(pages)]
    print("Outlines")
    outline = extract_outline(document)
    print("Content")
    pages = extract_content(dps, document, page_images, page_start, pages, config)

    title = None
    author = None
    if len(document.info) > 0:
        if "Title" in document.info:
            title = document.info["Title"]
        if "Author" in document.info:
            author = document.info["Author"]

    

    doc = Document(
        title, author, outline, pages, dps
    )  

    enrich_document_text(doc)
    return doc



######################### Image Functions ################################
##########################################################################

image_number = 0

def image_to_webp_b64(image: Image) -> bytes:
        buffer = io.BytesIO()
        image.save(buffer, format="WEBP")

        global image_number
        with open(f"images/image_{image_number}.webp", 'wb') as f:
            image.convert('RGB').save(f, "webp")
            image_number = image_number + 1


        return base64.b64encode(buffer.getvalue())

def handle_raw_image(image: LTImage) -> Image:
    """Save an image without encoding, just bytes. 
    Modified from https://github.com/pdfminer/pdfminer.six/blob/master/pdfminer/image.py"""
    width, height = image.srcsize
    channels = len(image.stream.get_data()) / width / height / (image.bits / 8)

    mode = "RGB"
    if image.bits == 1:
        mode = "1"
    elif image.bits == 8 and channels == 1:
        mode = "L"
    elif image.bits == 8 and channels == 3:
        mode = "RGB"
    elif image.bits == 8 and channels == 4:
        mode = "CMYK"

    img = Image.frombytes(mode, image.srcsize, image.stream.get_data(), "raw")
    return img

def convert_lt_to_pil(img: LTImage):
    ### Handle bug caused by some FlatDecodes not being resolved correctly
    img.stream.get_filters = lambda: fixed_get_filters(img.stream)
    filters = img.stream.get_filters()
    if filters[-1][0].name == "FlateDecode":
        return handle_raw_image(img)
    else:
        #image_type = determine_image_type(image_data)
        image_data = img.stream.get_data()
        return Image.open(io.BytesIO(image_data))	

def handle_lt_image(im: LTImage) -> Optional[bytes]:
    created_image = convert_lt_to_pil(im)
    transparency_mask = im.stream.get_any(["SMask"])
    if transparency_mask is not None:
        transparency_mask = transparency_mask.resolve()
        if transparency_mask:
            try:
                transparency_mask = LTImage(uuid4(), transparency_mask, im.bbox)
                mask_image = convert_lt_to_pil(transparency_mask)
                mask_image = mask_image.resize(size=(created_image.width, created_image.height))
                created_image.putalpha(mask_image)
            except:
                pass

    return image_to_webp_b64(created_image)



####################### Enrichment Functions #############################
##########################################################################

def enrich_span(span, dps):
    #print(span)
    if dps.very_large_font and span.format.size > dps.very_large_font:
        span.format.h1 = True
    elif dps.large_font and span.format.size  > dps.large_font:
        span.format.h2 = True
    
    if dps.fonts[span.format.font].bold:
        span.format.bold = True
    if dps.fonts[span.format.font].italic:
        span.format.italic = True

def enrich_document_text(document):
    document.dps.finalise()
    for page in document.pages:
        for box in page.children:
            for line in box.lines:
                for span in line.spans:
                    enrich_span(span, document.dps)


######################## Utility Functions ###############################
##########################################################################

def extract_page_images(file, start=None, end=None):
    return convert_from_bytes(file.read(), size=1080, first_page=start, last_page=None)


def __recurse_to_list(container):
    res = []
    for child in container.children:
        if isinstance(child, Container):
            res += __recurse_to_list(child)
        else:
            res.append(child)
    return res

def draw_page(page):
    draw_container(page.page_image, page)

def draw_container(image, container):
    colormap = {
        "Box":"blue",
        "Line":"red",
        "Figure":"green",
        "Page":"black",
        "Container":"purple"
    }
    _, ax = plt.subplots(figsize=(20, 10))
    plt.imshow(image)

    for child in __recurse_to_list(container):
        col = colormap[type(child).__name__]
        bb = child.bbox
        rect = plt.Rectangle(xy=(bb.left, 1-bb.top), width=bb.width, height=bb.height, 
            edgecolor=col, facecolor='none', transform=ax.transAxes)
        ax.add_patch(rect)
    plt.axis("off")
    plt.show()

def format_line_as_html(line: Line):
    text = ""
    for s in line.spans:
        span_text = s.text
        if s.format.bold:
            span_text = f"<b>{span_text}</b>"
        if s.format.italic:
            span_text = f"<i>{span_text}</i>"
        if s.format.h1:
            span_text = f"</p><h1>{span_text}</h1><p>"
        elif s.format.h2:
            span_text = f"</p><h2>{span_text}</h2><p>"
        text += span_text
    
    text = f"<p>{text.strip()}</p>"
    text = re.sub("</([pbih12]+)>([\t\s]*)<\\1>", "\g<2>", text)
    text = re.sub("<p>\s*</p>","", text)
    return text.strip()