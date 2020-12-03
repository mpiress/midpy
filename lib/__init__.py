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
import lib

import platform, os, sys, ctypes


library_path = lib.__path__[0] + os.sep

class clibrary:
    
    __library           = None
    __initialized       = False

    @staticmethod
    def get(library_name):
        
        if (not clibrary.__initialized):
            clibrary.__initialize(library_name)
            
        return clibrary.__library

    
    @staticmethod
    def __initialize(library_name):
        
        clibrary.__initialized = True
        arc = None
        
        if (platform.architecture()[0] == "64bit"):
            arc = "x64" + os.sep
        else:
            arc = "x86" + os.sep
        
        if not os.path.exists(lib.library_path + arc):
            print("The pymid is not supported for platform '" + sys.platform + "' (" + platform.architecture()[0] + ").\n" + 
                  "Please, contact to 'michelpires@dcc.ufmg.br'.")
            
            return None;
        
        if not os.path.isfile(lib.library_path + arc + library_name):
            print("The lib is not found (expected lib location: '" + lib.library_path + "').\n" + 
                  "Probably lib has not been successfully installed ('" + sys.platform + "', '" + platform.architecture()[0] + "').\n" + 
                  "Please, generate C, C++ shared .so before or contact to 'michelpires@dcc.ufmg.br'.")
            
            return None;

        clibrary.__library = ctypes.cdll.LoadLibrary(lib.library_path + arc + library_name)
        
        return clibrary.__library
    
