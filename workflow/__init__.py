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
import workflow
from containers import constants
from containers.wrapper.wrappers import NetworkWrapper, SchedulerWrapper, WorkloadWrrapper, CacheWrapper

from cache.replacement_policies.fifo import FIFO
from core import WorkflowManager

from schedulers.batch.round_robin import RoundRobin

import socket, os, math, shutil

__local_path__ = workflow.__path__[0] + os.sep

connection = NetworkWrapper()
scheduler = SchedulerWrapper()
workload = WorkloadWrrapper()
cache = CacheWrapper()
       
def get_local_path():
    return __local_path__

###############################################################################################################
#                                            NETWORK ASSIGNMENTS                                              #
###############################################################################################################
def network_wrapper(port=32001, nworkers=1):
    global connection
    connection.port             = port
    connection.nworkers         = nworkers
    

###############################################################################################################
#                                            SCHEDULER ASSIGNMENTS                                            #
###############################################################################################################
def scheduller_wrapper(schell=None):
    global scheduler
    assert schell, '[ERROR]: similarity metric is not defined'
    scheduler.type_scheduler = schell
    

###############################################################################################################
#                                            WORKLOAD ASSIGNMENTS                                             #
###############################################################################################################
def workload_wrapper(chunk=1, train=False, job_name=None):
    global workload
    assert chunk > 0, '[ERROR]: chunk must be greater than or equal to 1'
    workload.overview['chunk']      = chunk
    workload.train_neural_network   = train
    workload.job_name               = job_name

    

###############################################################################################################
#                                            CACHE ASSIGNMENTS                                                #
###############################################################################################################
def cache_wrapper(capacity=0, percent=0, policy=None):
    global cache
    assert policy, '[ERROR]: cache maintenance policy is not defined'
    cache.capacity    = capacity
    cache.type_cache  = policy
    cache.percent     = percent
    


###############################################################################################################
#                                           WORKFLOW INITIALIZATION                                           #
###############################################################################################################
def shutdown_server_name(workflow):
    workflow.shutdown_server_name()
    

def start_workflow_master(config, descriptor):
    global connection, scheduler, workload, cache
    workflow = WorkflowManager()
                    
    assert config.OUTPUT_PATH, '[ERROR]: output is not defined correctly'
    
    ip = socket.gethostbyname(socket.getfqdn())
    connection.server = ip
    network_wrapper(config.SERVER_PORT, config.NWORKERS)
    
    with open(constants.BUFFER+'server.csv', 'w') as file:
        file.write(ip)
   
    file = '/var/tmp/'+config.BASE_FILE_NAME+'_'+config.TEST[config.TEST.rfind('/')+1:]
    if os.path.isfile(file):
        os.remove(file)
    if not os.path.isfile(file):
        shutil.copyfile(config.TEST, file)
    config.TEST = file

    for cache_type in config.CACHE_TYPE:
        for schel in config.SCHEDULERS:
            for chunk in config.SIZE_OF_CHUNK:
                for capacity in config.CACHE_CAPACITY:
                    capacity = capacity if capacity >= 0 else 0
                    
                    if constants.VERBOSEMODE:
                        print('================================================================================================')
                        print('Starting the cache '+cache_type.__name__.lower()+' with '+str(capacity)+'% and '+schel.__name__.lower()+' metric')
                        print('================================================================================================')
                    workload_wrapper(chunk, config.TRAIN_NEURAL_NETWORK, config.BASE_FILE_NAME)
                    scheduller_wrapper(schel)
                    mod = '#div' if config.MOD_OR_DIV_SCHELL else '#mod' 
                    output_path = [config.OUTPUT_PATH+config.BASE_FILE_NAME+'_'+cache_type.__name__.lower()+'_'+str(config.NWORKERS)+'_'+mod+'.csv', str(capacity)]
                    workflow.taskmanager_init(connection, workload, scheduler, descriptor, output_path, constants.VERBOSEMODE)
                
    shutdown_server_name(workflow)

    return True


def start_workflow_worker(config, descriptor=None):
    global connection, workload, cache
    workflow = WorkflowManager()
                    
    ip = socket.gethostbyname(socket.getfqdn())
    network_wrapper(config.SERVER_PORT, config.NWORKERS)
    print('[INFO]: local IP ', ip) if constants.VERBOSEMODE else None
    
    print('[INFO]: Waiting start the job ...') if constants.VERBOSEMODE else None
    job = config.get_job()
    assert job, '[ERROR]: the job is not defined correctly'
    
    for cache_type in config.CACHE_TYPE:
        for schel in config.SCHEDULERS:
            for chunk in config.SIZE_OF_CHUNK:
                for capacity in config.CACHE_CAPACITY:
                    
                    if constants.VERBOSEMODE:
                        print('================================================================================================')
                        print('Starting the cache '+cache_type.__name__.lower()+' with '+str(capacity)+'% and '+schel.__name__.lower()+' scheduller')
                        print('================================================================================================')
                    cache_size = math.ceil((config.CACHE_FULL_SIZE/config.NWORKERS)*capacity/100) if capacity >= 0 else -1
                    workload_wrapper(chunk, config.TRAIN_NEURAL_NETWORK, config.BASE_FILE_NAME)
                    cache_wrapper(cache_size, capacity, cache_type)
                    workflow.workerpool_init(job, connection, workload, cache, schel.__name__.lower(), descriptor, config.OUTPUT_PATH, constants.VERBOSEMODE)
    
    return True
