
class StatblockBuilder(object):

    def can_be_continuation(self, current_tags, new_tags):
        if len(current_tags) == 0:
            return False

        if len(new_tags) == 0:
            return False

        tag_index_mapping = {
            "sb_start":0,
            "sb_defence_block":1,
            "sb_array_block":2,
            "sb_flavour_block":3,
            "sb_action_block":4,
            "sb_legendary_action_block":5,
            "sb_part":5,
            "sb_part_weak":5
        }

        last_tag = max(tag_index_mapping[t] if "sb_part" not in t else 0 for t in current_tags)
        next_tag = min(tag_index_mapping[t] for t in new_tags)

        return next_tag >= last_tag

    def get_bounding_box(self, statblock, wh=False, flat=False):
        box = {
            "left":100000,
            "top":100000,
            "right":0,
            "bottom":0
        }

        for cluster in statblock:
            if flat:
                if cluster[1]["left"] < box["left"]:
                    box["left"] = cluster[1]["left"]
                if cluster[1]["top"] < box["top"]:
                    box["top"] = cluster[1]["top"]
                if cluster[1]["left"] + cluster[1]["width"] > box["right"]:
                    box["right"] = cluster[1]["left"] + cluster[1]["width"]
                if cluster[1]["top"] + cluster[1]["height"] > box["bottom"]:
                    box["bottom"] = cluster[1]["top"] + cluster[1]["height"]
            else:
                for line in cluster:
                    if line[1]["left"] < box["left"]:
                        box["left"] = line[1]["left"]
                    if line[1]["top"] < box["top"]:
                        box["top"] = line[1]["top"]
                    if line[1]["left"] + line[1]["width"] > box["right"]:
                        box["right"] = line[1]["left"] + line[1]["width"]
                    if line[1]["top"] + line[1]["height"] > box["bottom"]:
                        box["bottom"] = line[1]["top"] + line[1]["height"]

        if not wh:
            return box
        else:
            box["width"] = box["right"] - box["left"]
            box["height"] = box["bottom"] - box["top"]
            del box["bottom"]
            del box["right"]
            return box

    def merge_statblocks(self, statblocks):
        boxes = [self.get_bounding_box(s[0]) for s in statblocks]

        merges = []
        used = []
        for i in range(len(statblocks)):
            s = statblocks[i]
            b = boxes[i]

            if "sb_start" not in s[1]:
                for j in range(len(statblocks)):
                    if i == j:
                        continue

                    if b["left"] - boxes[j]["left"] < 100:
                        continue
                    if not self.can_be_continuation(statblocks[j][1], s[1]):
                        continue
                    if abs(b["top"] - boxes[j]["top"]) < 100:
                        start_index = 0
                        for line in statblocks[i][0][0]:
                            if line[1]["top"] < statblocks[j][0][0][0][1]["top"] - 20:
                                start_index += 1
                            else:
                                break

                        statblocks[i][0][0] = statblocks[i][0][0][start_index:]

                        lines = statblocks[j][0] + statblocks[i][0]
                        parts = statblocks[j][1] + statblocks[i][1]
                        merges.append((lines, parts))
                        used += [j, i]
                        break

        for i in range(len(statblocks)):
            if i not in used:
                merges.append(statblocks[i])

        merges.sort(key = lambda x: x[0][0][0][1]["top"])
        return merges
        

    def flatten_statblock(self, s):
        lines = []
        for cluster in s:
            lines += cluster
        return lines

    def filter_statblocks(self, sbs):
        filtered_sb = []
        for sb in sbs:
            start_index = -1
            # Look for statblock title and remove statblocks without one
            for i,line in enumerate(sb):
                if "statblock_title" in line[2]:
                    start_index = i
                    break
            if start_index < 0:
                continue
            else:
                filtered_sb.append(
                    sb[start_index:]
                )
        return filtered_sb


    def create_statblocks(self, cols):
        statblock_parts = []
        for col in cols:
            current_statblock = []
            current_statblock_parts = []
            for cluster in col:
                sb_parts = [a for a in cluster[2] if isinstance(a, str) and a.startswith("sb_")]
                if len(sb_parts) == 0:
                    if len(current_statblock) > 0:
                        statblock_parts.append((current_statblock, current_statblock_parts))
                    current_statblock = []
                    current_statblock_parts = []
                    continue

                if self.can_be_continuation(current_statblock_parts, sb_parts):
                    current_statblock.append(cluster[0])
                    current_statblock_parts += sb_parts
                else:
                    if len(current_statblock) > 0:
                        statblock_parts.append((current_statblock, current_statblock_parts))
                    current_statblock = [cluster[0]]
                    current_statblock_parts = sb_parts                    

            if len(current_statblock) > 0:
                statblock_parts.append((current_statblock, current_statblock_parts))

        merged_statblocks = self.merge_statblocks(statblock_parts)
        flat_statblocks = [self.flatten_statblock(s[0]) for s in merged_statblocks]
        filtered_statblocks = self.filter_statblocks(flat_statblocks)
        return [[sb, self.get_bounding_box(sb, wh=True, flat=True)] for sb in filtered_statblocks]
        


