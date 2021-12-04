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
#pymid imports
from containers.wrapper.wrappers import LibraryWrapper
from utils import package_builder, package_extractor, read_file

#internal imports
from applications.pqnns.definations import codebook

#python import
import numpy as np


def pq_assign(dataset, pq):
    """!
    @brief função utilizada para gerar o codebook
        # assigns : indice dos k elementos mais proximos
        # dis : distancia entre os k elementos mais proximos e os definitivos
        # vsub : estrutura que contém temporariamente os subvetores
        # code : estrutura que armazena o codebook
        
    @param[in] dataset: caminho para a base a ser avaliada
    @param[in] pq: classe com o mapeamento dos centroids 
    
    @see: definations.py, pq_new.py
        
    """
    
    base    = read_file(dataset, has_header=False)
    nbase   = base.shape[0]
    base    = np.array(base.values.tolist())
    
    
    #predefinations 
    assigns  = package_builder([0]*nbase).create()
    dis      = package_builder([0]*nbase).create()
    code     = codebook()
    code.n   = nbase
    code.d   = 0
    code.mat = [[0]*nbase for _ in range(pq.m)]
    
    
    lib = LibraryWrapper.get('libyael.so')
    
    for i in range(pq.m):
        vsub = base[:,i*pq.ds:(i+1)*pq.ds].ravel()
        vsub = package_builder(vsub).create()
        centroids_tmp = package_builder(pq.centroids[i]).create()
        lib.knn_full(2, nbase, pq.ks, pq.ds, 1, centroids_tmp, vsub, None, assigns, dis)
        code.mat[i] = package_extractor(assigns).extract()
    
    return code 
    
    