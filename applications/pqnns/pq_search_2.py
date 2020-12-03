
from containers.wrapper.wrappers import LibraryWrapper
from utils import package_builder, package_extractor

import numpy as np
import time 


def _sumidxtab(distab, codebook, j, m, n):
    return [distab[codebook[j+i*m]] for i in range(n)]
            

def pq_search_2(pq, codebook, cache, task, k, tt, icache):
    
    nrules = hits = 0
    
    distab = [0.0]*codebook.n
    code = np.array(codebook.mat).ravel()
    
    lib = LibraryWrapper.get('libyael.so')
    
    for i in range(pq.m):
        
        key = tuple(enumerate(task[i*pq.ds:(i+1)*pq.ds]))
        t1 = time.time()
        rule = cache.get(key)
        tt['get_cache'] = time.time() - t1 if 'get_cache' not in tt else tt['get_cache'] + (time.time() - t1)
        
        if isinstance(rule, int) and rule == -1:
            t1 = time.time()
            vsub = package_builder(task[i*pq.ds:(i+1)*pq.ds]).create()
            centroids_tmp = package_builder(pq.centroids[i]).create()
            distab_temp = package_builder([0.0]*pq.ks).create()
            
            lib.compute_cross_distances(pq.ds, 1, pq.ks, vsub, centroids_tmp, distab_temp)
            tmp_dis = _sumidxtab(package_extractor(distab_temp).extract().tolist(), code, i, pq.m, codebook.n)
            distab = np.add(distab, tmp_dis)
            key = tuple(enumerate(task[i*pq.ds:(i+1)*pq.ds]))
            tt['generate_new_rules'] = time.time() - t1 if 'generate_new_rules' not in tt else tt['generate_new_rules'] + (time.time() - t1)
            t1 = time.time()
            cache.set(key, tmp_dis)
            tt['set_cache'] = time.time() - t1 if 'get_cache' not in tt else tt['get_cache'] + (time.time() - t1)
            nrules += 1
        
        else:
            t1 = time.time()
            distab = np.add(distab, rule)
            hits += 1
            tt['using_cache'] = time.time()-t1 if 'using_cache' not in tt else tt['using_cache'] + (time.time() - t1)
        
    distmp = sorted(enumerate(distab), key=lambda k:k[1])
    
    [d for i, d in distmp[0:k]]
    [i for i, d in distmp[0:k]]
    
    return [hits, nrules]

    
