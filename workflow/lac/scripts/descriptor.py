import pandas as pd
from containers.descriptor.reader import BaseReaderDescriptor
from containers.descriptor.cache import BaseCacheDescriptor
from itertools import combinations

class ReaderDescriptor(BaseReaderDescriptor):
    def __init__(self, path):
        super(ReaderDescriptor, self).__init__(path)
        self.dataFrame = None
        self.index     = None
        self.task_dim  = 0

    def get_task_dimensionality(self):
        return self.task_dim

    def load(self):
        self.dataFrame = pd.read_csv(self.path, header=None)
        self.index     = self.dataFrame.index.tolist()
        self.task_dim  = self.dataFrame.shape[1]
        
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
        rules = list(enumerate(task[0:-1]))
        return rules