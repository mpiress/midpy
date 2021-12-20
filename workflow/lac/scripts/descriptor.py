import pandas as pd
from containers.descriptor.reader import BaseReaderDescriptor
from containers.descriptor.cache import BaseCacheDescriptor
from ctypes import * 

class ReaderDescriptor(BaseReaderDescriptor):
    def __init__(self):
        super(ReaderDescriptor, self).__init__()
        self.dataFrame = None
        self.nns       = None
        self.index     = None
        self.task_dim  = 0
        
    def get_task_dimensionality(self):
        return self.task_dim

    def load(self):
        self.dataFrame = pd.read_csv(self.path, header=None, dtype='float_')
        #self.dataFrame = pd.read_csv(self.path, header=None, dtype='string')
        self.index     = self.dataFrame.index.tolist()
        self.task_dim  = self.dataFrame.shape[1]
        
    def sizeof(self):
        return self.dataFrame.shape[0]


    def readline(self):
        idx = self.index.pop(0)
        params = self.dataFrame[self.dataFrame.index == idx].values.tolist()[0]
        params = [round(x, 4) for x in params]
        return params
    
    def clear_all(self):
        del(self.dataFrame)
        del(self.index)

    def read_pair_of_tasks(self, idx1, idx2):
        params1 = self.dataFrame[self.dataFrame.index == idx1].values.tolist()[0]
        params2 = self.dataFrame[self.dataFrame.index == idx2].values.tolist()[0]
        params1 = [round(x, 4) for x in params1]
        params2 = [round(x, 4) for x in params2]
        return [params1, params2]


class CacheDescriptor(BaseCacheDescriptor):
    
    def processing(self, task):
        rules = list(enumerate(task[0:-1]))
        return rules