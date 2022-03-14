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

from collections import OrderedDict
from containers import constants 

class Cache:

    def __init__(self, wid, capacity=0):
        self.wid                = wid
        self.cache              = OrderedDict()
        self.times              = {'cache': 0}
        self.hits               = 0
        self.missing            = 0
        self.time               = 0
        self.capacity_in_bytes  = 0.0
        self.max_capacity       = float(constants.MEMORY_UNIT * capacity)
        print("[INFO]: cache start with size of ", self.max_capacity, " Bytes")

        #used to compose metrics investigation 
        self.task_cache         = set()
        self.produced_rules     = []
        self.discard_rules      = [] 
        self.used_rules         = []
        self.memory_reused      = {}
        self.memory_needed      = {}

    def get_hits(self):
        return self.hits

    def get_missing(self):
        return self.missing 
           
    def get_cache_time(self):
        return self.times
        
    def add_capacity_in_bytes(self, memory):
        self.capacity_in_bytes += memory

    def sub_capacity_in_bytes(self, memory):
        self.capacity_in_bytes -= memory
        
    def get_capacity_in_bytes(self):
        return self.capacity_in_bytes
    
    def get_task_rules(self):
        tmp = self.task_cache
        self.task_cache = set()
        return tmp

    def clear(self):
        self.cache.clear()
        self.capacity_in_bytes  = 0
        self.clear_evaluations()
    
    def add_produced_rule(self, rule):
        self.produced_rules.append(rule)
    
    def add_memory_reused(self, memory, depth):
        if depth not in self.memory_reused:
            self.memory_reused[depth] = [0, 0]
        self.memory_reused[depth][0] += 1
        self.memory_reused[depth][1] += memory
    
    def add_memory_needed(self, memory, depth):
        if depth not in self.memory_needed:
            self.memory_needed[depth] = [0, 0]
        self.memory_needed[depth][0] += 1
        self.memory_needed[depth][1] += memory

    def add_discard(self, rule):
        self.discard_rules.append(rule)
    
    def add_used_rules(self, rule):
        self.used_rules.append(rule)
    
    def clear_evaluations(self):
        self.discard_rules      = []
        self.used_rules         = []
        self.produced_rules     = []
        self.memory_reused      = {}
        self.memory_needed      = {}
        
        
    def get_discards(self):
        discard           = (set(self.discard_rules) - set(self.used_rules))
        premature_discard = discard & set(self.produced_rules)
        return (len(premature_discard), len(discard), len(self.used_rules), self.memory_reused, self.memory_needed)
        
    def size(self):
        return len(self.cache)
    
    def size_in_bytes(self):
        return self.capacity_in_bytes
    
    def iscached(self, key):
        return True if key in self.cache else False

    def get(self, key, depth=0):
        raise NotImplementedError("[ERROR]: this method is not implemented correctless")

    def set(self, key, value, memory=0, depth=0):
        raise NotImplementedError("[ERROR]: this method is not implemented correctless")
    
    
    
    
    
    
    