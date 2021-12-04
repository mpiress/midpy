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

def get_local_path():
    return __local_path__

class WorkflowInitialize:

    def __init__(self):
        self.connection = NetworkWrapper()
        self.scheduler  = SchedulerWrapper()
        self.workload   = WorkloadWrrapper()
        self.cache      = CacheWrapper()
        self.workflow   = None
        
    ###############################################################################################################
    #                                            NETWORK ASSIGNMENTS                                              #
    ###############################################################################################################
    def get_network_wrapper(self):
        return self.connection
    
    def set_network_wrapper(self, port=32001, nworkers=1, wpool=1):
        self.connection.port             = port
        self.connection.nworkers         = nworkers
        self.connection.wpool            = wpool
        

    ###############################################################################################################
    #                                            SCHEDULER ASSIGNMENTS                                            #
    ###############################################################################################################
    def get_scheduller_wrapper(self):
        return self.scheduler

    def set_scheduller_wrapper(self, schell=None):
        assert schell, '[ERROR]: similarity metric is not defined'
        self.scheduler.type_scheduler = schell
        

    ###############################################################################################################
    #                                            WORKLOAD ASSIGNMENTS                                             #
    ###############################################################################################################
    def get_workload_wrapper(self):
        return self.workload

    def set_workload_wrapper(self, chunk=1, bucket=1, train=False, job_name=None):
        assert chunk > 0, '[ERROR]: chunk must be greater than or equal to 1'
        self.workload.overview['chunk']      = chunk
        self.workload.overview['bucket']     = bucket
        self.workload.train_neural_network   = train
        self.workload.job_name               = job_name

        

    ###############################################################################################################
    #                                            CACHE ASSIGNMENTS                                                #
    ###############################################################################################################
    def get_cache_wrapper(self):
        return self.cache

    def set_cache_wrapper(self, policy=None, capacity=0):
        assert policy, '[ERROR]: cache maintenance policy is not defined'
        self.cache.type_cache  = policy
        self.cache.capacity    = capacity
        

    ###############################################################################################################
    #                                           WORKFLOW INITIALIZATION                                           #
    ###############################################################################################################

    def start_workflow_master(self, config, descriptor):
        self.workflow = WorkflowManager()
                        
        assert config.OUTPUT_PATH, '[ERROR]: output is not defined correctly'
        
        ip = socket.gethostbyname(socket.getfqdn())
        self.connection.server = ip
        self.set_network_wrapper(config.SERVER_PORT, config.NWORKERS, config.WPOOL)
        
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
                        if constants.VERBOSEMODE:
                            print('================================================================================================')
                            print('Starting the cache '+cache_type.__name__.lower()+' with '+str(capacity)+' tasks cached and '+schel.__name__.lower()+' metric')
                            print('================================================================================================')
                        self.set_workload_wrapper(chunk, config.SIZE_OF_BUCKET, config.TRAIN_NEURAL_NETWORK, config.BASE_FILE_NAME)
                        self.set_scheduller_wrapper(schel)
                        mod = '#div' if config.MOD_OR_DIV_SCHELL else '#mod' 
                        output_path = [config.OUTPUT_PATH+config.BASE_FILE_NAME+'_'+cache_type.__name__.lower()+'_'+str(config.NWORKERS)+'_'+mod+'.csv', str(capacity)]
                        execution_id = (cache_type.__name__.lower(), schel.__name__.lower(), chunk, capacity)
                        self.workflow.taskmanager_init(self.connection, self.workload, self.scheduler, descriptor, output_path, execution_id, constants.VERBOSEMODE)
                    
        self.workflow.shutdown_server_name(self.connection)
        

        return True


    def start_workflow_worker(self, config, descriptor=None):
        self.workflow = WorkflowManager()
                        
        ip = socket.gethostbyname(socket.getfqdn())
        self.set_network_wrapper(config.SERVER_PORT, config.NWORKERS)
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
                            print('Starting the cache '+cache_type.__name__.lower()+' with '+str(capacity)+' tasks cached and '+schel.__name__.lower()+' scheduller')
                            print('================================================================================================')
                        
                        self.set_workload_wrapper(chunk, config.SIZE_OF_BUCKET, config.TRAIN_NEURAL_NETWORK, config.BASE_FILE_NAME)
                        self.set_cache_wrapper(cache_type, capacity)
                        execution_id = (cache_type.__name__.lower(), schel.__name__.lower(), chunk, capacity)
                        self.workflow.workerpool_init(job, self.connection, self.workload, self.cache, schel.__name__.lower(), descriptor, config.OUTPUT_PATH, execution_id, constants.VERBOSEMODE)
        
        return True
