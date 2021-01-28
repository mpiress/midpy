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

from lib import clibrary
from containers import constants

class WorkloadWrrapper:
    overview             = {'chunk':1}  
    mod_or_div           = constants.DIV
    train_neural_network = False
    job_name             = None

class NetworkWrapper:
    server              = None
    port                = 32001
    broadcast           = False
    workers             = []
    nworkers            = 1
    nthreads            = 1
    
class SchedulerWrapper:
    type_scheduler      = None
    
      
class CacheWrapper:
    type_cache          = None
    capacity            = 0
    percent             = 0
   
class LibraryWrapper:
    @staticmethod
    def get(library_name):
        return clibrary.get(library_name)
    
    