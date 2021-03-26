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

from schedulers.batch.round_robin import RoundRobin
from schedulers.batch.feature_rank import FeatureRank
from schedulers.batch.neighbourhood_rank import NeighborhoodRank
from schedulers.batch.kmeans_rank import KMeansRank
from schedulers.basedrn.nnschell import NNSCHELLBYKCLUSTERS, NNSCHELLFORALL, NNSCHELLBYSIGNATURE

from cache.replacement_policies.lru import LRU
 
from applications.lac.lac2 import LAC

class config:
    
    BASE_FILE_NAME          = 'lac'
    PATH_DATASET            = '../../../datasets/census/'

    TRAIN_NEURAL_NETWORK    = False
    
    TEST                    = PATH_DATASET+'census_40.test'
    TRAIN                   = PATH_DATASET+'census.train'
    OUTPUT_PATH             = '../../../tmp/'
    
    SIZE_OF_CHUNK           = [40] #[16, 64, 256, 1024]
    SCHEDULERS              = [NNSCHELLBYKCLUSTERS, NNSCHELLBYSIGNATURE] #[RoundRobin, NNSCHELLBYKCLUSTERS, NNSCHELLBYSIGNATURE, NNSCHELLFORALL]
    MOD_OR_DIV_SCHELL       = constants.DIV

    CACHE_TYPE              = [LRU]
    CACHE_FULL_SIZE         = 179663 
    CACHE_CAPACITY          = [0.75] #[0.75, 1.0, 1.25, 1.5]
    CACHE_DIV_WORKERS       = False

    SERVER_PORT             = 32010
    NWORKERS                = 1

    def get_job(self):
        self.__job = LAC(config.TRAIN, 3, 0, 0)
        return self.__job
