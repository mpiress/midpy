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
from containers.wrapper.wrappers  import NetworkWrapper, WorkloadWrrapper

import time

class FeatureRank(SchedulerManager):

    def __init__(self, conn:NetworkWrapper, workload:WorkloadWrrapper, tasks, descriptor, isverbose=True):
        """!
        @brief Constructor of feature rank scheduler.
        @details Initializer is used for creating the Feature Rank scheduler manager based stratege presented on SBAC paper
        
        @param[in] conn: networking wrapper used to create a proxy to data access
        @param[in] workload: workload information used to define patterns for queries processing   
        @param[in] isverbose: flag to indicate the terminal information printed during the execution process  
                
        @see base_scheduler
        """
        
        super(FeatureRank, self).__init__(conn, workload, tasks, descriptor, isverbose)
        
        if self.isverbose:
            print('[INFO]: executing feature ranking to task scheduling')
        

    def __evaluated_model(self, dataset, inputset):
        attr_count = {}
        
        for index, query in dataset:
            for item in query:
                attr_count[item] = 1 if item not in attr_count else attr_count[item] + 1
             
        for index, query in dataset:
            inputset.append((index, query, sum([attr_count[k] for k in query])))
        
        
    def __add_time(self, data, t1, t2):
        for idx, _ in data:
            self.waiting['dispatch'][idx] = t2 - t1
            
            
    def predict(self):
        """!
        @brief Method used to process queries according to FeatureRank scheduler policy
        @details In this method, queries are performed in accordance with the relevance 
                 of the query attributes though the analysis of dataset
        
        @code
            @input: [
                        (idx, [f1, f2, ..., fn]),
                        ... ...  ...            ,
                        (idx, [f1, f2, ..., fn])
                    ]
        @endcode
        
        @return (matrix) of queries indexed and sorted by the worker type id
            @output:[
                        (worker_id, query_id),
                        ... ...  ...         ,
                        (worker_id, query_id)
                    ]
        """
        workload = 0 
        
        self.get_all_tasks()
        
        t1 = time.time()
        while workload < self.sizeof:
            inputset = []
            chunk = self.get_chunk()
            workload += len(chunk)
            self.__evaluated_model(chunk, inputset)
            data = list(map(lambda x: [x[0],x[1]], sorted(inputset, key=lambda x:(x[2],x[1]), reverse=True)))
            self.assign_tasks(data, self.workload.mod_or_div)
            
        self.set_exit()
        self.metrics['schell_runtime'] = time.time() - t1

        print('[INFO]: time expended for scheduling the tasks: ', self.metrics['schell_runtime']) if self.isverbose else None
        
        
        
        
        
        
        
        
        
        