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
from itertools import combinations, permutations
from operator import itemgetter

import sys
sys.setrecursionlimit(10000)
            
from igraph import Graph


class BASENNSCHELL(SchedulerManager):

    def __init__(self, conn:NetworkWrapper, workload:WorkloadWrrapper, workers_queues, descriptor, isverbose=True):
        super(BASENNSCHELL, self).__init__(conn, workload, workers_queues, descriptor, isverbose)
        self.model = SIAMESE(descriptor=descriptor, job=workload.job_name)
    
    def generate_graph(self, edges):
        graph = OrderedDict()
        for p, v in edges:
            if v[0] not in graph:
                graph[v[0]] = list()
            if v[1] not in graph:
                graph[v[1]] = list()
            if p > 0:
                graph[v[0]].append(v[1])
                graph[v[1]].append(v[0])
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
    
    def neighborhoodRank(self, dataset):
        outputset = []
        edges = []
        codec = {}
        code = 0
        
        for query in dataset:
            query = list(enumerate(query[1]))
            tmp   = []
            for v in query:
                if v not in codec:
                    codec[v] = code
                    code += 1
            edges += [(codec[query[i]], codec[query[i+1]]) for i in range(len(query)-1)] + [(codec[query[-1]], codec[query[0]])]
        
        G = Graph(edges)
        attr_count = dict(enumerate(G.pagerank()))
        
        t1 = time.time()
        for index, query in dataset:
            tmp = 0
            q = [codec[v] for v in enumerate(query)]
            edges = permutations(q, 2)
            for e1, e2 in edges:
                tmp += (attr_count[e1] + attr_count[e2])
            outputset.append((index, query, tmp))
        
        outputset = list(map(lambda x: (x[0], x[1]), sorted(outputset, key=lambda x: x[2], reverse=True)))

        return outputset
        

class NNSCHELLBYSIGNATURE(BASENNSCHELL):
    
    def __init__(self, conn:NetworkWrapper, workload:WorkloadWrrapper, workers_queues, descriptor, isverbose=True):
        
        super(NNSCHELLBYSIGNATURE, self).__init__(conn, workload, workers_queues, descriptor, isverbose)
        self.__sigsize      = 1
        self.__sizeofbucket = 1
        self.__signatures   = {} 
        self.__sigmanager   = {}    
    
    def predict(self):
        workload = 0

        print('[INFO]: assign', str(self.sizeof),'tasks for ',str(self.conn.nworkers),' worker(s)') if self.isverbose else None
        
        start = time.time()
        while workload < self.sizeof:
            
            chunk = OrderedDict(self.get_chunk())
            workload += self.size_of_chunk
            self.__sizeofbucket = math.ceil(len(chunk)/self.conn.nworkers)
            
            while chunk:

                count = [0]*self.conn.nworkers
                
                if len(self.__signatures) == 0:
                    self.__signatures = {wid:OrderedDict() for wid in range(self.conn.nworkers)}
                    self.__sigmanager = {wid:[] for wid in range(self.conn.nworkers)}
                    
                    #define centroids
                    sizeofslice = math.floor(len(chunk)/2)
                    c1 = dict(list(chunk.items())[0:sizeofslice])
                    c2 = dict(list(chunk.items())[sizeofslice:])
                    t1, t2, idx = self.combinations(c1, c2)
                    
                    pred = list(zip(self.model.predict(t1, t2), idx))
                    edges  = list(sorted(pred, key=lambda x:x[0], reverse=True)) 
                    graph = self.generate_graph(edges)
                    data = self.DFS(graph, len(chunk), chunk) 
                    
                    for wid in range(min(len(data), self.conn.nworkers)):
                        task = data.pop(0)
                        self.assign_tasks([task], self.workload.mod_or_div, wid)
                        self.__signatures[wid][task[0]] = task[1]
                        self.__sigmanager[wid].append(task[0])
                        count[wid] += 1

                    chunk = dict(data)

                T1  = []
                T2  = []
                IDX = []
                
                for wid in range(min(len(chunk), self.conn.nworkers)):
                    t1, t2, idx = self.combinations(chunk, self.__signatures[wid])
                    T1  += t1
                    T2  += t2
                    IDX += list(zip(idx, [wid]*len(idx)))
                
                pred    = list(zip(self.model.predict(T1, T2), IDX))
                edges   = list(sorted(pred, key=lambda x:x[0], reverse=True)) 
                
                while chunk and (sum(count) < (self.__sizeofbucket * self.conn.nworkers)):
                    task = edges.pop(0)
                    wid  = task[1][1]
                    idx  = task[1][0][0]
                    
                    if count[wid] < self.__sizeofbucket and idx in chunk:
                        task = (idx, chunk.pop(idx))
                        self.assign_tasks([task], self.workload.mod_or_div, wid)
                        count[wid] += 1
                            
                        if len(self.__signatures[wid]) >= self.__sigsize:
                            key = self.__sigmanager[wid].pop(0)
                            self.__signatures[wid].pop(key)
                            
                        self.__signatures[wid][task[0]] = task[1]
                        self.__sigmanager[wid].append(task[0])
                    
                    
        self.set_exit()
        self.metrics['schell_runtime'] = time.time() - start
        print('[INFO]: time expended for scheduling the tasks: ', self.metrics['schell_runtime']) if self.isverbose else None
    


class NNSCHELLBYKCLUSTERS(BASENNSCHELL):
    
    def __init__(self, conn:NetworkWrapper, workload:WorkloadWrrapper, tasks, descriptor, isverbose=True):
        super(NNSCHELLBYKCLUSTERS, self).__init__(conn, workload, tasks, descriptor, isverbose)
        self.__kcentroids   = 5 
        

    def predict(self):
        workload = 0
        
        print('[INFO]: assign', str(self.sizeof),'tasks for ',str(self.conn.nworkers),' worker(s)') if self.isverbose else None
        
        start = time.time()
        while workload < self.sizeof:
            chunk = OrderedDict(self.get_chunk())
            workload += self.size_of_chunk
            
            tp = time.time()
            
            #define centroids
            sizeofslice = math.floor(len(chunk)/2)
            c1 = dict(list(chunk.items())[0:sizeofslice])
            c2 = dict(list(chunk.items())[sizeofslice:])
            t1, t2, idx = self.combinations(c1, c2)
            
            pred = list(zip(self.model.predict(t1, t2), idx))
            edges  = list(sorted(pred, key=lambda x:x[0], reverse=True)) 
            graph = self.generate_graph(edges)
            data = self.DFS(graph, len(chunk), chunk)    
            
            chunk = dict(data)

            t1, t2, idx = self.combinations(dict(data[self.__kcentroids:]), dict(data[0:self.__kcentroids]))
            pred = list(zip(self.model.predict(t1, t2), idx))
            edges  = list(sorted(pred, key=lambda x:x[0], reverse=True)) 
            graph = self.generate_graph(edges)
            data = self.DFS(graph, len(chunk), chunk)    
            
            self.metrics['predict'] = time.time() - tp if 'predict' not in self.metrics else self.metrics['predict'] + (time.time() - tp)
            
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
            
            ####### MODIFICAÇÃO COMEÇA AQUI ######################
            #data = []
            #for idx, t in edges:
            #    if not chunk:
            #        break
            #    if t[0] in chunk:
            #        task = (t[0], chunk.pop(t[0]))
            #        data.append(task)
            #    if t[1] in chunk:
            #        task = (t[1], chunk.pop(t[1]))
            #        data.append(task)
            ####### MODIFICAÇÃO TERMINA AQUI #####################
            
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
