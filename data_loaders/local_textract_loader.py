import os
import json
import cv2

class LocalTextractLoader(object):

    def __init__(self, path):
        self.path = path

    def list(self):
        return os.listdir(self.path)

    def loadall(self):
        data = {}
        for page in os.listdir(self.path):
            data[page] = self.load(page)
        return data

    def load(self, page):

        path = os.path.join(self.path, page)
        out = {"path":path}
        fns = os.listdir(path)

        #Load Image
        for fn in fns:
            if fn.endswith(".png") or fn.endswith(".jpg"):
                out["img"] = cv2.imread(os.path.join(path, fn))
                out["shape"] = out["img"].shape
                break
        
        #Load Textract Response
        for fn in fns:
            if fn == "apiResponse.json":
                with open(os.path.join(path, fn), 'r') as f:
                    resp = json.load(f)
                    out["resp"] = resp
                    lines = []
                    for box in resp["Blocks"]:
                        if box["BlockType"] != "LINE":
                            continue

                        bb = box["Geometry"]["BoundingBox"]
                        bound = {
                            "left":bb["Left"] * out["shape"][1],
                            "top":bb["Top"] * out["shape"][0],
                            "width":bb["Width"] * out["shape"][1],
                            "height":bb["Height"] * out["shape"][0]
                        } 

                        lines.append([box["Text"], bound])
                    out["lines"] = lines
        return out