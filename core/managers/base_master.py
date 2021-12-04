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
from core.network.pipes import ResultQueues, TaskQueues, LookupWids, obj_publisher
from core.managers.orchestrator import Orchestrator
from containers.wrapper.wrappers import NetworkWrapper, SchedulerWrapper, WorkloadWrrapper
from concurrent import futures

from reduce.reduce import Reduce

import csv, time
import pandas as pd

from containers import constants


class BaseMaster():
    
    def __init__(self, conn:NetworkWrapper, workload:WorkloadWrrapper, schell:SchedulerWrapper, descriptor, isverbose):
        
        self.__workload = workload
        self.__schell = schell
        self.__isverbose = isverbose
        self.__daemons = {}
        self.__conn = conn
        self.__descriptor = descriptor
        
        #remote objects
        self.__qresults         = ResultQueues(conn.nworkers)
        self.__wids             = LookupWids(conn.nworkers, conn.wpool)
        self.__workers_queues   = {wid:TaskQueues() for wid in range(self.__conn.nworkers)}
        
        prefix = 'global.queues.'
        object_names = [('lookup_wids', self.__wids), ('results', self.__qresults)]
        
        if self.__workload.train_neural_network:
            self.__data_train_nn = ResultQueues(conn.nworkers)
            object_names.append(('train_nn', self.__data_train_nn))
        
        for name, obj in object_names:
            name, daemon = obj_publisher(obj, prefix, name, self.__conn)
            self.__daemons[name] = daemon
        
        for wid in self.__workers_queues:
            name, daemon = obj_publisher(self.__workers_queues[wid], prefix, 'tasks'+str(wid), self.__conn)
            self.__daemons[name] = daemon
                
    def __start_scheduler(self, warmup_cache):
        print('[INFO]: prepare scheduler strategy') if self.__isverbose else None
        dispatcher = Orchestrator(self.__conn, self.__workload, self.__schell, self.__workers_queues, self.__descriptor, warmup_cache, self.__isverbose)
        dispatcher.schedulling()
        return dispatcher.get_metrics()
        
    def get_daemons(self):
        return self.__daemons
    
    
    def get_nn_results(self, wid):
        tasks = []
        
        t = self.__data_train_nn.get(wid)
        while(t != 'EXIT'):
            tasks.append(t)
            t = self.__data_train_nn.get(wid)
        
        return tasks
            

    def generate_header(self, metrics, output):
        with open(output[0], 'a', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=' ')
            writer.writerow(['---------------------> ' + self.__schell.type_scheduler.__name__ + ' SCHEDULLER AND CACHE WITH ' + output[1] + ' TASKS -----------------'])
            writer.writerow(['CHUNK(' + str(self.__workload.overview['chunk']) + ')'])
            for m in metrics:
                writer.writerow(['Scheduling ' + m + ':' + str(metrics[m])]) 

    
    def processing(self, output, warmup_cache):
        reduce = Reduce(self.__conn)

        t1 = time.time()
        metrics = self.__start_scheduler(warmup_cache)
        self.generate_header(metrics, output) if not self.__workload.train_neural_network else None
        print('[INFO]: waiting for queries to be processed') if self.__isverbose else None
        
        if self.__workload.train_neural_network:
            tasks = []
            with futures.ThreadPoolExecutor(max_workers=1) as executor:
                pool = {executor.submit(self.get_nn_results, wid) : wid for wid in range(self.__conn.nworkers)}

            for feature in futures.as_completed(pool):
                tasks += feature.result()
                
            df = pd.DataFrame(tasks, columns=['t1', 't2', 'similarity'])
            df.to_csv(constants.BUFFERNN+self.__workload.job_name+'_train.csv', index=None)

        else:
            with futures.ThreadPoolExecutor(max_workers=1) as executor:
                pool = {executor.submit(reduce.reduce, wid, output) : wid for wid in range(self.__conn.nworkers)} 

            for feature in futures.as_completed(pool):
                data = feature.result()
                
            with open(output[0], 'a', newline='') as csvfile:
                writer = csv.writer(csvfile, delimiter=' ')
                writer.writerow(['#'])

        if not self.__workload.train_neural_network:
            print('[INFO]: global task queue processed') if self.__isverbose else None
        
        return metrics['schell_runtime'], time.time() - t1
            