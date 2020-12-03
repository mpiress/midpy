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
import os, signal, socket

from multiprocessing import Process
from core.managers.base_master import BaseMaster
from core.managers.base_worker import BaseWorker
from core.managers.orchestrator import Orchestrator
from core.network.pipes import start_named_server, LookupWids, WorkerInfo, waiting_named_server
from core.network.pipes import lookup, obj_finalize

from containers.wrapper.wrappers import NetworkWrapper, WorkloadWrrapper, SchedulerWrapper, CacheWrapper

import time


class WorkflowManager:
    
    def __init__(self):
        self.__orchestrator    = None
        self.__master          = None
        self.__slave           = None
        self.__server          = None
        self.__id_worker       = None
        self.__conn            = None
        self.__times           = {'orchestrator_runtime':0, 'taskmanager_runtime':0, 'workerpool_runtime':0}
    
    def init_server_name(self, conn:NetworkWrapper):
        self.__server = Process(target=start_named_server, args=(conn,))
        self.__server.start()
        
    def shutdown_server_name(self):
        obj_finalize(self.__conn, self.__master.get_daemons())
        os.kill(self.__server.pid, signal.SIGKILL)
        
    def taskmanager_init(self, conn:NetworkWrapper, workload:WorkloadWrrapper, schell:SchedulerWrapper, descriptor, output, isverbose=False):
        if self.__master == None:
            self.__conn = conn
            self.init_server_name(conn)
            waiting_named_server(conn, isverbose)
            self.__master = BaseMaster(conn, workload, schell, descriptor, isverbose)
        self.__times['orchestrator_runtime'], self.__times['taskmanager_runtime'] = self.__master.processing(output)

        return True
        
    def workerpool_init(self, job, conn:NetworkWrapper, workload:WorkloadWrrapper, cache:CacheWrapper, schell=None, descriptor=None, output_path=None, isverbose=False):
        conn.server = waiting_named_server(conn, isverbose)
        generate_wid = lookup(conn=conn, uri='global.queues.lookup_wids')

        if self.__id_worker == None:
            self.__id_worker = generate_wid.get()
            
        print('[INFO]: Starting worker pool management') if isverbose else None
        if self.__slave == None:
            self.__slave = BaseWorker(job, conn, workload, cache, self.__id_worker, schell, descriptor, output_path, isverbose)
        self.__times['workerpool_runtime'] = self.__slave.processing()
        
        generate_wid.put(self.__id_worker)
        self.__id_worker = None

        return True
        
    def get_execution_times(self):
        return self.__times
    
    