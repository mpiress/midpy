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
from schedulers.base_scheduler import SchedulerManager
from containers.wrapper.wrappers import NetworkWrapper, WorkloadWrrapper
from threading import Thread
from scipy.stats import poisson, norm
from itertools import combinations, permutations


from igraph import Graph
import numpy as np
import time, math, random

class NeighborhoodRank(SchedulerManager):

    def __init__(self, conn:NetworkWrapper, workload:WorkloadWrrapper, tasks, descriptor, warmup_cache=0, isverbose=True):
        """!
        @brief Constructor of feature rank scheduler.
        @details Initializer is used for creating the Feature Rank scheduler manager based stratege presented on SBAC paper
        
        @param[in] conn: networking wrapper used to create a proxy to data access
        @param[in] workload: workload information used to define patterns for queries processing   
        @param[in] isverbose: flag to indicate the terminal information printed during the execution process  
                
        @see base_scheduler
        """
        
        super(NeighborhoodRank, self).__init__(conn, workload, tasks, descriptor, warmup_cache, isverbose)
        
        if self.isverbose:
            print('[INFO]: executing neighborhood rank for task scheduling')
        
        random.seed(42)
        
        self.__times = {'Graph':0, 'PageRank':0, 'Eval':0}
    
    
    def __evaluated_model(self, dataset, inputset):
        edges = []
        codec = {}
        code = 0
        
        t1 = time.time()
        for query in dataset:
            query = list(enumerate(query[1]))
            tmp   = []
            for v in query:
                if v not in codec:
                    codec[v] = code
                    code += 1
            edges += [(codec[query[i]], codec[query[i+1]]) for i in range(len(query)-1)] + [(codec[query[-1]], codec[query[0]])]
        self.__times['Graph'] += time.time() - t1
        
        t1 = time.time()
        G = Graph(edges)
        attr_count = dict(enumerate(G.pagerank()))
        self.__times['PageRank'] += time.time() - t1
        
        t1 = time.time()
        for index, query in dataset:
            tmp = 0
            q = [codec[v] for v in enumerate(query)]
            #q = list(enumerate(query))
            edges = permutations(q, 2)
            #edges = [(codec[q[i]], codec[q[i+1]]) for i in range(len(q)-1)] + [(codec[q[-1]], codec[q[0]])]
            for e1, e2 in edges:
                tmp += (attr_count[e1] + attr_count[e2])#/min(attr_count[codec[e1]], attr_count[codec[e2]]) 
            inputset.append((index, query, tmp))
        self.__times['Eval'] += time.time() - t1
        
    
    def __distribution(self, div=True):
        workload = 0
        wid = 0
        
        t1 = time.time()
        workload += self.warmup_cache()
        self.metrics['schell_warmup_cache'] = time.time() - t1    
        
        t1 = time.time()
        while workload < self.sizeof:
            chunk = self.get_chunk()
            inputset = []
            sizeof = min(self.workload.overview['chunk'], self.sizeof - workload)
            workload += len(chunk)
            
            self.__evaluated_model(chunk, inputset)
            data = list(map(lambda x: [x[0], x[1]], sorted(inputset, key=lambda x: x[2], reverse=True)))
            self.assign_tasks(data, div)
        
        self.set_exit()
        self.metrics['schell_runtime'] = time.time() - t1
        
        
    def predict(self):
        """!
        @brief Method used to process queries according to RoundRobin scheduler policy
        @details In this method, queries are performed based on neighboor relevance attributes by query 
        
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
        self.__distribution(self.workload.mod_or_div)
        print('[INFO]: time expended for scheduling the tasks: ', self.metrics['schell_runtime']) if self.isverbose else None
                
        
        
        
