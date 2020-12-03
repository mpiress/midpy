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
from cache.replacement_policies.fifo import FIFO

from applications.lac.lac import LAC

class config:
    """!
        @brief Constructor used by the framework to configure the application execution
        @details Initializes variables to conduct the application's execution process and data manipulation
        
        @param[in] TEST: a point of reference to the test's data set
        @param[in] TRAIN: a point of reference to the train's data set   
        @param[in] OUTPUT_PATH: a point of reference to the output file on storage
        @param[in] BUFFER: a point of reference to the server ip file on storage
        @param[in] PATTERNS: define (sizeof_chunk, sizeof_dataset, tag_file_result)
        @param[in] MOD_OR_DIV: define if the chunks are distributed in MOD or DIV mode
        @param[in] METRICS: define scheduler strategies for execution
        @param[in] CACHE_TYPE: replacement_policies 
        @param[in] CACHE_FULL_SIZE: number of entries for 100% cache size 
        @param[in] CACHE_CAPACITY: percentage of rules cached
        @param[in] AUTHKEY: the security key used to transactions between master and workers
        @param[in] SERVER_PORT: port used to start communication between master / workers
        @param[in] NWORKERS: number of workers running on the experiment
        @param[in] GID: applied to compose remote object names
        @param[in] JOB: composes part of name of result file        
        @see __init__.py (workflow package), base_master and base_worker
    """
    
    ISVERBOSE       = True
    
    TEST            = '../../../../datasets/census/census_small.testing'
    TRAIN           = '../../../../datasets/census/census.train'
    OUTPUT_PATH     = '/Users/michel/Dropbox/Doutorado/workspace/experimentos/PassoBase/'
    BUFFER          = '/Users/michel/Dropbox/Doutorado/workspace/MidPy/workflow/buffer/'
    
    PATTERNS        = [100]
    MOD_OR_DIV      = constants.DIV
    
    METRICS         = [NeighborhoodRank]
    
    CACHE_TYPE      = [LRU]
    CACHE_FULL_SIZE = 344852 #993689 para 500 #6894146 para 10000
    CACHE_CAPACITY  = [0.5, 0.75, 1.0, 1.25]
    
    AUTHKEY         = 'Doutorado'
    SERVER_PORT     = 32000
    NWORKERS        = 1
    
    GID             = 'full'  
    JOB             = 'lac' 
    
    @staticmethod
    def get_job():
        job = LAC(config.TRAIN, 3, 0, 0)
        return job
