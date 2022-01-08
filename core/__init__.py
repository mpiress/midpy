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
import os, signal

from multiprocessing import Process
from core.managers.base_master import BaseMaster
from core.managers.base_worker import BaseWorker
from core.network.pipes import start_named_server, waiting_named_server
from core.network.pipes import lookup, obj_finalize

from containers.wrapper.wrappers import NetworkWrapper, WorkloadWrrapper, SchedulerWrapper, CacheWrapper
from containers import constants

import time


class WorkflowManager:
    
    def __init__(self):
        self.__master          = None
        self.__slave           = None
        self.__server          = None
        self.__id_worker       = None
        self.__conn            = None
        self.__generate_wid    = None
        self.__times           = {'orchestrator_runtime':0, 'taskmanager_runtime':0, 'workerpool_runtime':0}
    
    def init_server_name(self, conn:NetworkWrapper):
        self.__server = Process(target=start_named_server, args=(conn,))
        self.__server.start()
        
    def shutdown_server_name(self, conn):
        obj_finalize(self.__conn, self.__master.get_daemons())
        os.kill(self.__server.pid, signal.SIGKILL)
        
    def taskmanager_init(self, conn:NetworkWrapper, workload:WorkloadWrrapper, schell:SchedulerWrapper, descriptor, output, execution_id=None, isverbose=False):
        self.__conn = conn
        
        if self.__master == None:
            print("[INFO]: Start master queues to manage jobs")  if constants.VERBOSEMODE else None
            self.init_server_name(conn)
            print("[INFO]: Waiting for nameserver to start.")  if constants.VERBOSEMODE else None 
            waiting_named_server(conn, isverbose)
            print("[INFO]: Start master workflow to distribute jobs.")  if constants.VERBOSEMODE else None 
            self.__master = BaseMaster(conn, workload, schell, descriptor, isverbose)
            self.__generate_wid = lookup(conn=conn, uri='global.queues.lookup_wids')

        print("[INFO]: Initiating wids queue to manage execution..")  if constants.VERBOSEMODE else None
        self.__generate_wid.set(execution_id)
        self.__times['orchestrator_runtime'], self.__times['taskmanager_runtime'] = self.__master.processing(output, execution_id[-1])

        return True
        
    def workerpool_init(self, job, conn:NetworkWrapper, workload:WorkloadWrrapper, cache:CacheWrapper, schell=None, descriptor=None, output_path=None, execution_id=None, isverbose=False):
        self.__id_worker = None
        
        print("[INFO]: Waiting for nameserver to start by the master.")  if constants.VERBOSEMODE else None 
        conn.server = waiting_named_server(conn, isverbose)

        print("[INFO]: Lookup wids queue to manage execution..")  if constants.VERBOSEMODE else None
        generate_wid = lookup(conn=conn, uri='global.queues.lookup_wids')
        
        print("[INFO]: Get wid to manage execution..")  if constants.VERBOSEMODE else None
        self.__id_worker = generate_wid.get(execution_id)

        while self.__id_worker != 'EXIT':
            
            if self.__id_worker != 'WAIT':
                print("[INFO]: Start worker workflow to execute jobs.")  if constants.VERBOSEMODE else None 
                self.__slave = BaseWorker(job, conn, workload, cache, self.__id_worker, schell, descriptor, output_path, isverbose)
                self.__slave.update_wid(self.__id_worker)
                self.__times['workerpool_runtime'] = self.__slave.processing()
            
            self.__id_worker = generate_wid.get(execution_id)
            
        return True
        
    def get_execution_times(self):
        return self.__times
    
    