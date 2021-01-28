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
from collections import OrderedDict, defaultdict

import time


class LAC(BaseWorkerInfo):

    def __init__(self, train, maxrule=1, minsup=0, minconf=0):
        super(LAC, self).__init__()
        self.__maxrule          = maxrule
        self.__minsup           = minsup
        self.__minconf          = minconf
        self.__classes          = {}
        self.__features         = {}
        self.size_of_train      = 0
        self.__preprocessing(train)
        
        
    def __preprocessing(self, train):
        
        data = read_file(path=train, norm=False)
        self.size_of_train = data.shape[0]
        
        for index, line in enumerate(data.values):
            line = list(enumerate(line))
            if line[-1] not in self.__classes:
                self.__classes[line[-1]] = [index]
            else:
                self.__classes[line[-1]].append(index)
            
            for key in line[0:-1]:
                if key not in self.__features:
                    self.__features[key] = [index]
                else:
                    self.__features[key].append(index)
            print('[INFO] Load training data:', int(100*index/self.size_of_train),'%', end="\r")
        
        for key in self.__features:
            self.__features[key] = set(self.__features[key])
        for key in self.__classes:
            self.__classes[key] = set(self.__classes[key])

    
    def __getRules(self, itemset, classe):
        hits = 0
        misses = 0
        rules = {}
        score = defaultdict()
        
        for size in range(1,self.__maxrule+1):
            
            combination = list(combinations(itemset.keys(), size))
            
            for c in combination:

                rule = self.cache.get(c)
                
                if rule == -1:
                    tx = time.time()
                    tc2 = 0
                    rule = c
                    aux = itemset[rule[0]]
                    if len(rule) >= 2:
                        for k in rule[1:]:
                            aux = aux & itemset[k]
                    
                    if bool(aux):
                        for c,t in self.__classes.items():
                            aux_c = aux & t
                            if len(aux_c) > 0:
                                sup = len(aux_c)/self.size_of_train
                                if sup >= self.__minsup:
                                    conf = len(aux_c)/len(aux)
                                    if conf >= self.__minconf:
                                        if rule not in rules:
                                            rules[rule] = {}
                                        rules[rule][c] = [sup, conf]
                                        score[c] = [score[c][0] + sup, score[c][1] + conf] if c in score else [sup, conf]
                        
                        if (rule in rules):
                            misses += 1
                            self.cache.set(rule, rules[rule])

                    self.times['generate_rules'] = time.time() - tx if 'generate_rules' not in self.times else (self.times['generate_rules'] + (time.time() - tx))           
                        
                else:
                    hits += 1
                    for c,v in rule.items():
                        score[c] = [score[c][0] + v[0], score[c][1] + v[1]] if c in score else [v[0], v[1]]
                    
        #if you have that return results, using variable c
        c = max(score.items(), key=lambda item:item[1][1]) 
        
        return [hits, misses]
        

    def execute_task(self, task):
        hits, missing = [0,0]
        itemset = OrderedDict()
        
        task, classe = list(enumerate(task[0:-1])), task[-1]
        
        for k in task:
            if k in self.__features:
                itemset[k] = self.__features[k]
                
        if len(itemset) > 0:

            t1 = time.time()
            hits, missing = self.__getRules(itemset, classe)
            self.times['function_get_rules'] = time.time() - t1 if 'function_get_rules' not in self.times else self.times['function_get_rules'] + (time.time() - t1)
            
        #self.info_cache['hits'] += hits
        #self.info_cache['missing'] += missing
                                        
        return [hits, missing]
        

        