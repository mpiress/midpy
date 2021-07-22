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
from itertools import combinations
from lac import C_LAC

import time

class LAC(BaseWorkerInfo):

    def __init__(self, path, maxrule=1, minsup=0, minconf=0):
        self.__maxrule = maxrule
        self.__clac    = C_LAC(minsup, minconf, path)
        self.__clac.preprocessing()

    def execute_task(self, task):
        result = 0
        
        #task = enumerate(task[0:-1])
        #task = [str(t) for t in enumerate(task[0:-1])]
        keys = []
        for i in range(len(task[0:-1])):
            aux = "(" + str(i) + "," + str(task[i]) + ")"
            keys.append(aux)
        
        task = self.__clac.get_itemset(keys)
        
        combination = []
        for size in range(1,self.__maxrule+1):
            for c in combinations(task, size):
                value = " "
                for x in c:
                    value = value + x + " "
                combination.append(value)
        
        tx = time.time()
        score = {}
        for c in combination:
            rule = self.cache.get(c)
            if rule == -1:
                rule = self.__clac.execute_task([c])
                self.cache.set(c, rule)
            for c, v in rule.items():
                score[c] = [score[c][0] + v[0], score[c][1] + v[1]] if c in score else [v[0], v[1]] 
        self.times['generate_rules'] = time.time() - tx if 'generate_rules' not in self.times else (self.times['generate_rules'] + (time.time() - tx))           
        
        result = max(score.items(), key=lambda item:item[1][1])         
        
        return result
        

        