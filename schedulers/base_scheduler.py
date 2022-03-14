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
from containers import constants
from containers.wrapper.wrappers import NetworkWrapper, WorkloadWrrapper, SchedulerWrapper
from multiprocessing.managers import BaseManager

import math, csv

class SchedulerManager(BaseManager):
    
    def __init__(self, conn:NetworkWrapper, workload:WorkloadWrrapper, schell:SchedulerWrapper, workers_queues, descriptor, warmup, isverbose=True):
        self.descriptor         = descriptor
        self.descriptor.load()

        self.warmup             = warmup
        self.warmup.load()
        

        self.conn               = conn
        self.workload           = workload
        self.schell             = schell
        self.isverbose          = isverbose
        self.sizeof             = self.descriptor.sizeof()
        self.metrics            = {'schell_runtime':0, 'generate_train_nn':0, 'workload':self.sizeof, 'workload_wid':{wid:[] for wid in range(self.conn.nworkers)}}
        self.size_of_chunk      = workload.overview['chunk']
        self.__workers_queues   = workers_queues
        self.__dataindex        = 0

        
        
        
    def get_metrics(self):
        return self.metrics
        
    
    def warmup_cache(self, sig=None):
        wid = 0
        
        while wid < self.conn.nworkers: 
            query = self.warmup.readline()
            query = ['wup'+str(wid), query]
            self.assign_tasks([query], self.workload.mod_or_div, wid)
            if sig != None and wid in sig:
                sig[wid][query[0]] = query[1]
            wid += 1
    

    def get_chunk(self):
        chunk = []
        while (self.__dataindex < self.sizeof) and (len(chunk) < self.workload.overview['chunk']):
            query = self.descriptor.readline()
            query = [self.__dataindex, query]
            chunk.append(query)
            self.__dataindex += 1
        self.size_of_chunk = len(chunk)
        return chunk

    def set_exit(self):
        for wid in range(self.conn.nworkers):
            self.__workers_queues[wid].put(['EXIT'])
        self.metrics['schell_runtime'] = self.metrics['schell_runtime'] - self.metrics['generate_train_nn'] 
    
    
    def assign_tasks(self, dataset, div=True, wid=None):
        workload = 0
        
        if wid != None:
            for query in dataset:
                self.__workers_queues[wid].put(query)
                self.metrics['workload_wid'][wid].append(query[0])
                    
        else:
                
            if div:

                sizeof = math.floor(len(dataset)/self.conn.nworkers)
                workload = sizeof * self.conn.nworkers
                wid    = 0
                pos    = 0
                
                while workload > 0:
                    wid = wid % self.conn.nworkers
                    idx = (wid * sizeof) + pos
                    query = dataset[idx]
                    self.__workers_queues[wid].put(query)
                    self.metrics['workload_wid'][wid].append(query[0])
                    wid += 1
                    if wid % self.conn.nworkers == 0:
                        pos += 1
                    workload -= 1
                    
                wid = 0
                idx = 0 
                dataset = dataset[sizeof*self.conn.nworkers:]
                workload = len(dataset)
                while workload > 0:
                    wid = wid % self.conn.nworkers
                    query = dataset[idx]
                    self.__workers_queues[wid].put(query)
                    self.metrics['workload_wid'][wid].append(query[0])
                    workload -= 1
                    wid += 1
                    idx += 1
                    
    
            else:
                wid = 0
                idx = 0
                workload = len(dataset)
                while workload > 0:
                    wid = wid % self.conn.nworkers
                    query = dataset[idx]
                    self.__workers_queues[wid].put(query)
                    self.metrics['workload_wid'][wid].append(query[0])
                    workload -= 1
                    wid += 1
        
             

    
    def predict(self):
        """!
        @brief Method implemented by scheduler policies to predict the queries order
        @details Each schedule policy uses this method to implement rules that are applied to sort queries
        """
        raise NotImplementedError("this method is not implemented correctless")
    
    
    
        
