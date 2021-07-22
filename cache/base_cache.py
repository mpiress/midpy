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
from utils import dump, load
from cache import cache_path


from collections import OrderedDict
import os, sys


class Cache:

    def __init__(self, wid, capacity=0):
        self.wid                = wid
        self.capacity           = capacity
        self.cache              = OrderedDict()
        self.times              = {'cache': 0}
        self.hits               = 0
        self.missing            = 0
        self.time               = 0
        
        #used to compose metrics investigation 
        self.task_cache         = set()
        self.produced_rules     = []
        self.discard_rules      = [] 
        self.used_rules         = []
        
    def get_hits(self):
        return self.hits

    def get_missing(self):
        return self.missing 
           
    def set_number_of_tasks(self, workload):
        if workload == self.k:
            self.capacity = len(self.cache)
        
    def get_cache_time(self):
        return self.times
        
    def get_capacity(self):
        return self.capacity

    def get_capacity_in_bytes(self):
        return sys.getsizeof(self.cache)
    
    def get_task_rules(self):
        tmp = self.task_cache
        self.task_cache = set()
        return tmp

    def set_capacity(self, capacity):
        self.capacity = capacity
        
    def clear(self):
        self.cache.clear()
    
    def add_produced_rule(self, rule):
        self.produced_rules.append(rule)

    def add_discard(self, rule):
        self.discard_rules.append(rule)
    
    def add_used_rules(self, rule):
        self.used_rules.append(rule)
    
    def clear_evaluations(self):
        self.discard_rules = []
        self.used_rules = []
        self.produced_rules = []
        
    def get_discards(self):
        discard           = (set(self.discard_rules) - set(self.used_rules))
        premature_discard = discard & set(self.produced_rules)
        return (len(premature_discard), len(discard), len(self.used_rules))
        
    def size(self):
        return len(self.cache)

    def get_keys(self):
        return self.cache.keys()
        
    def get(self, key, tid):
        raise NotImplementedError("[ERROR]: this method is not implemented correctless")

    def set(self, key, value, tid):
        raise NotImplementedError("[ERROR]: this method is not implemented correctless")
    
    
    
    
    
    
    