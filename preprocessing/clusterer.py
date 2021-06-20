import numpy as np

class HierarchicalCluster(object):

    def __init__(self, levels=3, fuzzyness=1, min_gap=0, max_gap=100):
        self.levels = levels
        self.fuzzyness = fuzzyness
        self.min_gap = min_gap
        self.max_gap = max_gap

    def _estimate_distances_and_gap(self, boxes):
        gaps = [boxes[i+1]["top"] - (boxes[i]["top"] + boxes[i]["height"]) for i in range(len(boxes) - 1)]
        gaps = np.array(gaps)
        bins = np.arange(0, 500, 10)
        counts, edges = np.histogram(gaps, bins=bins)
        lg = edges[counts.argmax() + 1]
        return gaps, lg

    def merge_lines(self, lines):
        lefts = []
        tops = []
        bottoms = []
        rights = []

        for l in lines:
            lefts.append(l[1]["left"])
            tops.append(l[1]["top"])
            bottoms.append(l[1]["top"] + l[1]["height"])
            rights.append(l[1]["left"] + l[1]["width"])

        new_box = {
            "left":min(lefts),
            "top":min(tops),
        }

        new_box["width"] = max(rights) - new_box["left"]
        new_box["height"] = max(bottoms) - new_box["top"]

        if isinstance(lines[0][0], str):
            return [lines, new_box]
        else:
            new_lines = []
            for l in lines:
                new_lines += l[0]
            return [new_lines, new_box]

    def cluster(self, lines):
        cluster_levels = [lines]
        for level in range(self.levels + 1):
            clusters = []
            input = cluster_levels[-1]
            if len(input) == 0:
                continue

            gaps, threshold = self._estimate_distances_and_gap([l[1] for l in input])
            threshold = min(max(self.min_gap, threshold * self.fuzzyness), self.max_gap)
            current_cluster = [input[0]]
            for l,g in zip(input[1:], gaps):
                t = l
                for _ in range(int(level)):
                    t = l[0][0]
                if g < -100 or g > threshold or "statblock_start" in t[2]:
                    clusters.append(current_cluster)
                    current_cluster = [l]
                else:
                    current_cluster.append(l)
            clusters.append(current_cluster)

            merged_clusters = [self.merge_lines(c) for c in clusters]
            cluster_levels.append(merged_clusters)

        new_clusters = []
        cluster_index = 0
        current_cluster = cluster_levels[-1][cluster_index]

        while cluster_index < len(cluster_levels[-1]):
            split = 0
            for i,line in enumerate(current_cluster[0][1:]):
                if "statblock_title" in line[2]:
                    split = i + 1
                    break
            if split > 0:
                new_clusters.append(self.merge_lines(current_cluster[0][:split]))
                current_cluster = self.merge_lines(current_cluster[0][split:])
                continue
            else:
                new_clusters.append(current_cluster)
                cluster_index += 1
                if cluster_index >= len(cluster_levels[-1]):
                    break
                current_cluster = cluster_levels[-1][cluster_index]

        return new_clusters
