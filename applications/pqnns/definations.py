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

class kmeans_flags:
    # flags para o kmeans
    KMEANS_QUIET                = 0x10000
    KMEANS_INIT_BERKELEY        = 0x20000
    KMEANS_NORMALIZE_CENTS      = 0x40000
    KMEANS_INIT_RANDOM          = 0x80000
    KMEANS_INIT_USER            = 0x100000
    KMEANS_L1                   = 0x200000
    KMEANS_CHI2                 = 0x400000
        

class pq:
    def __init__(self):
        self.m = 0
        self.ks = 0
        self.ds = 0
        self.centroids = None
        self.centroidsn = 0
        self.centroidsd = 0


class codebook:
    def __init__(self):
        self.mat = []
        self.d = 0
        self.n = 0
    
    
    
