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

from cache.base_cache import Cache
import time

class FIFO(Cache):

    def __init__(self, wid, capacity=0):
        super(FIFO, self).__init__(wid, capacity)
        self.__isverbose = True
        
    def get(self, key, depth=0):
        if self.max_capacity > 0:
            try:
                t1 = time.time()
                v = self.cache[key]
                self.add_used_rules(key)
                self.add_memory_reused(v[1])
                self.add_depth_param_reused(depth)
                self.task_cache.add(key)
                self.hits += 1
                self.time += (time.time() - t1)
                return v[0]
            except:
                return -1
        return -1    

    def set(self, key, value, memory=0, depth=0):
        
        t1 = time.time()
        self.task_cache.add(key)
        self.add_memory_needed(memory)
        self.add_depth_param_needed(depth)
        
        if self.max_capacity > 0:
            self.add_produced_rule(key)

            if (self.capacity_in_bytes + memory) < self.max_capacity:
                self.cache[key] = (value, memory)
                self.add_capacity_in_bytes(memory)

            else:
                
                discard = self.cache.popitem()
                self.add_discard(discard[0])
                self.sub_capacity_in_bytes(discard[1][1])

                while (self.capacity_in_bytes + memory) > self.max_capacity:
                    discard = self.cache.popitem()
                    self.add_discard(discard[0])
                    self.sub_capacity_in_bytes(discard[1][1])
                
                self.cache[key] = (value, memory)
                self.add_capacity_in_bytes(memory)

            self.missing += 1
        self.time += (time.time() - t1)