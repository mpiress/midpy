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

from containers.wrapper.wrappers import SchedulerWrapper, WorkloadWrrapper, NetworkWrapper

class Orchestrator:

    def __init__(self, conn:NetworkWrapper, workload:WorkloadWrrapper, schell:SchedulerWrapper, workers_queues=None, descriptor=None, warmup=None, isverbose=False):
        self.__isverbose = isverbose
        print('[INFO]: instantiating scheduler policy') if isverbose else None
        scheduler_policy = type('Scheduler', (schell.type_scheduler,), {})
        self.__scheduler = scheduler_policy(conn, workload, schell, workers_queues, descriptor, warmup, isverbose)
        
    def get_scheduler(self):
        return self.__scheduler
    
    def schedulling(self):
        print('[INFO]: Executing scheduler policy') if self.__isverbose else None
        return self.__scheduler.predict()
    
    def get_metrics(self):
        print('[INFO]: Scheduler providing metrics') if self.__isverbose else None
        return self.__scheduler.get_metrics()
        
        
        
        