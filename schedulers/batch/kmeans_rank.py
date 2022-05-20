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

from sklearn import neighbors
warnings.warn = warn

from schedulers.base_scheduler import SchedulerManager
from schedulers.batch.neighbourhood_rank import NeighborhoodRank
from containers.wrapper.wrappers  import NetworkWrapper, WorkloadWrrapper, SchedulerWrapper

from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler
from igraph import Graph

import time, math
import pandas as pd
import numpy as np



class KMeansRank(SchedulerManager):
    '''
    @brief Round Robin Scheduler Policy
    '''

    def __init__(self, conn:NetworkWrapper, workload:WorkloadWrrapper, schell:SchedulerWrapper, tasks, descriptor, warmup, isverbose=True):
        
        """!
        @brief Constructor of KMeans scheduler.
        @details Initializer is used for creating the Round Robin scheduler manager.
        
        @param[in] conn: networking wrapper used to create a proxy to data access
        @param[in] workload: workload information used to define patterns for queries processing   
        @param[in] isverbose: flag to indicate the terminal information printed during the execution process  
                
        @see base_scheduler
        """
        super(KMeansRank, self).__init__(conn, workload, schell, tasks, descriptor, warmup, isverbose)
        self.__neighbors = NeighborhoodRank(conn, workload, schell, tasks, descriptor, warmup, isverbose)
        
        if self.isverbose:
            print('[INFO]: executing KMeans scheduler to manage tasks')
        
    
    def __evaluated_model_KR(self, dataset, inputset):
        tmp = []
        
        for _, query in dataset:
            tmp.append([item[1] if isinstance(item, tuple) else item for item in query])
        df = pd.DataFrame(tmp)
        
        nclusters = self.conn.nworkers
        kmeans = KMeans(n_clusters=nclusters, random_state=42).fit(df.values).labels_
        for q, k in zip(dataset, kmeans):
            if k not in inputset:
                inputset[k] = [(q[0], q[1])]
            else:
                inputset[k].append((q[0], q[1]))
            
                
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
        
        print('[INFO]: assign', str(self.sizeof),'tasks for ',str(self.conn.nworkers),' worker(s)') if self.isverbose else None
        
        workload = 0
        schell = 0
        
        t1 = time.time()
        self.warmup_cache()
        self.metrics['schell_warmup_cache'] = time.time() - t1  


        t1 = time.time()
        while workload < self.sizeof:
            inputset = {}
            
            chunk = self.get_chunk()
            workload += len(chunk)
            self.__evaluated_model_KR(chunk, inputset)
            
            data = []
            for w in inputset:
                tasks = []
                self.__neighbors.evaluated_model(inputset[w], tasks)
                data += list(map(lambda x: [x[0], x[1]], sorted(tasks, key=lambda x: x[2], reverse=True)))
            
            self.assign_tasks(data, self.workload.mod_or_div) 
            
        self.set_exit()
        self.metrics['schell_runtime'] = time.time() - t1

        print('[INFO]: time expended for scheduling the tasks: ', self.metrics['schell_runtime']) if self.isverbose else None
    
    
    
    
