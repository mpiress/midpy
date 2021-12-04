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
def warn(*args, **kwargs):
    pass
import warnings
warnings.warn = warn

from schedulers.base_scheduler import SchedulerManager
from containers.wrapper.wrappers  import NetworkWrapper, WorkloadWrrapper

from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler
from igraph import Graph

import time, math
import pandas as pd
import numpy as np
import networkx as nx



class KMeansRank(SchedulerManager):
    '''
    @brief Round Robin Scheduler Policy
    '''

    def __init__(self, conn:NetworkWrapper, workload:WorkloadWrrapper, tasks, descriptor, isverbose=True):
        
        """!
        @brief Constructor of KMeans scheduler.
        @details Initializer is used for creating the Round Robin scheduler manager.
        
        @param[in] conn: networking wrapper used to create a proxy to data access
        @param[in] workload: workload information used to define patterns for queries processing   
        @param[in] isverbose: flag to indicate the terminal information printed during the execution process  
                
        @see base_scheduler
        """
        super(KMeansRank, self).__init__(conn, workload, tasks, descriptor, isverbose)
        
        if self.isverbose:
            print('[INFO]: executing KMeans scheduler to manage tasks')
        
    
    def __evaluated_by_NR(self, dataset, inputset):
        data = []
        edges = []
        codec = {}
        code = 0
        for query in dataset:
            query = list(enumerate(query[1]))
            for v in query:
                if v not in codec:
                    codec[v] = code
                    code += 1
            edges += [(codec[query[i]], codec[query[i+1]]) for i in range(len(query)-1)] + [(codec[query[-1]], codec[query[0]])]
        
        G = Graph(edges)
        attr_count = dict(enumerate(G.pagerank()))
        
        for index, query in dataset:
            tmp = 0
            q = list(enumerate(query))
            edges = [(q[i], q[i+1]) for i in range(len(q)-1)] + [(q[-1], q[0])]
            for e1,e2 in edges:
                tmp += (attr_count[codec[e1]] + attr_count[codec[e2]])/min(attr_count[codec[e1]], attr_count[codec[e2]]) 
            data.append((index, query, tmp))
        
        inputset += list(map(lambda x: [x[0],x[1]], sorted(data, key=lambda x:(x[2],x[1]), reverse=True)))

    
    def __evaluated_model_FR(self, dataset, inputset):
        attr_count = {}
        
        for index, query in dataset:
            for item in query:
                attr_count[item] = 1 if item not in attr_count else attr_count[item] + 1
             
        tmp = []
        for index, query in dataset:
            tmp.append((index, query, sum([attr_count[k] for k in query])))
        
        inputset += list(map(lambda x: [x[0], x[1]], sorted(tmp, key=lambda x:(x[2],x[1]), reverse=True)))
            
    #estimate based in elbow curve 
    def __elbow_method(self, inertia):
        m = np.mean(inertia)
        k =[(index+1, math.pow((point - m), 2)) for index, point in enumerate(inertia)]
        k = sorted(k, key=lambda x:x[1])
        return k[0][0]
        
    def __estimante_nclusters(self, dataset):
        inertia = []
        mmx = MinMaxScaler()
        K = range(1, min(10, len(dataset)))
        mmx.fit(dataset)
        df = mmx.transform(dataset)
        
        for k in K:
            kmeans = KMeans(n_clusters=k, precompute_distances=True, random_state=42).fit(df)
            inertia.append(kmeans.inertia_)
        
        k = self.__elbow_method(inertia)
        
        return k
            
    
    def __evaluated_model_KR(self, dataset, inputset):
        tmp = []
        
        for _, query in dataset:
            tmp.append([item[1] if isinstance(item, tuple) else item for item in query])
        df = pd.DataFrame(tmp)
        
        nclusters = self.__estimante_nclusters(df)
        kmeans = KMeans(n_clusters=nclusters, random_state=42).fit(df.values).labels_
        for q, k in zip(dataset, kmeans):
            if k not in inputset:
                inputset[k] = [(q[0], q[1])]
            else:
                inputset[k].append((q[0], q[1]))
            
                
    def __add_time(self, data, t1, t2):
        for idx, _ in data:
            self.waiting['dispatch'][idx] = t2 - t1
            
    
    def predict(self):
        """!
        @brief Method used to process queries according to KMeans scheduler policy
        @details In this method, queries are performed in the natural order that they are produced
        
        @code
            @input: [
                        (idx, [f1, f2, ..., fn]),
                        ... ...  ...            ,
                        (idx, [f1, f2, ..., fn])
                    ]
        @endcode
        
        @return (matrix) of queries indexed by the worker type id
            @output:[
                        (worker_id, query_id),
                        ... ...  ...         ,
                        (worker_id, query_id)
                    ]
        """
        
        workload = 0
        schell = 0
        
        self.get_all_tasks()
        
        while workload < self.sizeof:
            inputset = {}
            
            chunk = self.get_chunk()
            workload += len(chunk)
            self.__evaluated_model_KR(chunk, inputset)
            
            data = []
            for k in inputset:
                self.__evaluated_model_FR(inputset[k], data)
                #self.__evaluate_by_NR(inputset[k], data)
            
            t1 = time.time()
            self.assign_tasks(data, self.workload.dist_in_div)
            t2 = time.time()
            
            schell += t2 - t1
            
            self.__add_time(data, t1, t2)
        
        del(inputset)
        del(data)
        
        self.set_exit()
        
        print('[INFO]: time expended for scheduling the tasks: ', schell) if self.isverbose else None
        
        return schell, self.waiting
    
    
    
    
