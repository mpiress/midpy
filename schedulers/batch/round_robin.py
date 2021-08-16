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


from schedulers.base_scheduler import SchedulerManager
from containers.wrapper.wrappers  import NetworkWrapper, WorkloadWrrapper

import time


class RoundRobin(SchedulerManager):
    '''
    @brief Round Robin Scheduler Policy
    '''

    def __init__(self, conn:NetworkWrapper, workload:WorkloadWrrapper, tasks, descriptor, warmup_cache=0, isverbose=True):
        
        super(RoundRobin, self).__init__(conn, workload, tasks, descriptor, warmup_cache, isverbose)
        
        if self.isverbose:
            print('[INFO]: executing RoundRobin scheduler for ', self.sizeof ,' tasks')
        
    
    def predict(self):
        
        print('[INFO]: assign', str(self.sizeof),'tasks for ',str(self.conn.nworkers),' worker(s)') if self.isverbose else None
        workload = 0

        t1 = time.time()
        workload += self.warmup_cache()
        self.metrics['schell_warmup_cache'] = time.time() - t1    
        
        t1 = time.time()
        while workload < self.sizeof:
            chunk = self.get_chunk()
            workload += len(chunk)
            self.assign_tasks(chunk, self.workload.mod_or_div) 
        self.metrics['schell_runtime'] = time.time() - t1    

        self.set_exit()
        
        print('[INFO]: time expended for scheduling the tasks: ', self.metrics['schell_runtime']) if self.isverbose else None
            
        
             
        
        
        
        