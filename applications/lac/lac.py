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

import time

class LAC(BaseWorkerInfo):

    def __init__(self, train, maxrule=1, minsup=0, minconf=0):
        self.__maxrule          = maxrule
        self.__minsup           = minsup
        self.__minconf          = minconf
        self.__classes          = {}
        self.__features         = {}
        self.size_of_train      = 0
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
                self.__classes[key] = {index}
            else:
                self.__classes[key].add(index)
            
            for key in line[0:-1]:
                key = str(key)
                if key not in self.__features:
                    self.__features[key] = {index}
                else:
                    self.__features[key].add(index)
            print('[INFO] Load training data:', int(100*index/self.size_of_train),'%', end="\r")
        
        #for k in self.__classes:
        #    self.__classes[k] = sorted(self.__classes[k])
        #for k in self.__features:
        #    self.__features[k] = sorted(self.__features[k])

        print("NUMERO DE FEATURES: " , len(self.__features))
        



    def intersection(self, lst1, lst2):
        lst3 = []
        temp1 = set(lst2) if len(lst1) < len(lst2) else set(lst1)
        temp2 = lst1 if len(lst1) < len(lst2) else lst2
        lst3 = [value for value in temp2 if value in temp1]
        return lst3

    def __getRules(self, combination):
        rules     = {}
        score     = {}
        notcached = []
        
        txx = time.time()
        for c in combination:
            rule = self.cache.get(c)
            if rule == -1:
                notcached.append(c)
            else:
                for c, v in rule.items():
                    score[c] = [score[c][0] + v[0], score[c][1] + v[1]] if c in score else [v[0], v[1]]
        
        del(combination)
        
        tx1 = 0
        tx = time.time()
        for rule in notcached:
            
            aux = [self.__features[k] for k in rule]
            l1 = set.intersection(*aux)
            
            if l1:
                sizeof = len(l1)
                aux = [(c, len(l1.intersection(t))) for c, t in self.__classes.items()]
                eval = {}
                for c, value in aux:
                    if value > 0:
                        sup = value/self.size_of_train
                        if sup >= self.__minsup:
                            conf = value/sizeof
                            if conf >= self.__minconf:
                                eval[c] = [sup, conf]
                                score[c] = [score[c][0] + sup, score[c][1] + conf] if c in score else [sup, conf]
                
                if eval:
                    self.cache.set(rule, eval)
                        
        self.times['generate_rules'] = time.time() - tx if 'generate_rules' not in self.times else (self.times['generate_rules'] + (time.time() - tx))           
        
        #if you have that return results, using variable c
        c = max(score.items(), key=lambda item:item[1][1]) 
        
        return c
        

    def execute_task(self, task):
        result = 0
        itemset = []
        
        task = [str(x) for x in enumerate(task[0:-1])]
        for k in task:
            if k in self.__features:
                itemset.append(k)
        
        if len(itemset) > 0:
            combination = []
            for size in range(1,self.__maxrule+1):
                combination += list(combinations(itemset, size))
            
            t1 = time.time()
            result = self.__getRules(combination)
            self.times['function_get_rules'] = time.time() - t1 if 'function_get_rules' not in self.times else self.times['function_get_rules'] + (time.time() - t1)
            
        
        return result
        

        