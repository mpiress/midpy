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

class LRU(Cache):

    def __init__(self, wid, capacity=0):
        super(LRU, self).__init__(wid, capacity)
        self.__isverbose = True
        
    def get(self, key):
        if self.capacity > 0:
            try:
                t1 = time.time()
                v = self.cache[key]
                self.cache.move_to_end(key, last=False)
                self.add_used_rules(key)
                self.task_cache.add(key)
                self.hits += 1
                self.time += (time.time() - t1)
                return v
            except:
                return -1
        return -1    

    def set(self, key, value):
        
        t1 = time.time()
        self.task_cache.add(key)
        
        if self.capacity > 0:
            self.add_produced_rule(key)

            if not self.lock:
                self.cache[key] = value
                self.cache.move_to_end(key, last=False)

            else:
                discard = self.cache.popitem(last=True)
                self.add_discard(discard[0])
                self.cache[key] = value
                self.cache.move_to_end(key, last=False)
                if self.__isverbose:
                    print('[INFO]: maximum cache space in memory:', self.get_capacity_in_bytes())
                    print('[INFO]: maximum cache space in rules quantity:', self.size())
                    self.__isverbose = False
            self.missing += 1
        self.time += (time.time() - t1)
                
    
    
                    
