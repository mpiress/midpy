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

import pickle, os, csv
import numpy as np
import collections
import pandas as pd

from sklearn.preprocessing import MinMaxScaler

from ctypes import *


def get_delimiter(path):
    delimiter = csv.Sniffer()
    with open(path, 'r') as fp:
        fp.readline()
        line = fp.readline()
    try:
        d = delimiter.sniff(line, [',',';', '\t']).delimiter
    except:
        d = None
    return d
    


def read_file(path, has_header=False, cols=None, norm=True):
    data = []
    assert os.path.isfile(path), '[ERROR] file is not found in dataset folder, read_file error'
    
    d = get_delimiter(path)
    
    if d:
        if has_header:
            data = pd.read_csv(path, delimiter=d, usecols=cols)
        else:
            data = pd.read_csv(path, header=None, delimiter=d) 
    else:
        if has_header:
            data = pd.read_csv(path, usecols=cols)
        else:
            data = pd.read_csv(path, header=None) 

    if norm:
        min_max_scaler = MinMaxScaler()
        data = pd.DataFrame(min_max_scaler.fit_transform(data.values))
            
    return data


def dump(path, data):
    open(path, 'w').close()
    with open(path,'wb') as fp:
        pickle.dump(data, fp)
    
        
def load(path):
    with open(path,'rb') as fp:
        data = pickle.load(fp)    
    return data

                 
class type_data:
    """!
    @brief Contains constants that defines type of package.
    
    """
    
    TYPE_INT                            = 0x00
    TYPE_UNSIGNED_INT                   = 0x01
    TYPE_FLOAT                          = 0x02
    TYPE_DOUBLE                         = 0x03
    TYPE_LONG                           = 0x04
    TYPE_UNSIGNED_CHAR                  = 0x05
    TYPE_UNSIGNED_LONG                  = 0x06
    TYPE_LIST                           = 0x07
    TYPE_SIZE_T                         = 0x08
    TYPE_UNDEFINED                      = 0x09
    

    __CTYPE_PYMID_MAP = { 
        c_int                           : TYPE_INT,
        c_uint                          : TYPE_UNSIGNED_INT,
        c_float                         : TYPE_FLOAT,
        c_double                        : TYPE_DOUBLE,
        c_long                          : TYPE_LONG,
        c_ulong                         : TYPE_UNSIGNED_LONG,
        c_size_t                        : TYPE_SIZE_T,
        c_ubyte                         : TYPE_UNSIGNED_CHAR,
        None                            : TYPE_UNDEFINED
    }

    __PYMID_CTYPE_MAP = {
        TYPE_INT                        : c_int,
        TYPE_UNSIGNED_INT               : c_uint,
        TYPE_FLOAT                      : c_float,
        TYPE_DOUBLE                     : c_double,
        TYPE_LONG                       : c_long,
        TYPE_UNSIGNED_LONG              : c_ulong,
        TYPE_SIZE_T                     : c_size_t,
        TYPE_UNSIGNED_CHAR              : c_ubyte,
        TYPE_UNDEFINED                  : None
    }

    @staticmethod
    def get_ctype(pymid_package_type):
        """!
        @return (ctype) Return ctype that corresponds to pymid type data.
        
        """
        return type_data.__PYMID_CTYPE_MAP[pymid_package_type]

    
    @staticmethod
    def get_pymid_type(data_ctype):
        """!
        @return (unit) Return pymid data type that corresponds to ctype.
        
        """
        return type_data.__CTYPE_PYMID_MAP[data_ctype]



class package_builder:
    """!
    @brief Package builder provides service to create 'pymid_package' from data that is stored in 'list' container.

    """
    def __init__(self, data):
        """!
        @brief Initialize package builder object by dataset.
        
        @param[in] dataset (array): Data that should be packed in 'pymid_package'.
        @param[in] c_data_type (ctype.type): If specified than specified data type is used for data storing in package. 
        
        """
        self.__data      = data
        self.__data_type = None


    def create(self):
        """!
        @brief Performs convertion python to c_types
        
        @return (pointer) ctype-pointer
        
        """
        assert isinstance(self.__data, collections.Iterable), '[ERROR]: the data should be a interable type'
        builder = None 

        if isinstance(self.__data[0], int):
            self.__data_type = type_data.get_ctype(type_data.TYPE_INT)
        elif isinstance(self.__data[0], float) or isinstance(self.__data[0], np.float32):
            self.__data_type = type_data.get_ctype(type_data.TYPE_FLOAT)
        
        assert self.__data_type != None, '[ERROR]: data type not suported by pymid <using interable type>'
        
        return (self.__data_type * len(self.__data))(* self.__data)
    
    
    

class package_extractor:
    """!
    @brief Package extractor provides servies to unpack pymid package.
    
    """
    def __init__(self, c_package):
        """!
        @brief Initialize package extractor object by ctype-pointer
        
        @param[in] package_pointer (pointer): ctype-pointer that should be used for unpacking.
        
        """
        self.__c_package = c_package


    def extract(self):
        """!
        @brief Performs unpacking procedure of the pymid package to the data.
        
        @return (list) Extracted data from c list to numpy array
        
        """
        
        return np.array(self.__c_package)



    







