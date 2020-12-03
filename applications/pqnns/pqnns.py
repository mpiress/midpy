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

#pymid imports
import applications
from core.managers.worker import BaseWorkerInfo
import time 

#internal imports
from applications.pqnns.pq_new import pq_new
from applications.pqnns.pq_assign import pq_assign
from applications.pqnns.pq_search_geoge import pq_search


BASED_PATH = '/Users/michel/Dropbox/Doutorado/datasets/siftsmall/'
BASE = BASED_PATH + 'base.fvecs'

class PQNNS(BaseWorkerInfo):

    def __init__(self, train, k=20, m=8):
        super(PQNNS, self).__init__()
        self.__k            = k
        self.__codebook     = None
        self.__pq           = None
        self.__preprocessing(train, m)   
        
    def __preprocessing(self, train, m):
        global BASE

        self.__pq = applications.load_buffer('pq.pkl')
        if not self.__pq:
            print('[INFO]: producing the pq dataset for the experiments ...')
            self.__pq = pq_new(train, m)
            applications.dump_buffer('pq.pkl', self.__pq)

        self.__codebook = applications.load_buffer('codebook.pkl')
        if not self.__codebook:
            print('[INFO]: generating the codebook ...')
            self.__codebook = pq_assign(BASE, self.__pq)
            applications.dump_buffer('codebook.pkl', self.__codebook)
    
    
    def execute_task(self, task):
        t1 = time.time()
        result = pq_search(self.__pq, self.__codebook, self.cache, task, self.__k, self.times)
        self.times['function_get_rules'] = time.time() - t1 if 'function_get_rules' not in self.times else self.times['function_get_rules'] + (time.time() - t1)
        
        self.info_cache['hits'] += result[0]
        self.info_cache['missing'] += result[1]
        return result  
        
        
