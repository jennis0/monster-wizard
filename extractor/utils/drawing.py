from ..utils.datatypes import Section, Line
from typing import Union, List

import matplotlib.pyplot as plt
import cv2

def drawBoundingBoxes(imageData, boxes: Union[List[Section], List[Line]], color = (0, 120, 0, 120)):
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
        #rint(res)
        #res = Line("", "", res, [])
        imgHeight, imgWidth, _ = imageData.shape

        left = int(res.bound.left * imgWidth)
        top = int(res.bound.top * imgHeight) 
        right = int(res.bound.right() * imgWidth)
        bottom = int(res.bound.bottom() * imgHeight)
        
        thick = int((imgHeight + imgWidth) // 900)
        cv2.rectangle(imageData,(left, top), (right, bottom), c, thick)

    plt.figure(figsize=(20, 20))
    RGB_img = cv2.cvtColor(imageData, cv2.COLOR_BGR2RGB)
    plt.imshow(RGB_img, )