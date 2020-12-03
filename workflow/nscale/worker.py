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
import os, sys

path = os.getcwd()
path = path[0:path.find('MidPy') + 5]
sys.path.append(path)

from workflow import start_workflow_worker
from workflow.nscale.scripts.config import config
from workflow.nscale.scripts.descriptor import CacheDescriptor

if __name__ == '__main__':
    descriptor = CacheDescriptor()
    start_workflow_worker(config, descriptor)
    exit(0)

