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
import time 

from concurrent import futures


def _sumidxtab(distab, codebook, j, m, n):
    return [distab[codebook[j+i*m]] for i in range(n)]
            

def __processing_m(cache, task, tt, tid, pq, lib, distab, code, codebook):
    nrules = hits = 0
    
    t1 = time.time()
    vsub = package_builder(task[tid*pq.ds:(tid+1)*pq.ds]).create()
    centroids_tmp = package_builder(pq.centroids[tid]).create()
    distab_temp = package_builder([0.0]*pq.ks).create()
    
    lib.compute_cross_distances(pq.ds, 1, pq.ks, vsub, centroids_tmp, distab_temp)
    key = package_extractor(distab_temp).extract().tolist()
    tc = time.time()
    rule = cache.get(tuple(key))
    tt['cache'] = time.time() - tc if 'cache' not in tt else tt['cache'] + (time.time() - tc)
    
    if isinstance(rule, int) and rule == -1:
        tmp_dis = _sumidxtab(key, code, tid, pq.m, codebook.n)
        distab = np.add(distab, tmp_dis)
        tt['generate_rules'] = time.time() - t1 if 'generate_rules' not in tt else tt['generate_rules'] + (time.time() - t1)
        t1 = time.time()
        cache.set(tuple(key), tmp_dis)
        tt['cache'] = time.time() - t1 if 'cache' not in tt else tt['cache'] + (time.time() - t1)
        nrules += 1

    else:
        t1 = time.time()
        distab = np.add(distab, rule)
        hits += 1
        tt['cache'] = time.time()-t1 if 'cache' not in tt else tt['cache'] + (time.time() - t1)
    
    return nrules, hits

    
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
    @param[in] tt: time variable to measure the execution times   
    
    @see: pq_new.py, pq_assign.py  
        
    """
    nrules = hits = 0
    ds     = int(len(task)/pq.m)
    distab = [0.0]*codebook.n
    cents  = [0.0]*256
    code = np.array(codebook.mat).ravel()
    lib = LibraryWrapper.get('libyael.so')
    
    #for tid in range(pq.m):
    #    r, h = __processing_m(cache, task, tt, tid, pq, lib, distab, code, codebook)
    #    nrules += r
    #    hits   += h

    #with futures.ThreadPoolExecutor(max_workers=1) as executor:
    #    pool = {executor.submit(__processing_m, cache, task, tt, tid, pq, lib, distab, code, codebook) : tid for tid in range(pq.m)}
    
    #for feature in futures.as_completed(pool):
    #    data = feature.result()
    #    nrules += data[0]
    #    hits += data[1]
            
    
    for i in range(pq.m):
        
        #key = tuple(enumerate(task[i*pq.ds:(i+1)*pq.ds]))
        #t1 = time.time()
        #rule = cache.get(key)
        #tt['get_cache'] = time.time() - t1 if 'get_cache' not in tt else tt['get_cache'] + (time.time() - t1)
        
        #if isinstance(rule, int) and rule == -1:
        t1 = time.time()
        vsub = package_builder(task[i*pq.ds:(i+1)*pq.ds]).create()
        centroids_tmp = package_builder(pq.centroids[i]).create()
        distab_temp = package_builder([0.0]*pq.ks).create()
        print(len(task[i*pq.ds:(i+1)*pq.ds]))
        print(len(pq.centroids[i]))
        print(len(pq.centroids))
        exit(1)
        lib.compute_cross_distances(pq.ds, 1, pq.ks, vsub, centroids_tmp, distab_temp)
        distab_temp = package_extractor(distab_temp).extract().tolist()
        tc = time.time()
        key = list(map(lambda x:x[0], sorted(enumerate(distab_temp), key=lambda x:x[1])[0:k]))
        rule = -1 #cache.get(key)
        #tt['cache'] = time.time() - tc if 'cache' not in tt else tt['cache'] + (time.time() - tc)

        if isinstance(rule, int) and rule == -1:
            tmp_dis = _sumidxtab(distab_temp, code, i, pq.m, codebook.n)
            distab = np.add(distab, tmp_dis)
            tt['generate_rules'] = time.time() - t1 if 'generate_rules' not in tt else tt['generate_rules'] + (time.time() - t1)
            #tc = time.time()
            #cache.set(key, tmp_dis)
            #tt['cache'] = time.time() - t1 if 'cache' not in tt else tt['cache'] + (time.time() - t1)
            nrules += 1

        else:
            print('FOI !!')
            tc = time.time()
            distab = np.add(distab, rule)
            tt['cache'] = time.time() - tc if 'cache' not in tt else tt['cache'] + (time.time() - tc)
            hits += 1

            #key = tuple(enumerate(task[i*pq.ds:(i+1)*pq.ds]))
            #tt['generate_new_rules'] = time.time() - t1 if 'generate_new_rules' not in tt else tt['generate_new_rules'] + (time.time() - t1)
            #t1 = time.time()
            #cache.set(key, tmp_dis)
            #tt['set_cache'] = time.time() - t1 if 'get_cache' not in tt else tt['get_cache'] + (time.time() - t1)
            #nrules += 1
        
        #else:
        #    t1 = time.time()
        #    distab = np.add(distab, rule)
        #    hits += 1
        #    tt['using_cache'] = time.time()-t1 if 'using_cache' not in tt else tt['using_cache'] + (time.time() - t1)
        
    distmp = sorted(enumerate(distab), key=lambda k:k[1])
    
    #if you have that return the result, set variables dis and ids before each procedure between [ ... ]
    D = [d for i, d in distmp[0:k]]
    I = [i for i, d in distmp[0:k]]
    return [hits, nrules]

    
