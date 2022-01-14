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
import ast

import time


class NNSCHELLBYSIGNATURE(SchedulerManager):
    '''
    @brief NNSCHELLBYSIGNATURERR Round Robin Version Scheduler Policy
    '''

    def __init__(self, conn:NetworkWrapper, workload:WorkloadWrrapper, tasks, descriptor, warmup_cache=0, isverbose=True):
        
        super(NNSCHELLBYSIGNATURE, self).__init__(conn, workload, tasks, descriptor, warmup_cache, isverbose)
        
        if self.isverbose:
            print('[INFO]: executing NNSCHELLBYSIGNATURE scheduler for ', self.sizeof ,' tasks')
        
    
    def predict(self):
        
        print('[INFO]: assign', str(self.sizeof),'tasks for ',str(self.conn.nworkers),' worker(s)') if self.isverbose else None
        workload = 0

        t1 = time.time()
        data = None 
        file = "/var/tmp/"+str(self.conn.nworkers)+"w"+str(self.warmup)+".csv"
        with open(file, "r") as fp:
            for l in fp:
                data = ast.literal_eval(l)
        
        for wid in data:
            chunk = []

            for idx in data[wid]:
                chunk.append([idx, self.descriptor.readlineidx(idx)])
            
            self.assign_tasks(chunk, self.workload.mod_or_div, wid) 
        
        self.set_exit()
        
        print('[INFO]: time expended for scheduling the tasks: ', self.metrics['schell_runtime']) if self.isverbose else None
            
        
             
        
        
        
        