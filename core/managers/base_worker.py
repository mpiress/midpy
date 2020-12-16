"""!

@PyMid is deployed to manage machine learn algorithms in a multitask execution.

@authors Michel Pires da Silva
@email michelpires@dcc.ufmg.br / michel@cefetmg.br

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
from core.managers.worker import Worker
from containers.wrapper.wrappers import NetworkWrapper, WorkloadWrrapper, CacheWrapper
from containers import constants
from core.network.pipes import lookup
from collections import Counter

import socket, time, csv
import pandas as pd

class BaseWorker:
    
    def __init__(self, job, conn:NetworkWrapper, workload:WorkloadWrrapper, cache:CacheWrapper, wid, schell, cache_descriptor, output_path, isverbose):
        self.__job              = job
        self.__bytask           = {}
        self.__conn             = conn
        self.__workload         = workload
        self.__output_path      = output_path
        self.__isverbose        = isverbose
        self.__cache            = cache
        self.__id_worker        = wid
        self.__output           = None
        self.__task_similarity  = {}
        self.__name_scheduler   = schell
        self.__cache_descriptor = cache_descriptor
        
    def __modules_init(self):
        self.__task_similarity = {}
        self.__output = {'times':{}, 'size_of_work':0, 'general_runtime':0, 'tasks_runtime':0, 'global_queue_runtime':0,'number_of_rules':0, 'number_of_hits':0, 'size_of_cache':0}
        self.__global_queue_results = lookup(conn=self.__conn, uri='global.queues.results')
        self.__tasks = lookup(conn=self.__conn, uri='global.queues.tasks'+str(self.__id_worker))
        self.__worker = Worker(self.__job, self.__output)
        cache = type('Cache', (self.__cache.type_cache,), {})
        cache = cache(self.__id_worker, self.__cache.capacity)
        self.__job.cache = cache
        self.__job.clear_all()
        
        if self.__workload.train_neural_network:
            self.__train_nn = lookup(conn=self.__conn, uri='global.queues.train_nn')


    def __cache_analyser(self):
        lasttask = []
        Y = []

        print('[INFO]: Worker ', self.__id_worker, ' started with ', self.__job.cache.size(), ' rules cached') if self.__isverbose else None
        task = self.__tasks.get()
        
        while task[0] != 'EXIT':
            t1 = time.time()
            rules = self.__cache_descriptor.processing(task[1])
            
            for r in rules:
                tmp = self.__job.cache.get(r)
                if tmp == -1:
                    self.__job.cache.set(r, 0)

            tmp = self.__job.cache.get_task_rules()

            if lasttask:
                value = len(tmp & lasttask[1])/len(tmp)
                self.__train_nn.put({'t1':lasttask[0], 't2':task[0], 'similarity':value}, self.__id_worker)
                print('t1:', len(lasttask[1]), 't2:', len(tmp), 'value:', value)
    
            lasttask = (task[0], tmp)
            task = self.__tasks.get()
            #print('[INFO]: TEMPO: ', time.time() - t1)

        print('[INFO]: Worker ',self.__id_worker,' Finalized with ', self.__job.cache.get_hits(), ' hits and ', self.__job.cache.get_missing(),' missing') if self.__isverbose else None
        print(Counter(Y))

    def __execute_tasks(self):
        sworkload = 0
        lasttask = []
        
        print('[INFO]: Worker ', self.__id_worker, ' started with ', self.__job.cache.size(), ' rules cached') if self.__isverbose else None
        task = self.__tasks.get()
        start = time.time()
        ttmp = 0
        
        while task[0] != 'EXIT':
            hits     = self.__job.cache.get_hits()
            missing  = self.__job.cache.get_missing()
            sworkload += 1
            t1 = time.time() 
            result = self.__worker.processing((task[0], task[1]))
            self.__bytask[task[0]] = [self.__job.cache.get_hits() - hits, self.__job.cache.get_missing() - missing] 
            ttmp += (time.time() - t1)
            print('[INFO]: TEMPO: ', time.time() - t1)
            
            tmp = self.__job.cache.get_task_rules()
                
            if sworkload > 1:
                t2 = time.time()
                key = (lasttask[0][0], task[0])
                value = round(len(tmp & lasttask[1])/len(tmp), 2) if len(tmp) > 0 else 0.0 
                self.__task_similarity[key] = (value, self.__job.cache.get_discards())
                self.__output['evaluate_cache_similarity'] = (time.time() - t2) if 'evaluate_cache_similarity' not in self.__output else (self.__output['evaluate_cache_similarity'] + (time.time() - t2))           
                #print('PAIR:', value)

            lasttask = (task, tmp)
            task = self.__tasks.get()
            self.__job.cache.clear_evaluations()
            
        self.__output['worker_runtime']         = time.time() - start
        self.__output['size_of_work']           = sworkload
        self.__output['tasks_runtime']          = ttmp - self.__job.cache.time
        self.__output['times']                  = self.__job.times
        self.__output['size_of_cache']          = self.__job.cache.size()
        self.__output['number_of_rules']        = self.__job.cache.get_missing()
        self.__output['number_of_hits']         = self.__job.cache.get_hits()
        self.__output['cache_memory_usage']     = self.__job.cache.get_capacity_in_bytes()
        
        
        print('[INFO]: Worker ',self.__id_worker, ' Finished with ', self.__output['size_of_work'], ' tasks processed and,', self.__job.cache.size(),' rules cached') if self.__isverbose else None
        print('[INFO]: Worker ',self.__id_worker,' Finalized with ', self.__job.cache.get_hits(), ' hits and ', self.__job.cache.get_missing(),' missing') if self.__isverbose else None
        
        self.__output['general_runtime'] = time.time() - start
        output = {socket.gethostname():{self.__id_worker:self.__output}}
        
        self.__global_queue_results.put(output, self.__id_worker)

        
    def __save_internal_data(self):
        md = '#div' if self.__workload.mod_or_div else '#mod'
        app = self.__job.__class__.__name__.lower()
        tcache = self.__cache.type_cache.__name__.lower()
        
        sizeof = self.__cache.percent if self.__cache.percent >= 0 else 0
        md = '#div' if self.__workload.mod_or_div else '#mod'
        output = self.__output_path + app+'_'+tcache+'_'+'w'+str(self.__id_worker)+'_'+md+'.csv'
        with open(output, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=' ')
            writer.writerow(['---------------------> ' + self.__name_scheduler + ' SCHEDULLER, CACHE WITH ' + str(sizeof) + '% AND CHUNK OF ('+str(self.__workload.overview['chunk'])+') -----------------'])
            for key, value in self.__task_similarity.items():
                ht1 = self.__bytask[key[0]][0]
                rt1 = self.__bytask[key[0]][1]
                ht2 = self.__bytask[key[1]][0]
                rt2 = self.__bytask[key[1]][1]
                aux = {'t1':key[0], 't2':key[1], 'similar?':value[0], 'premature_discard':value[1][0], 'discarded':value[1][1], 'used':value[1][2], 'hits_t1':ht1, 'rules_t1':rt1, 'hits_t2':ht2, 'rules_t2':rt2}
                writer.writerow([aux])
            writer.writerow(['#'])
            
    def processing(self): 
        self.__modules_init()
        worker = socket.gethostbyname(socket.getfqdn())
        print('[INFO]: Start worker ', worker) if self.__isverbose else None
        
        t1 = time.time()
        self.__cache_analyser() if self.__workload.train_neural_network else self.__execute_tasks()
        runtime = time.time() - t1
        self.__save_internal_data() if not self.__workload.train_neural_network else None
        
        print('[INFO]: Worker successfully completed') if self.__isverbose else None
        
        return runtime
        
        


