"""!
@PyMid is devoted to manage multitask algorithms and methods.

@authors Michel Pires da Silva (michelpires@dcc.ufmg.br)

@date 2014-2018

@copyright GNU Public License

@cond GNU_PUBLIC_LICENSE
    PyMid is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    
    PyMid is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    
    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
@endcond
"""

from core.managers.worker import BaseWorkerInfo
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors

import pandas as pd
import numpy as np
import time


class NETFLIX(BaseWorkerInfo):

    def __init__(self, train, isverbose=False, nrecommendations=10):
        self.__train  = None
        self.__matrix = None
        self.__knn    = None
        self.__nrec   = nrecommendations
        self.__preprocessing(train, isverbose)
    
    
    def __preprocessing(self, train, isverbose):
        print('[INFO]: Reading dataset reviews ...') if isverbose else None
        self.__train = pd.read_csv(train)
        
        #get pivoted matrix movies, users
        unique_movies = 17770
        unique_users  = self.__train['user_id'].unique().max()+1
        print('[INFO]: Detected ', unique_users, ' users and ', unique_movies, ' movies in dataset') if isverbose else None

        print('[INFO]: Generating factorization matrix ...') if isverbose else None
        matrix = np.zeros([unique_movies, unique_users])
        for data in self.__train.itertuples():
            matrix[data[2], data[1]] = data[3]
        self.__matrix = csr_matrix(matrix)
        
        print('[INFO]: Training Knn for recomendations ...') if isverbose else None    
        self.__knn = NearestNeighbors(metric='cosine', algorithm='brute', n_neighbors=10, n_jobs=-1)
        self.__knn.fit(self.__matrix)
        
    
    def __itemBasedCollaborativeFilter(self, task):
        movies = set()
        df = None 

        for movie in task:

            t1 = time.time()
            rule = self.cache.get(movie)
            self.times['cache'] = time.time() - t1 if 'cache' not in self.times else self.times['cache'] + (time.time() - t1)
            
            if rule == -1:
                distances , indices = self.__knn.kneighbors(self.__matrix[movie], n_neighbors=self.__nrec+1)    
                betters = list(zip(indices.squeeze().tolist(),distances.squeeze().tolist()))
                rec_movie_indices = set(sorted(betters, key=lambda x: x[1])[1:self.__nrec+1])
                movies |= rec_movie_indices
                t1 = time.time()
                self.cache.set(movie, rec_movie_indices)
                self.times['cache'] = (time.time() - t1) if 'cache' not in self.times else (self.times['cache'] + (time.time() - t1))
            else:
                movies |= rule
                
        movies = sorted(movies, key=lambda x: x[1])[0:self.__nrec]
        recommend_frame = []
        for val in movies:
            recommend_frame.append({'Title':self.__train[self.__train['movie'] == val[0]]['title'].unique(),'Distance':val[1]})
        df = pd.DataFrame(recommend_frame)
        return df

    
    def execute_task(self, task):
        task = csr_matrix(task)
        task = task[0,:].indices
        t1 = time.time()
        movies = self.__itemBasedCollaborativeFilter(task)
        self.times['function_get_rules'] = time.time() - t1 if 'function_get_rules' not in self.times else self.times['function_get_rules'] + (time.time() - t1)

        return movies