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

import csv
from reduce.base_reduce import BaseReduce

class Reduce(BaseReduce):
    
    def __init__(self, connection):
        super(Reduce, self).__init__(connection)
    
    def reduce(self, wid, output):
        
        data = self.global_queue_results.get(wid)
        
        with open(output[0], 'a', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=' ')    
            sec = ['worker '+str(wid)+':']
            writer.writerow(sec)
        
            for machine in data:
                
                for worker in data[machine]:
                    
                    for item in data[machine][worker]:
                        
                        if item == 'worker_runtime':
                            writer.writerow(['Machine ' + str(machine) + ' Worker ' + str(worker) + ' with worker runtime:' + str(data[machine][worker][item])])
                        
                        elif item == 'tasks_runtime':
                            print('[INFO]: worker ', str(machine), ' with task runtime in ', str(data[machine][worker][item]))
                            writer.writerow(['Machine ' + str(machine) + ' Worker ' + str(worker) + ' with tasks runtime:' + str(data[machine][worker][item])])

                        elif item == 'wait_runtime':
                            print('[INFO]: worker ', str(machine), ' with wait task runtime in ', str(data[machine][worker][item]))
                            writer.writerow(['Machine ' + str(machine) + ' Worker ' + str(worker) + ' with wait runtime:' + str(data[machine][worker][item])])
                        
                        elif item == 'cache_runtime':
                            print('[INFO]: worker ', str(machine), ' with cache runtime in ', str(data[machine][worker][item]))
                            writer.writerow(['Machine ' + str(machine) + ' Worker ' + str(worker) + ' with cache runtime:' + str(data[machine][worker][item])])

                        elif item == 'number_of_rules':
                            writer.writerow(['Machine ' + str(machine) + ' Worker ' + str(worker) + ' number of missing:' + str(data[machine][worker][item])])
                        
                        elif item == 'cache_memory':
                            writer.writerow(['Machine ' + str(machine) + ' Worker ' + str(worker) + ' cache_size:' + str(data[machine][worker][item])])
                        
                        elif item == 'number_of_hits':
                            writer.writerow(['Machine ' + str(machine) + ' Worker ' + str(worker) + ' number of hits:' + str(data[machine][worker][item])])
                        
                        elif item ==  'size_of_work':
                            writer.writerow(['Machine ' + str(machine) + ' Worker ' + str(worker) + ' with size of work:' + str(data[machine][worker][item])])
                            
                        elif item ==  'size_of_cache':
                            writer.writerow(['Machine ' + str(machine) + ' Worker ' + str(worker) + ' with size_of_cache:' + str(data[machine][worker][item])])
                        
                        elif item ==  'cache_memory_usage':
                            writer.writerow(['Machine ' + str(machine) + ' Worker ' + str(worker) + ' with cache_memory_usage_in_bytes:' + str(data[machine][worker][item])])

                        elif item == 'times':    
                            #process execution time obtained of job process - design pattern in dictionary <key, value>
                            job_times = data[machine][worker][item]
                            for key, value in job_times.items():
                                writer.writerow(['Machine ' + str(machine) + ' Worker ' + str(worker) + ' with ' + str(key) + ' runtime:' + str(value)])
        
        
