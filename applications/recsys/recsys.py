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
from utils import read_file

import time
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

class config:
    USERCUISINE = 'fusercuisine.csv'
    REST        = 'geoplaces.csv'
    RESTCUISINE = 'fchefmozcuisine.csv'
    RATING      = 'rating_final.csv'
    
    
class RECSYS(BaseWorkerInfo):
    
    def __init__(self, train, basepath, nrecommendations=10):
        super(RECSYS, self).__init__()
        self.__usertrain     = None
        self.__usercuisine   = None
        self.__rest          = None
        self.__restcuisine   = None
        self.__rating        = None
        self.__k             = nrecommendations
        self.__basepath      = basepath
        self.__preprocessing(train)
    
    def __preprocessing(self, train):
        self.__usertrain      = read_file(train, has_header=True, norm=True)
        self.__usercuisine    = read_file(self.__basepath+config.USERCUISINE, has_header=True, norm=True)
        self.__rest           = read_file(self.__basepath+config.REST, has_header=True, cols=['placeID', 'name', 'Rambience'], norm=True)
        self.__restcuisine    = read_file(self.__basepath+config.RESTCUISINE, has_header=True, norm=True)
        self.__rating         = read_file(self.__basepath+config.RATING, has_header=True, norm=True)
        self.__rating['rating'] = self.__rating.apply(lambda row: row.rating + row.food_rating + row.service_rating, axis=1)
        self.__rating = self.__rating.drop(['food_rating', 'service_rating'], axis=1)
        

    def __compute_cross_distances(self, userset, task):
        data_matrix = userset.values[:, 1:]
        cosine = cosine_similarity(data_matrix, [task[1:]])
        return dict(zip(userset.userID, cosine[:, 0]))
        
    
    def __collaborative_filter(self, userset, task): 
           
        cosine = self.__compute_cross_distances(userset, task)
        
        rating = self.__rating[self.__rating.userID.isin(userset.userID)]   
        
        places = {}
        for line in rating.itertuples():
            places[line[2]] = line[3] * cosine[line[1]] if line[2] not in places else places[line[2]] + line[3] * cosine[line[1]]
            
        places = list(map(lambda x: x[0], sorted(places.items(), key=lambda x:x[1], reverse=True)))
        return places[0:self.__k]
        
    
    def __predict(self, dataset, task):
        hits = nrules = 0
        query = task
        
        t1 = time.time()
        key = tuple(query[1:])
        rule = self.cache.get(key)
        self.times['cache'] = time.time() - t1 if 'cache' not in self.times else self.times['cache'] + (time.time() - t1)
        
        if isinstance(rule, int):
            t1 = time.time()
            nrules += 1
            u_cuisine = self.__usercuisine[self.__usercuisine.userID == query[0]]
            userIDs   = self.__usercuisine[self.__usercuisine.Rcuisine.isin(u_cuisine.Rcuisine)].userID.unique()
            if len(userIDs) >  0:
                userset  = dataset[dataset.userID.isin(userIDs)]
                if len(userset) == 0:
                    cosine = self.__compute_cross_distances(dataset, query)
                    userIDs = list(map(lambda x: x[0], sorted(cosine.items(), key=lambda x: x[1], reverse=True)))[0:self.__k]
                    userset  = dataset[dataset.userID.isin(userIDs)]
            else:
                cosine = self.__compute_cross_distances(dataset, query)
                userIDs = list(map(lambda x: x[0], sorted(cosine.items(), key=lambda x: x[1], reverse=True)))[0:self.__k]
                userset  = dataset[dataset.userID.isin(userIDs)]
            
            places = self.__collaborative_filter(userset, query)
            
            rule = places
            self.times['generate_rules'] = (time.time() - t1) if 'generate_rules' not in self.times else self.times['generate_rules'] + (time.time() - t1)    
            
            t1 = time.time()
            key = tuple(query[1:])
            self.cache.set(key, rule)
            self.times['cache'] = time.time() - t1 if 'cache' not in self.times else self.times['cache'] + (time.time() - t1)
        
        else:
            hits += 1
        
        return [hits, nrules]
        
        
    def execute_task(self, task):
        task = list(task)
        size = len(task)
        places = [0,0]
        m = 4
        header = list(self.__usertrain)
        r = list(range(1, size, m))
        r.append(size)
        j = r[0]
        for i in r[1:]:
            h = header[0:1] + header[j:i]
            dataset =  pd.DataFrame(np.concatenate((self.__usertrain.values[:,0:1], self.__usertrain.values[:,j:i]), axis=1), columns=h)
            t = task[0:1] + task[j:i]
            tmp = self.__predict(dataset, t)
            places[0] += tmp[0]
            places[1] += tmp[1]
            j = i
        self.info_cache['hits'] += places[0]
        self.info_cache['missing'] += places[1]
        
        return places    
