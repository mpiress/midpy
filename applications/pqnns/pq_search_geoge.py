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
from utils import package_builder, package_extractor

#python import
import numpy as np

def _sumidxtab(distab, codebook, m):
    code = np.array(codebook.mat).ravel()
    return [sum([distab[j][code[j+i*m]] for j in range(m)]) for i in range(codebook.n)]            
    
def pq_search(pq, codebook, cache, task, k, tt):
    """!
    @brief função utilizada para realizar a pesquisa sob o codebook gerado
        # ids1 : vetor que armazena temporariamente o indice dos vetores mais proximos
        # dis1 : vetor que armazena temporariamente a distancia entre os vetores mais proximos e o vetor da fila
        # distab_temp : vetor que recebe temporariamente a tabela de distancias de um subespaco
        # vsub : estrutura que recebe um subvetor temporariamente
        # distab : estrutura que recebe todas as distancias tabeladas
        # disquerybase : estrutura que recebe as distancias entre os vetores da fila e os vetores mais proximos
        # lib : application wrapper utilizado para chamar a biblioteca C utilizada para as avaliações

    @param[in] pq: classe com o mapeamento dos centroids
    @param[in] codebook: atribuições de centroids gerada para a base avaliada
    @param[in] cache: mecânismo de cache utilizado pelo PyMid para coordenar as regras já tratadas
    @param[in] task: a query a ser avaliada 
    @param[in] k: numero de vetores proximos a serem retornados  
    
    @see: pq_new.py, pq_assign.py  
        
    """
    nrules = hints = 0
    
    distab = [[0.0]*pq.ks for _ in range(pq.m)]
    
    lib = LibraryWrapper.get('libyael.so')
    for i in range(pq.m):
        nrules += 1
        vsub = package_builder(task[i*pq.ds:(i+1)*pq.ds]).create()
        centroids_tmp = package_builder(pq.centroids[i]).create()
        distab_temp = package_builder([0.0]*pq.ks).create()
        lib.compute_cross_distances(pq.ds, 1, pq.ks, vsub, centroids_tmp, distab_temp)
        distab[i] = package_extractor(distab_temp).extract()
        tt['cache'] = 0
                    
    disquerybase = _sumidxtab(distab, codebook, pq.m)
    
    distmp = sorted(list(enumerate(disquerybase)), key=lambda k:k[1])
    
    #if you have that return the result
    D = [d for i, d in distmp[0:k]]
    I = [i for i, d in distmp[0:k]]
    
    return [hints, nrules]
    
