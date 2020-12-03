import numpy as np
import pandas as pd
from containers.descriptor.reader import BaseReaderDescriptor
from containers.descriptor.cache import BaseCacheDescriptor

import time
      
class ReaderDescriptor(BaseReaderDescriptor):
    def __init__(self, path):
        super(ReaderDescriptor, self).__init__(path)
        self.__task_dimensionality = 6
        self.dataFrame = None
        self.index     = None
        self.load()

    def get_task_dimensionality(self):
        return self.__task_dimensionality

    def load(self):
        self.dataFrame = pd.read_csv(self.path, header=None)
        self.index     = self.dataFrame.index.tolist()
        
    def sizeof(self):
        return self.dataFrame.shape[0]


    def readline(self):
        idx = self.index.pop(0)
        params = self.dataFrame[self.dataFrame.index == idx].values.tolist()[0]
        return params
    
    def clear_all(self):
        del(self.dataFrame)
        del(self.index)

    def read_pair_of_tasks(self, idx1, idx2):
        params1 = self.dataFrame[self.dataFrame.index == idx1].values.tolist()[0]
        params2 = self.dataFrame[self.dataFrame.index == idx2].values.tolist()[0]
        return [params1, params2]


class CacheDescriptor(BaseCacheDescriptor):
    def processing(self, task):
        rules = [[task[0]]]
        for t in task[1:]:
            rules.append(rules[-1] + [t])
        del(rules[0])
        return rules