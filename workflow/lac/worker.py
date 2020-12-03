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
import math, os, sys
from containers import constants

path = os.getcwd()
path = path[0:path.find('MidPy') + 5]
sys.path.append(path)


from workflow import network_wrapper, workload_wrapper, cache_wrapper, start_workflow_worker
from workflow.lac.config import config

def parameterization(cache_policy, cache_size, cache_percentage, chunk, metric_name):
    network_wrapper(config.AUTHKEY, config.SERVER_PORT, config.NWORKERS, config.GID, config.BUFFER)
    workload_wrapper(chunk, config.TEST, 'queries', config.MOD_OR_DIV)
    cache_wrapper(cache_size, cache_policy, cache_percentage, metric_name)


def run():
    
    print('[INFO]: waiting for configuration files to define patterns and cache size') if constants.VERBOSEMODE else None
    job = config.get_job()
    
    for cache in config.CACHE_TYPE:
        for m in config.METRICS:
            for p in config.SIZE_OF_CHUNK:
                for s in config.CACHE_CAPACITY:
                    if constants.VERBOSEMODE:
                        print('================================================================================================')
                        print('Starting the cache '+cache.__name__.lower()+' with '+str(s)+'% and '+m.__name__.lower()+' metric')
                        print('================================================================================================')
                    cache_size = math.ceil((config.CACHE_FULL_SIZE/config.NWORKERS)*s/100) if s >= 0 else -1
                    parameterization(cache, cache_size, s, p, m.__name__.lower())
                    start_workflow_worker(job, config)
                                        

if __name__ == '__main__':
    run()
    exit(0)

