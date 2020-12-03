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

#midpy imports
from containers.wrapper.wrappers import LibraryWrapper
from utils import package_builder, package_extractor, read_file

#internal application imports
from applications.pqnns.definations import kmeans_flags, pq

#python imports
import math
import numpy as np       


def pq_new(dataset, m):
    """!
    @brief função utilizada para gerar os quantizadores
        # ds: dimensao dos subvetores
        # ks: numero de centroides por subquantizador
        # flags: modo de inicializacao do kmeans
        # assign: vetor que guarda os indices dos centroides
        # seed: semente do kmeans (qualquer valor diferente de 0)
        # centroids_tmp: vetor que guarda temporariamente os centroides de um subvetor
        # dis: vetor que guarda as distancias entre um centroide e o vetor assinalado por ele
        # vs: vetor que guarda temporariamente cada subvetor
        # pq: estrutura do quantizador
        
    @param[in] dataset: path to learning dataset
    @param[in] m: numero de subquantizadores
        
    """
    seed = 2
    flags = 0
    
    flags   |= kmeans_flags.KMEANS_INIT_BERKELEY
    flags   |= 1
    flags   |= kmeans_flags.KMEANS_QUIET
    
    train   = read_file(dataset, has_header=False)
    dtrain  = train.shape[1]
    ntrain  = train.shape[0]
    train   = np.array(train)
    
    ds = int(dtrain/m)
    ks = int(math.pow(2, m))
    
    pqinst = pq()
    pqinst.m            = m
    pqinst.ks           = ks
    pqinst.ds           = ds
    pqinst.centroidsn   = ks*ds
    pqinst.centroidsd   = m
    pqinst.centroids    = [[0.0]*ks*ds for _ in range(m)]
    
    lib = LibraryWrapper.get('libyael.so')
    
    for i in range(m):
        vs = train[:,i*ds:(i+1)*ds].ravel()
        vs = package_builder(vs).create()
        centroids_tmp = package_builder(pqinst.centroids[i]).create()
        lib.kmeans(ds, ntrain, ks, 100, vs, flags, seed, 1, centroids_tmp, None, None, None)
        pqinst.centroids[i] = package_extractor(centroids_tmp).extract()
    
    return pqinst   
    
    
