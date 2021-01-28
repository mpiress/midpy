import numpy as np
import pandas as pd
from containers.descriptor.reader import BaseReaderDescriptor
from containers.descriptor.cache import BaseCacheDescriptor

import time
      
class ReaderDescriptor(BaseReaderDescriptor):
    def __init__(self, path):
        super(ReaderDescriptor, self).__init__(path)
        self.__task_dimensionality = 17770
        self.__matrix = []
        self.load()

    def get_task_dimensionality(self):
        return self.__task_dimensionality

    def load(self):
        self.dataFrame = pd.read_csv(self.path)
        self.index     = list(self.dataFrame['user_id'].unique())

    def sizeof(self):
        return len(self.dataFrame['user_id'].unique())


    def readline(self):
        task = np.zeros(self.__task_dimensionality)
        idx = self.index.pop(0)
        movies = self.dataFrame[self.dataFrame.user_id == idx][['movie', 'rating']]
        for movie in movies.itertuples():
            task[movie[1]] = movie[2]
        return list(task)
    
    def clear_all(self):
        del(self.__matrix)
        del(self.dataFrame)

    def read_pair_of_tasks(self, idx1, idx2):
        if len(self.__matrix) == 0:
            unique_users  = len(self.dataFrame['user_id'].unique())
            self.__matrix = np.zeros([unique_users, self.__task_dimensionality])
            for data in self.dataFrame.itertuples():
                self.__matrix[data[1], data[2]] = data[3]
        return [self.__matrix[idx1], self.__matrix[idx2]]


class CacheDescriptor(BaseCacheDescriptor):
    def processing(self, task):
        rules = list(np.nonzero(task)[0])
        return rules


