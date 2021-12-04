import pandas as pd
from containers.descriptor.reader import BaseReaderDescriptor
from containers.descriptor.cache import BaseCacheDescriptor
      
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
        #['blue', 'green', 'red', 'T1', 'T2', 'G1', 'G2', 'minSize', 'maxSize', 'minSizePl', 'minSizeSeg', 'maxSizeSeg', 'fillHoles', 'recon', 'water']
        rules = [(task[0], task[1], task[2], task[3], task[4],),\
                 (task[0], task[1], task[2], task[3], task[4], task[13],),\
                 (task[0], task[1], task[2], task[3], task[4], task[13], task[12], task[5],),\
                 (task[0], task[1], task[2], task[3], task[4], task[13], task[12], task[5], task[7], task[8],),\
                 (task[0], task[1], task[2], task[3], task[4], task[13], task[12], task[5], task[7], task[8], task[6],),\
                 (task[0], task[1], task[2], task[3], task[4], task[13], task[12], task[5], task[7], task[8], task[6], task[9], task[14],),\
                 (task[0], task[1], task[2], task[3], task[4], task[13], task[12], task[5], task[7], task[8], task[6], task[9], task[14], task[10], task[11],)]
        return rules