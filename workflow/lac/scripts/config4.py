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

from containers import constants

from schedulers.basedrn.nnschell_RR import NNSCHELLBYSIGNATURE5B
from cache.replacement_policies.lru import LRU
from applications.lac.lac import LAC

class config:
    
    BASE_FILE_NAME          = 'lac'
    PATH_DATASET            = '../../../datasets/census/'

    TRAIN_NEURAL_NETWORK    = False
    
    TEST                    = PATH_DATASET+'census.test'
    TRAIN                   = PATH_DATASET+'census.train'
    WARMUP                  = PATH_DATASET+'census.warmup'
    OUTPUT_PATH             = '../../../tmp/'
    
    SIZE_OF_CHUNK           = [2160] 
    SIZE_OF_BUCKET          = 5
    SCHEDULERS              = [NNSCHELLBYSIGNATURE5B]
    
    CACHE_TYPE              = [LRU]
    CACHE_CAPACITY          = [1.75, 2.0, 2.25, 2.5]
    CACHE_SIG_SIZE          = 1 
    
    SERVER_PORT             = 32000
    NWORKERS                = 1
    WPOOL                   = 1

    def get_job(self):
        self.__job = LAC(config.TRAIN, 5, 0, 0)
        return self.__job
