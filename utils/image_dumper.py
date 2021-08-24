import sys
import os
from tqdm import tqdm

from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.layout import LAParams, LTImage
from pdfminer.converter import PDFPageAggregator


from binascii import b2a_hex
import hashlib

from typing import List, Union, Any

def determine_image_type (stream):
	"""Find out the image file type based on the magic number comparison of the first 4 (or 2) bytes"""
	stream_first_4_bytes = stream[:4]
	file_type = None
	bytes_as_hex = b2a_hex(stream_first_4_bytes).decode()
	if bytes_as_hex.startswith('ffd8'):
		file_type = '.jpeg'
	elif bytes_as_hex == '89504e47':
		file_type = '.png'
	elif bytes_as_hex == '47494638':
		file_type = '.gif'
	elif bytes_as_hex.startswith('424d'):
		file_type = '.bmp'
	elif bytes_as_hex.startswith("4949") or bytes_as_hex.startswith("4d4d"):
		file_type = ".tiff"
	else:
		file_type = ".tiff"
	return file_type

def dump_images(filepath: str, outdir: str):
    '''Reads PDF and dumps all images to the output directory'''

    if not os.path.exists(filepath):
        print("File {} does not exist".format(filepath))
        return None

    if not os.path.exists(outdir):
        os.makedirs(outdir)

    with open(filepath, 'rb') as f:
        parser = PDFParser(f)
        document = PDFDocument(parser)

        if not document.is_extractable:
            raise PDFTextExtractionNotAllowed
        
        rsrcmgr = PDFResourceManager()
        laparams = LAParams(all_texts=True)

        device = PDFPageAggregator(rsrcmgr, laparams=laparams)
        interpreter = PDFPageInterpreter(rsrcmgr, device)   
        
        found_images = set()

        name = os.path.basename(filepath).split(".")[0]
        for i,page in enumerate(tqdm(PDFPage.create_pages(document))):
            interpreter.process_page(page)

            # y_size = page.mediabox[3]
            # x_size = page.mediabox[2]
            layout = device.get_result()

            images = []
            for lt in layout:
                ims = recursive_filter_to_images(lt)
                images += ims

            for j,im in enumerate(images):
                try:
                    data = im.stream.get_data()
                except:
                    print("Failed to render image {} on page {}".format(im, i))
                    continue
                type = determine_image_type(data)
                hash = hashlib.sha256(data).hexdigest()

                #Skip images we've already seen
                if hash in found_images:
                    continue

                found_images.add(hash)

                # if im.srcsize[0] == x_size and im.srcsize[1] == y_size:
                #     continue

                with open(os.path.join(outdir, f"{name}_{i}_{j}{type}"), 'wb') as f:
                    f.write(data)


def recursive_filter_to_images(lt: Any) -> List[LTImage]:
    images = []
    if isinstance(lt, LTImage):
        images.append(lt)
    else:
        if hasattr(lt, "_objs"):
            for o in lt._objs:
                images += recursive_filter_to_images(o)
    return images


if __name__ == "__main__":
    dump_images(sys.argv[1], sys.argv[2])