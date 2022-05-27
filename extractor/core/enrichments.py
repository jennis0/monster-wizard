from base64 import b64decode
import configparser
import io
from matplotlib import pyplot as plt
import numpy as np
from scipy.spatial.distance import cdist
import logging
import configparser

from PIL import Image
from imagehash import dhash

from ..utils.datatypes import Bound

varr = []
varg = []
varb = []

class Enrichments(object):
    '''Applies a variety of algorithms to provide additional information to the parsed statblocks'''
    
    def __init__(self, config: configparser.ConfigParser, logger: logging.Logger):
        self.config = config
        self.logger = logger.getChild("imagepicker")

        self.minimum_width=0.1
        self.minimum_height=0.1
        self.minimum_area = 0.05
        self.maximum_overlap=0.75
        self.required_variance=100

    def filter_page_images(self, imgs, sbs):

        all_statblock_line_bounds = []
        totals = []
        for sb in sbs:
            all_statblock_line_bounds.append([[l["page"], Bound.deserialise(l["bound"])] for l in sb["section"]["lines"]])
            totals.append(sum(l[1].width * l[1].height for l in all_statblock_line_bounds[-1]))

        results = [True for img in imgs]
        for i,img in enumerate(imgs):
            for j, w_and_lbs in enumerate(zip(totals, all_statblock_line_bounds)):
                weight = w_and_lbs[0]
                line_bounds = w_and_lbs[1]
                overlap_area = 0
                for lb in line_bounds:
                    if lb[0] != img.page:
                        continue
                    overlap_area += Bound.overlap(img.bound, lb[1]) / weight

                self.logger.debug(f"Found overlap of {overlap_area} for image {img.id} and statblock {sbs[j]['name']}")

                if overlap_area > self.maximum_overlap:
                    self.logger.debug(f"Discarding image {img.id} due to overlap")
                    results[i] = False
                    break

        return results

    def filter_images(self, imgs):
        
        image_hashes = {}
        results = [True for img in imgs]

        for i,img in enumerate(imgs):
            ### Filter out images that are too small
            if img.bound.width < self.minimum_width or\
                 img.bound.height < self.minimum_height or\
                 (img.bound.width * img.bound.height < self.minimum_area) or (abs(1 - img.bound.width) < 0.05 and (abs(1-img.bound.height) < 0.05)):
                self.logger.debug(f"Discarding image {img.id} on page {img.page} due to dimensions ({img.bound.width},{img.bound.height})")
                results[i] = False
                continue

            ### Convert image back into a PIL image to do some basic processing
            img_data = b64decode(imgs[i].data)
            pil_img = Image.open(io.BytesIO(img_data))

            ### Do a 'difference-hash' of the images to filter out duplicates (likely to be watermarks)
            hash = dhash(pil_img)
            if hash in image_hashes:
                results[i] = False
                results[image_hashes[hash]] = False
                continue
            else:
                image_hashes[hash] = i

            ### Filter out images that are very low variance - typically backgrounds
            img_array = np.asarray(pil_img)

            var_x = np.max([img_array[:,:,i].var(axis=0).max() for i in range(3)])
            var_v_x = np.mean( [img_array[:,:,i].var(axis=0).var() for i in range(3)])
            var_v_y = np.mean([img_array[:,:,i].var(axis=1).var() for i in range(3)])
            
            if var_v_y > 0:
                var_var_ratio = var_v_x/ var_v_y
            else:
                var_var_ratio = 0
            if var_x > 10000 and var_var_ratio > 0.3 and var_var_ratio < 3 or \
                var_x > 2000 and var_var_ratio > 0.3 and var_var_ratio < 1.7:
                continue
            else:
                self.logger.debug(f"Discarding image {img.id} on page {img.page} due to lack of variance ({var_x}, {var_v_x}, {var_v_y}, {var_var_ratio})")
                results[i] = False
                
        return [img for i,img in enumerate(imgs) if results[i]]

    def filter_and_associate_images(self, source):

        images = {}
        sbs = {}
        ###Build SB and image page maps
        for img in self.filter_images(source.images):
            if img.page in images:
                images[img.page].append(img)
            else:
                images[img.page] = [img]
        
        for sb in source.statblocks:
            page = sb["source"]["page"]
            if sb["source"]["page"] in sbs:
                sbs[page].append(sb)
            else:
                sbs[page] = [sb]
            
        used_images = set()
        for page in sbs:
            page_sbs = np.array([np.array(Bound.deserialise(s["section"]["bound"]).center()) for s in sbs[page]])
            page_img= np.array([np.array(i.bound.center()) for i in images[page]] if page in images else [])

            if page_img.shape[0] > 0 and page_sbs.shape[0] > 0:
                distances = cdist(page_sbs, page_img)
                
                for i in range(min(len(page_sbs), len(page_img))):
                    closest = np.unravel_index(np.argmin(distances, axis=None), distances.shape)

                    img_id = images[page][closest[1]].id
                    sbs[page][closest[0]]["image"] = {"ref":img_id}
                    used_images.add(img_id)
                    self.logger.debug(f'Linked img {img_id} to statblock {sbs[page][closest[0]]["name"]}')

                    distances[closest[0],:] = 1000
                    distances[:,closest[1]] = 1000

        for page in sbs:
            if page % 2 == 0:
                ### Look at the right hand page
                offset = 1
            else:
                ### Look at left hand page
                offset = -1

            ### Traverse unused images on next/previous page and match to closest
            if page+offset in images:
                unset_statblocks = [sb for sb in sbs[page] if "image" not in sb]
                unused_images = [img for img in images[page+offset] if img.id not in used_images]
                page_sbs = np.array([np.array(Bound.deserialise(s["section"]["bound"]).center()) for s in unset_statblocks])
                page_img = np.array([np.array(i.bound.center()) for i in unused_images])

                if page_img.shape[0] > 0 and page_sbs.shape[0] > 0:
                    distances = cdist(page_sbs, page_img + [offset,0])
                    
                for i in range(min(len(page_sbs), len(page_img))):
                    closest = np.unravel_index(np.argmin(distances, axis=None), distances.shape)

                    img_id = unused_images[closest[1]].id
                    unset_statblocks[closest[0]]["image"] = {"ref":img_id}
                    used_images.add(img_id)
                    self.logger.debug(f'Linked img {img_id} to statblock {unset_statblocks[closest[0]]["name"]}')

                    distances[closest[0],:] = 1000
                    distances[:,closest[1]] = 1000

        ### Do the same thing but in reverse to pick-up things going unexpectedly
        for page in sbs:
            if page % 2 == 0:
                offset = -1
            else:
                offset = 1

            ### Traverse unused images on next/previous page and match to closest
            if page+offset in images:
                unset_statblocks = [sb for sb in sbs[page] if "image" not in sb]
                unused_images = [img for img in images[page+offset] if img.id not in used_images]
                page_sbs = np.array([np.array(Bound.deserialise(s["section"]["bound"]).center()) for s in unset_statblocks])
                page_img = np.array([np.array(i.bound.center()) for i in unused_images])

                if page_img.shape[0] > 0 and page_sbs.shape[0] > 0:
                    distances = cdist(page_sbs, page_img + [offset,0])
                    
                for i in range(min(len(page_sbs), len(page_img))):
                    closest = np.unravel_index(np.argmin(distances, axis=None), distances.shape)

                    img_id = unused_images[closest[1]].id
                    unset_statblocks[closest[0]]["image"] = {"ref":img_id}
                    self.logger.debug(f'Linked img {img_id} to statblock {unset_statblocks[closest[0]]["name"]}')

                    distances[closest[0],:] = 1000
                    distances[:,closest[1]] = 1000


        ### Store only the images we've chosen to keep
        last_page = max(sbs.keys()) if len(sbs) > 0 else 0
        source.images = []
        for page in images:
            ### Skil pages more than one page past the last detected statblock
            if page > last_page + 1:
                continue
            source.images += images[page]      
          

    def filter_and_associate_backgrounds(self, source):
        pass

