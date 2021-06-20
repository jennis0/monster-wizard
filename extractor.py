import matplotlib.pyplot as plt
import cv2
         
def drawBoundingBoxes(imageData, boxes, color = (0, 120, 0, 120)):
    """Draw bounding boxes on an image.
    imageData: image data in numpy array format
    inferenceResults: inference results array off object (l,t,w,h)
    colorMap: Bounding box color candidates, list of RGB tuples.
    """
    if len(color) != len(boxes):
        colors = [color for i in range(len(boxes))]
    else:
        colors = color

    for res,c in zip(boxes, colors):
        left = int(res['left'])
        top = int(res['top'])
        right = int(res['left']) + int(res['width'])
        bottom = int(res['top']) + int(res['height'])
        imgHeight, imgWidth, _ = imageData.shape
        thick = int((imgHeight + imgWidth) // 900)
        cv2.rectangle(imageData,(left, top), (right, bottom), c, thick)

    plt.figure(figsize=(20, 20))
    RGB_img = cv2.cvtColor(imageData, cv2.COLOR_BGR2RGB)
    plt.imshow(RGB_img, )



class StatblockExtractor(object):

    def __init__(self, data_loader, columniser, line_annotator, clusterer, cluster_annotator, statblock_generator):
        self.data_loader = data_loader
        self.columniser = columniser
        self.line_annotator = line_annotator
        self.clusterer = clusterer
        self.cluster_annotator = cluster_annotator
        self.statblock_generator = statblock_generator

        self.data = {}
        self.statblocks = {}

        self.line_colour = (120, 0, 0, 120)
        self.column_colour = (0, 120, 0, 120)
        self.hierarchy_colour = (0, 0, 120, 120)
        self.statblock_colour = (200, 50, 50, 250) 

    def load_data(self, pages=None):
        if isinstance(pages, str):
            pages = [pages]
        if pages:
            for p in pages:
                self.data[p] = self.data_loader.load(p)
        else:
            self.data = self.data_loader.loadall()

    def get_pages(self):
        if self.data:
            return [list(self.data.keys()), self.data_loader.list()]
        else:
            return [None, self.data_loader.list()]

    def parse(self, pages=None, draw_lines=False, draw_columns=False, draw_statblocks=False, draw_clusters=False, draw_final_columns=False):
        ### Load Data
        if pages:
            if isinstance(pages, str):
                pages = [pages]
            for p in pages:
                if p not in self.data:
                    self.data[p] = self.data_loader.load(p)
        else:
            if len(self.data.keys()) == 0:
                self.data = self.data_loader.loadall()
            pages = self.data.keys()

        draw = draw_lines or draw_columns or draw_statblocks or draw_clusters

        for p in pages:
            print("Loading {}".format(p))
            d = self.data[p]        

            boxes = []
            colours = []

            if draw_lines:
                boxes += [x[1] for x in d["lines"]]
                colours += [self.line_colour for i in range(len(d["lines"]))]

             ### Parse data into sections
            self.columniser.find_columns(d)

            if draw_columns:
                boxes += [x[1] for x in d["columns"]]
                colours += [self.column_colour for i in range(len(d["columns"]))]

            ### Generate line annotations
            for col in d["columns"]:
                self.line_annotator.annotate(col[0])

            ### Combine lines into clusters
            clusters = []
            for col in d["columns"]:
                clusters.append(self.clusterer.cluster(col[0]))

            if draw_clusters:
                for col in clusters:
                    boxes += [x[1] for x in col]
                    colours += [self.hierarchy_colour for i in range(len(col))]

            ### Combine line annotations into cluster annotations
            for col in clusters:
                self.cluster_annotator.annotate(col)

            ### Generate statblocks from clusters
            self.statblocks[p] = self.statblock_generator.create_statblocks(clusters)

            if draw_statblocks:
                boxes += [s[1] for s in self.statblocks[p]]
                colours += [self.statblock_colour for i in range(len(self.statblocks[p]))]
            
            ### Recalculate columns within statblocks
            columned_statblocks = []
            if len(self.statblocks[p]) > 0:
                for sb in self.statblocks[p]:
                    sb_to_columns = {"lines":sb[0]}
                    self.columniser.find_columns(sb_to_columns, second_pass=True)
                    if draw_final_columns:
                        boxes += [x[1] for x in sb_to_columns["columns"]]
                        colours += [self.column_colour for i in range(len(sb_to_columns["columns"]))]

                    columned_statblocks.append([[], sb[1]])
                    for col in sb_to_columns["columns"]:
                        columned_statblocks[-1][0] += col[0]
            self.statblocks[p] = columned_statblocks

            for sb in self.statblocks[p]:
                sb[0].append(["", {"left":0, "right":0, "width":0, "height":0}, ["end"]])

            
            if draw:
                drawBoundingBoxes(d["img"], boxes, colours)

        return self.statblocks