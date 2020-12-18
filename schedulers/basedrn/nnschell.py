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

from neural_network.siamese import SIAMESE
import time, math, os
import numpy as np
import time 

from collections import OrderedDict
from sklearn.cluster import KMeans
from itertools import combinations

import sys
sys.setrecursionlimit(10000)
            



class BASENNSCHELL(SchedulerManager):

    def __init__(self, conn:NetworkWrapper, workload:WorkloadWrrapper, workers_queues, descriptor, isverbose=True):
        super(BASENNSCHELL, self).__init__(conn, workload, workers_queues, descriptor, isverbose)
        self.model = SIAMESE(descriptor=descriptor, job=workload.job_name)
    
    def generate_graph(self, edges):
        graph = {}
        for p, v in edges:
            if v[0] not in graph:
                graph[v[0]] = set()
            if v[1] not in graph:
                graph[v[1]] = set()
            if p > 0:
                graph[v[0]].add(v[1])
                graph[v[1]].add(v[0])
        return graph
 
    
    def __dfs_visit(self, data, graph, visited, t1, sizeof, chunk):
        if t1 not in visited:
            task = (t1, chunk.pop(t1))
            data.append(task)
            sizeof -= 1
            visited.append(t1)
            for neighbour in graph[t1]:
                if neighbour not in visited:
                    self.__dfs_visit(data, graph, visited, neighbour, sizeof, chunk)  
    
    
    def DFS(self, graph, sizeof, chunk):
        data = []
        visited = []
        for t1 in graph:
            self.__dfs_visit(data, graph, visited, t1, sizeof, chunk)
            if sizeof == 0:
                break
                
        return data


    def BFS(self, graph, sizeof, chunk):
        data  = []
        queue = []
        visited = []

        for t1 in graph:

            if t1 not in visited:
                visited.append(t1)
                queue.append(t1)
                task = (t1, chunk.pop(t1))
                data.append(task)
                sizeof -= 1

                while queue and sizeof > 0:
                    node = queue.pop(0)
                    for neighbour in graph[node]:
                        if neighbour not in visited and sizeof > 0:
                            visited.append(neighbour)
                            queue.append(neighbour)
                            task = (neighbour, chunk.pop(neighbour))
                            data.append(task)
                            sizeof -= 1

        return data

    def combinations(self, chunk, centroids):
        t1  = []
        t2  = []
        idx = []

        keys   = list(set(chunk.keys()) - set(centroids.keys()))
        values = [chunk[k] for k in keys]

        sizeof = len(keys)
        for key, value in centroids.items():
            t1 += values
            t2 += [value] * sizeof
            idx += list(zip(keys, [key]*sizeof))

        return t1, t2, idx
    
    def sizeof_by_worker(self):
        size = math.floor(self.size_of_chunk/self.conn.nworkers)
        sizeof = {wid:size for wid in range(self.conn.nworkers)}
        wid = 0
        while(sum(sizeof.values()) < self.size_of_chunk):
            wid = wid % self.conn.nworkers
            sizeof[wid] += 1
            wid += 1
        return sizeof

    
    
class NNSCHELLBYSIGNATURE(BASENNSCHELL):
    
    def __init__(self, conn:NetworkWrapper, workload:WorkloadWrrapper, workers_queues, descriptor, isverbose=True):
        
        super(NNSCHELLBYSIGNATURE, self).__init__(conn, workload, workers_queues, descriptor, isverbose)
        self.__kcentroids   = 1
        self.__sizeoftasks  = 1
        self.__signatures   = {}     
    
    def predict(self):
        workload = 0

        print('[INFO]: assign', str(self.sizeof),'tasks for ',str(self.conn.nworkers),' worker(s)') if self.isverbose else None
        
        start = time.time()
        while workload < self.sizeof:
            
            chunk = OrderedDict(self.get_chunk())
            workload += self.size_of_chunk
            data = {wid:[] for wid in range(self.conn.nworkers)}
            
            if len(self.__signatures) == 0:
                self.__signatures = {wid:OrderedDict() for wid in range(self.conn.nworkers)}
                for wid in range(min(len(chunk), self.conn.nworkers)):
                    task = chunk.popitem()
                    data[wid].append(task)
                    self.__signatures[wid][task[0]] = task[1]

            while chunk:

                for wid in range(min(len(chunk), self.conn.nworkers)):
                    t1, t2, idx = self.combinations(chunk, self.__signatures[wid])
                    pred = list(zip(self.model.predict(t1, t2), idx))
                    edges = list(sorted(pred, key=lambda x:x[0], reverse=True)) 
                    for _ in range(min(self.__sizeoftasks, len(chunk))):
                        task = edges.pop(0)[1][0]
                        task = (task, chunk.pop(task))
                        data[wid].append(task)

                        if len(self.__signatures[wid]) < self.__kcentroids:
                            self.__signatures[wid][task[0]] = task[1]
                        
                        else:
                            self.__signatures[wid].popitem()
                            self.__signatures[wid][task[0]] = task[1]
                    
            chunk = []
            for wid in (range(self.conn.nworkers)):
                chunk += data[wid]

            self.assign_tasks(chunk, self.workload.mod_or_div)

        self.set_exit()
        self.metrics['schell_runtime'] = time.time() - start
        print('[INFO]: time expended for scheduling the tasks: ', self.metrics['schell_runtime']) if self.isverbose else None
    


class NNSCHELLBYKCLUSTERS(BASENNSCHELL):
    
    def __init__(self, conn:NetworkWrapper, workload:WorkloadWrrapper, tasks, descriptor, isverbose=True):
        super(NNSCHELLBYKCLUSTERS, self).__init__(conn, workload, tasks, descriptor, isverbose)
        self.__maxcent      = 0.10 
        self.__mincent      = 4
        self.__kcentroids   = 0 
        self.__centlimit    = 50     


    #estimate based in elbow curve 
    def __elbow_method(self, inertia):
        m = np.mean(inertia)
        k =[(index, math.pow((point - m), 2)) for index, point in enumerate(inertia, self.__mincent)]
        k = sorted(k, key=lambda x:x[1])
        return k[0][0]
        
    
    def __estimante_nclusters(self, chunk):
        inertia = []
        model = KMeans()
        maxcent = max(math.ceil(self.size_of_chunk*self.__maxcent), self.__mincent)
        if maxcent > self.__mincent:
            for k in range(self.__mincent, maxcent):
                kmeans = KMeans(n_clusters=k, random_state=42).fit(list(chunk.values()))
                inertia.append(kmeans.inertia_)
        k = self.__elbow_method(inertia) if maxcent > self.__mincent else self.__mincent
        return k
    

    def predict(self):
        workload = 0
        
        print('[INFO]: assign', str(self.sizeof),'tasks for ',str(self.conn.nworkers),' worker(s)') if self.isverbose else None
        
        start = time.time()
        while workload < self.sizeof:
            chunk = OrderedDict(self.get_chunk())
            workload += self.size_of_chunk
            
            tp = time.time()
            if ((self.__kcentroids == 0) or ((self.size_of_chunk < self.workload.overview['chunk']) and (self.__kcentroids > self.size_of_chunk/2))):
                self.__kcentroids = 25 #self.__estimante_nclusters(chunk) #min(max(math.ceil(self.size_of_chunk*self.__maxcent), self.__mincent), self.__centlimit)
                print('[INFO]: Number of centroids:', self.__kcentroids)
            
            centroids = dict(list(chunk.items())[0:self.__kcentroids])
            t1, t2, idx = self.combinations(chunk, dict(centroids))
            pred = list(zip(self.model.predict(t1, t2), idx))
            
            edges  = list(sorted(pred, key=lambda x:x[0], reverse=True)) 
            graph = self.generate_graph(edges)
            self.metrics['predict'] = time.time() - tp if 'predict' not in self.metrics else self.metrics['predict'] + (time.time() - tp)
            
            t1 = time.time()
            data = self.DFS(graph, self.size_of_chunk, chunk)    
            self.metrics['process_graph'] = time.time() - t1 if 'process_graph' not in self.metrics else self.metrics['process_graph'] + (time.time() - t1)
            
            t1 = time.time()
            self.assign_tasks(data, self.workload.mod_or_div)
            self.metrics['send_tasks'] = time.time() - t1 if 'send_tasks' not in self.metrics else self.metrics['send_tasks'] + (time.time() - t1)

        self.set_exit()
        self.metrics['schell_runtime'] = time.time() - start
        print('[INFO]: time expended for scheduling the tasks: ', self.metrics['schell_runtime']) if self.isverbose else None


class NNSCHELLFORALL(BASENNSCHELL):
    
    def __init__(self, conn:NetworkWrapper, workload:WorkloadWrrapper, tasks, descriptor, isverbose=True):
        super(NNSCHELLFORALL, self).__init__(conn, workload, tasks, descriptor, isverbose)
        
    def predict(self):
        workload = 0
        
        print('[INFO]: assign', str(self.sizeof),'tasks for ',str(self.conn.nworkers),' worker(s)') if self.isverbose else None
        
        start = time.time()
        while workload < self.sizeof:
            chunk = OrderedDict(self.get_chunk())
            workload += self.size_of_chunk
            
            tp = time.time()
            idx  = list(combinations(chunk.keys(), 2))
            t1   = []
            t2   = []
            for k1, k2 in idx:
                t1.append(chunk[k1])
                t2.append(chunk[k2])

            pred = list(zip(self.model.predict(t1, t2), idx))
            
            edges  = list(sorted(pred, key=lambda x:x[0], reverse=True)) 
            graph = self.generate_graph(edges)
            self.metrics['predict'] = time.time() - tp if 'predict' not in self.metrics else self.metrics['predict'] + (time.time() - tp)
            
            t1 = time.time()
            data = self.DFS(graph, self.size_of_chunk, chunk)    
            self.metrics['process_graph'] = time.time() - t1 if 'process_graph' not in self.metrics else self.metrics['process_graph'] + (time.time() - t1)
            
            t1 = time.time()
            self.assign_tasks(data, self.workload.mod_or_div)
            self.metrics['send_tasks'] = time.time() - t1 if 'send_tasks' not in self.metrics else self.metrics['send_tasks'] + (time.time() - t1)

        self.set_exit()
        self.metrics['schell_runtime'] = time.time() - start
        print('[INFO]: time expended for scheduling the tasks: ', self.metrics['schell_runtime']) if self.isverbose else None
