import numpy as np
from typing import List, Tuple
from configparser import ConfigParser
from logging import Logger

from utils.datatypes import Line, Section

class Clusterer(object):

    def __init__(self, config: ConfigParser, logger: Logger):
        
        self.fuzzyness = config.getfloat("clusterer", "fuzzyness", fallback=3.0)
        self.min_gap = config.getfloat("clusterer", "min_gap", fallback=0.)
        self.max_gap = config.getfloat("clusterer", "max_gap", fallback=1.)

        self.logger = logger.getChild("clusterer")

        self.logger.debug("Configured Clusterer with config:")
        self.logger.debug("\tFuzzyness={}".format(self.fuzzyness))
        self.logger.debug("\tMin Gap={}".format(self.min_gap))
        self.logger.debug("\tMax Gap={}".format(self.max_gap))


    def _estimate_distances_and_gap(self, lines: List[Line]) -> Tuple[List[float], float]:
        '''Calculate the distances between each element in the cluster and returns a sensible cutoff'''

        gaps = [lines[i+1].bound.top - (lines[i].bound.bottom()) for i in range(len(lines) - 1)]
        gaps = np.array(gaps)
        bins = np.arange(0, .1, 0.005)
        counts, edges = np.histogram(gaps, bins=bins)
        lg = edges[counts.argmax() + 1]
        self.logger.debug("Found reasonable threshold of {}%".format(lg))
        return gaps, lg


    def cluster(self, lines: List[Line]) -> List[Section]:
        '''Cluster the passed lines into sections by finding lines with large gaps between them'''

        clusters = []

        gaps, threshold = self._estimate_distances_and_gap(lines)
        threshold = min(max(self.min_gap, threshold * self.fuzzyness), self.max_gap)
        self.logger.debug("Using clustering threshold of {}".format(threshold))

        current_cluster = Section([lines[0]], [])
        for line,gap in zip(lines[1:], gaps):
            #Gap is large so start a new cluster
            if gap < -0.1 or gap > threshold or "statblock_title" in line.attributes:
                clusters.append(current_cluster)
                current_cluster = Section([line], [])
            else:
                current_cluster.add_line(line)

        clusters.append(current_cluster)

        return clusters
