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
import time, math
import time, random, csv

from collections import OrderedDict
from itertools import combinations, permutations

import sys
sys.setrecursionlimit(10000)
            
from igraph import Graph


class BASENNSCHELL(SchedulerManager):

    def __init__(self, conn:NetworkWrapper, workload:WorkloadWrrapper, workers_queues, descriptor, warmup_cache=0, isverbose=True):
        super(BASENNSCHELL, self).__init__(conn, workload, workers_queues, descriptor, warmup_cache, isverbose)
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
        
        for index, query in dataset:
            tmp = 0
            q = [codec[v] for v in enumerate(query)]
            edges = permutations(q, 2)
            for e1, e2 in edges:
                tmp += (attr_count[e1] + attr_count[e2])
            outputset.append((index, query, tmp))
        
        outputset = list(map(lambda x: (x[0], x[1]), sorted(outputset, key=lambda x: x[2], reverse=True)))

        return outputset
    
    def neighborhoodRank_local_coordinate(self, dataset):
        edges = []
        codec = {}
        idf    = {}
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
        local_weight = sum(attr_count.values())
        
        outputset = {}
        for index, query in dataset:
            outputset[index] = math.log2(1 + sum([attr_count[codec[v]] for v in enumerate(query)]))
             
        return outputset
        

class NNSCHELLBYSIGNATURE(BASENNSCHELL):
    
    def __init__(self, conn:NetworkWrapper, workload:WorkloadWrrapper, workers_queues, descriptor, warmup_cache=0, isverbose=True):
        
        super(NNSCHELLBYSIGNATURE, self).__init__(conn, workload, workers_queues, descriptor, warmup_cache, isverbose)
        self.__sigsize      = warmup_cache
        self.__sizeofbucket = self.workload.overview['bucket']
        self.__signatures   = {wid:OrderedDict() for wid in range(self.conn.nworkers)}
        
    def predict(self):
        workload = 0
        count = []
        wids  = []
        #data_tmp = {wid:[] for wid in range(self.conn.nworkers)}
        #file = "/home/michel/Doutorado/tmp/datasets/nscale_" + str(self.conn.nworkers) + "w" + str(self.warmup) + ".csv"

        print('[INFO]: assign', str(self.sizeof),'tasks for ',str(self.conn.nworkers),' worker(s)') if self.isverbose else None
        
        t1 = time.time()
        workload += self.warmup_cache(self.__signatures)
        self.metrics['schell_warmup_cache'] = time.time() - t1    

        start = time.time()
        while workload < self.sizeof:
            
            chunk     = OrderedDict(self.get_chunk())
            workload += self.size_of_chunk
            
            while chunk:
                if not wids:
                    count = [0]*self.conn.nworkers
                    wids  = [wid for wid in range(self.conn.nworkers)]

                T1  = []
                T2  = []
                IDX = []
                
                for wid in wids:
                    t1, t2, idx = self.combinations(chunk, self.__signatures[wid])
                    T1  += t1
                    T2  += t2
                    IDX += list(zip(idx, [wid]*len(idx)))
                
                pred    = list(zip(self.model.predict(T1, T2), IDX))
                edges   = list(sorted(pred, key=lambda x:x[0], reverse=True)) 
                
                buckets     = {wid:[] for wid in wids}
                for p, t in edges:
                    wid  = t[1]
                    idx  = t[0][0]
                    buckets[wid].append([p, idx])
                    
                while chunk and wids:
                    tasks = []
                    
                    for wid in wids:
                        tasks.append((wid, buckets[wid].pop(0)))
                        tasks[-1][1][0] = math.log2(1 + tasks[-1][1][0] + buckets[wid][0][0]) if buckets[wid] else 0
                    tasks = sorted(tasks, key=lambda x:x[1][0])
                    
                    tam = math.ceil(len(tasks)/self.conn.nworkers)
                    self.__sizeofbucket = self.__sizeofbucket if  tam >= self.__sizeofbucket else tam

                    for wid, t in tasks:
                        
                        if count[wid] < self.__sizeofbucket and t[1] in chunk:
                            task = (t[1], chunk.pop(t[1]))
                            self.assign_tasks([task], self.workload.mod_or_div, wid)
                            
                            #TEMPORÁRIO, REMOVER DEPOIS LINHA ABAIXO....
                            #data_tmp[wid].append(task[1])
                            
                            count[wid] += 1
                                
                            if len(self.__signatures[wid]) >= self.__sigsize:
                                self.__signatures[wid].popitem(last=False)

                            self.__signatures[wid][task[0]] = task[1]
                            
                        if count[wid] == self.__sizeofbucket:
                            wids.remove(wid)
            
                
        self.set_exit()
        self.metrics['schell_runtime'] = time.time() - start
        print('[INFO]: time expended for scheduling the tasks: ', self.metrics['schell_runtime']) if self.isverbose else None

        #TEMPORÁRIO, REMOVER DEPOIS LINHA ABAIXO....
        #with open(file, 'a', newline='') as csvfile:
        #    writer = csv.writer(csvfile, delimiter=',')
        #    for wid in range(self.conn.nworkers):
        #        for t in data_tmp[wid]:
        #            writer.writerow(t)
        

class NNSCHELLBYKCLUSTERS(BASENNSCHELL):
    
    def __init__(self, conn:NetworkWrapper, workload:WorkloadWrrapper, tasks, descriptor, warmup_cache=0, isverbose=True):
        super(NNSCHELLBYKCLUSTERS, self).__init__(conn, workload, tasks, descriptor, warmup_cache, isverbose)
        self.__kcentroids   = 25 
        

    def predict(self):
        workload = 0
        
        print('[INFO]: assign', str(self.sizeof),'tasks for ',str(self.conn.nworkers),' worker(s)') if self.isverbose else None
        
        t1 = time.time()
        workload += self.warmup_cache()
        self.metrics['schell_warmup_cache'] = time.time() - t1  

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
    
    def __init__(self, conn:NetworkWrapper, workload:WorkloadWrrapper, tasks, descriptor, warmup_cache=0, isverbose=True):
        super(NNSCHELLFORALL, self).__init__(conn, workload, tasks, descriptor, warmup_cache, isverbose)
        
    def predict(self):
        workload = 0
        
        print('[INFO]: assign', str(self.sizeof),'tasks for ',str(self.conn.nworkers),' worker(s)') if self.isverbose else None
        
        t1 = time.time()
        workload += self.warmup_cache()
        self.metrics['schell_warmup_cache'] = time.time() - t1  

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
