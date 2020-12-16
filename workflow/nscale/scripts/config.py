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
from schedulers.basedrn.nnschell import NNSCHELLBYKCLUSTERS

from cache.replacement_policies.lru import LRU

from applications.nscale.nscale import NSCALE

class config:
    
    BASE_FILE_NAME          = 'nscale'
    PATH_DATASET            = '../../../datasets/nscale/'

    TRAIN_NEURAL_NETWORK    = False
    
    TEST                    = PATH_DATASET+BASE_FILE_NAME+'.test'
    TRAIN                   = PATH_DATASET+BASE_FILE_NAME+'.train'
    OUTPUT_PATH             = 'results/'
    
    SIZE_OF_CHUNK           = [16, 64, 256, 1024]
    SCHEDULERS              = [NNSCHELLBYKCLUSTERS]
    MOD_OR_DIV_SCHELL       = constants.DIV

    CACHE_TYPE              = [LRU]
    CACHE_FULL_SIZE         = 8439
    CACHE_CAPACITY          = [0.25, 0.5, 1.0, 1.25]
    
    SERVER_PORT             = 32010
    NWORKERS                = 1

    @staticmethod
    def get_job():
        job = NSCALE('/home/michel/Doutorado/datasets/nscale/imgs/image1.png', '/home/michel/Doutorado/datasets/nscale/imgs/output.png')
        return job
