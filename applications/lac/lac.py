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

from core.managers.worker import BaseWorkerInfo
from utils import read_file
from itertools import combinations

import time, sys

class LAC(BaseWorkerInfo):

    def __init__(self, train, maxrule=1, minsup=0, minconf=0):
        self.__maxrule          = maxrule
        self.__minsup           = minsup
        self.__minconf          = minconf
        self.__classes          = {}
        self.__features         = {}
        self.size_of_train      = 0
        self.tasks              = 0
        self.__preprocessing(train)

        
    def __preprocessing(self, train):
        data = []
        index = 0
        
        data = read_file(path=train, norm=False)
        self.size_of_train = data.shape[0]
        
        for index, line in enumerate(data.values):
            line = list(enumerate(line))
            
            key = str(line[-1])
            if key not in self.__classes:
                self.__classes[key] = [index]
            else:
                self.__classes[key].append(index)
            
            for key in line[0:-1]:
                key = str(key)
                if key not in self.__features:
                    self.__features[key] = [index]
                else:
                    self.__features[key].append(index)
            print('[INFO] Load training data:', int(100*index/self.size_of_train),'%', end="\r")
        
        print()
        print("NUMERO DE FEATURES: " , len(self.__features))
        print("NUMERO DE CLASSES : " , len(self.__classes))
        

    
    def __get__support_and_confidence(self, classes, sizeof):
        keys = list(classes.keys())
        memory = 0
        
        for c in keys:
            value = len(classes[c][2])
            sup = value/self.size_of_train
            if sup >= self.__minsup:
                conf = value/sizeof
                if conf >= self.__minconf:
                    classes[c] = [sup, conf, classes[c][2]]
                    memory += sys.getsizeof(sup)
                    memory += sys.getsizeof(conf)
                    memory += sys.getsizeof(classes[c][2])
        
        return memory
        

    def __get_matches(self, rule):
        matched    = {}
        sizeof     = len(rule)
        matchsize  = sizeof - 1 if (sizeof - 1) > 0 else 0
        reuse      = []
        task       = []

        while(len(matched) < sizeof and matchsize > 1):
        #if (matchsize > 1):
            tmp = list(combinations(rule, matchsize))
            while(len(matched) < sizeof and tmp):
                idx = tmp.pop(0)
                if self.cache.iscached(idx):
                    for f in idx:
                        if f not in matched:
                            matched[f] = idx
            matchsize = matchsize - 1 
        
        for r in rule:
            if r in matched:
                reuse.append(matched[r])
            else:
                task.append(r)
        
        return reuse, task



    def __getRules(self, combination, score):
        task_memory = 0
        memory = 0

        tx = time.time()
        for rule in combination:
            
            #step 1: find a same rule in the cache
            classes = self.cache.get(rule, len(rule))
            classes = classes[1] if classes != -1 else classes 

            if classes == -1:

                classes = {}
                features = set()
                memory = 0

                #step 2: find segment rules 
                reuse, task  = self.__get_matches(rule)
                #reuse = []
                #task = rule
                #step 2.1: process reuse into segment rules
                if reuse:
                    reuse = list(set(reuse))
                    idx = reuse.pop(0)
                    features, classes = self.cache.get(idx, len(idx))
                    features = set(features)
                    classes = {c:[0,0, set(classes[c][2])] for c in classes}
                    while reuse and features and classes:
                        idx = reuse.pop(0)
                        f, c = self.cache.get(idx, len(idx))
                        features = features.intersection(f)
                        keys = set(classes.keys()).intersection(set(c.keys()))
                        classes  = {k:[0,0,classes[k][2].intersection(c[k][2])] for k in keys}
                        classes = {c:classes[c] for c in classes if len(classes[c][2]) > 0}
                
                    reuse = True
                else:
                    reuse = False

                #step 2.2: evaluate task, i.e., rules not found into the cache
                if task:
                    
                    if reuse and features and classes:
                        l2 = [set(self.__features[idx]) for idx in task]
                        features = features.intersection(*l2)
                        classes = {c:[0,0, features.intersection(classes[c][2])] for c in classes.keys()}
                        classes = {c:classes[c] for c in classes if len(classes[c][2]) > 0}
                        
                    elif not reuse:
                        l2 = [set(self.__features[idx]) for idx in task]
                        features = set.intersection(*l2)
                        if features: 
                            classes = {c:[0,0, features.intersection(val)] for c, val in self.__classes.items()}
                            classes = {c:classes[c] for c in classes if len(classes[c][2]) > 0}
                    
                if features and classes:
                    features = list(features)
                    classes = {c:[0,0,list(classes[c][2])] for c in classes}
                    memory += self.__get__support_and_confidence(classes, len(features))
                    memory += sys.getsizeof(features)
                else:
                    features = []
                    classes  = {}
                
                memory += sys.getsizeof(rule)
                self.cache.set(rule, (features, classes), memory, len(rule)) 
                
            for c in classes:
                score[c] = [score[c][0] + classes[c][0], score[c][1] + classes[c][1]] if c in score else [classes[c][0], classes[c][1]]  

            task_memory += memory    
        
        self.times['generate_rules'] = time.time() - tx if 'generate_rules' not in self.times else (self.times['generate_rules'] + (time.time() - tx))           
        
        #if you have that return results, using variable c
        c = max(score.items(), key=lambda item:item[1][1]) if score else None
        
        return c, task_memory
        

    def execute_task(self, task):
        result = 0
        itemset = []
        score = {}
        
        task = [str(x) for x in enumerate(task[0:-1])]
        for k in task:
            if k in self.__features:
                itemset.append(k)
        
        if len(itemset) > 0:
            combination = []
            for size in range(1, self.__maxrule+1):
                combination += list(combinations(itemset, size))
            
            t1 = time.time()
            result, memory = self.__getRules(combination, score)
            self.times['function_get_rules'] = time.time() - t1 if 'function_get_rules' not in self.times else self.times['function_get_rules'] + (time.time() - t1)
            self.tasks += 1
            
        return result
        

        