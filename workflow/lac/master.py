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
import math, os, shutil, sys, socket
from containers import constants

path = os.getcwd()
path = path[0:path.find('MidPy') + 5]
sys.path.append(path)

from workflow import network_wrapper, metric_wrapper, workload_wrapper
from workflow import start_workflow_master, shutdown_server_name
from workflow.lac.config import config


def parameterization(metric, chunk):
    network_wrapper(config.AUTHKEY, config.SERVER_PORT, config.NWORKERS, config.GID, config.BUFFER)
    metric_wrapper(metric)
    workload_wrapper(chunk, config.TEST, constants.NO_HAS_HEADER, 'queries', config.MOD_OR_DIV)
    
def run():

    config.SERVER = socket.gethostbyname(socket.gethostname())
    with open(config.BUFFER+'server.csv', 'w') as file:
        file.write(config.SERVER)
   
    file = '/var/tmp/'+config.JOB+'_'+config.TEST[config.TEST.rfind('/')+1:]
    if not os.path.isfile(file):
        shutil.copyfile(config.TEST, file)
    
    config.TEST = file
    
    for cache in config.CACHE_TYPE:
        for m in config.METRICS:
            for p in config.PATTERNS:
                csize = config.CACHE_CAPACITY
                for s in csize:
                    s = s if s >= 0 else 0
                    if constants.VERBOSEMODE:
                        print('================================================================================================')
                        print('Starting the cache '+cache.__name__.lower()+' with '+str(s)+'% and '+m.__name__.lower()+' metric')
                        print('================================================================================================')
                    parameterization(m, p)
                    mod = '#div' if config.MOD_OR_DIV else '#mod' 
                    output_path = [config.OUTPUT_PATH+config.JOB+'_'+cache.__name__.lower()+'_'+str(config.NWORKERS)+'_'+mod+'.csv', str(s)]
                    start_workflow_master(output_path, isverbose=constants.VERBOSEMODE)
    
    shutdown_server_name()
    
    
if __name__ == '__main__':
    
    run()
    if os.path.isfile(config.TEST):
        os.remove(config.TEST)
    
    exit(0)
    
