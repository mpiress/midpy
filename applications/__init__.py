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

import applications
from utils import load, dump

import os


application_path = applications.__path__[0] + os.sep 


def load_buffer(filename):
    if os.path.isfile(application_path + 'buffer' + os.sep + filename):
        return load(application_path + 'buffer' + os.sep + filename)
    return None
  
    
def dump_buffer(filename, data):
    assert os.path.exists(application_path + 'buffer' + os.sep), '[ERROR] buffer path is not found in applications folder'
    dump(application_path + 'buffer' + os.sep + filename, data)


