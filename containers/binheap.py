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

import heapq

class BinHeap():

    def __init__(self, maxk):
        self.__heap = []
        self.__size = 0
        self.__maxk = maxk

    def pop(self):
        assert self.__size > 0, '[ERROR]: heap is empty'
        item = heapq.heappop(self.__heap)
        self.__size -= 1
        return item

    def push(self, label, value):
        
        if self.__size < self.__maxk:
            heapq.heappush(self.__heap, (value, label))
            self.__size += 1
        else:
            lim = heapq.nlargest(1, self.__heap)[0]
            if (value < lim[0]):
                self.__heap.remove(heapq.nlargest(1, self.__heap)[0])
                heapq.heappush(self.__heap, (value, label))


    def addn_label_range(self, n, label0, values):
        i = 0
        while (i < n):
            self.push(label0+i, values[i])
            i+= 1

    def get_n_items(self, n):
        return [self.pop() for _ in range(n)]









