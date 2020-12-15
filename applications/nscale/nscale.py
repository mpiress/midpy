from core.managers.worker import BaseWorkerInfo
from containers.wrapper.wrappers import LibraryWrapper
from utils import package_builder, package_extractor

import cv2
import time
from ctypes import *
import numpy as np
import pbcvt as nscale

from subprocess import Popen, PIPE

class NSCALE(BaseWorkerInfo):
    
    def __init__(self, input, output):
        self.__input  = input
        self.__output = output 
    
    def __segmentNuclei(self, img, blue, green, red, T1, T2, G1, G2, minSize, maxSize, minSizePl, minSizeSeg, maxSizeSeg, fillHoles, recon, water):
        hits, missing = 0

        rule = rule = self.cache.get((blue, green, red, T1, T2, recon, fillHoles, G1, minSize, maxSize, G2, minSizePl, water, minSizeSeg, maxSizeSeg,))
        if rule == -1:
            missing += 1
            rule = rule = self.cache.get((blue, green, red, T1, T2,))
            if rule == -1:
                missing += 1
                rbc, bgr = nscale.segmentNucleiStg1Py(img, (blue, green, red, T1, T2,))
                self.cache.set((blue, green, red, T1, T2,), [rbc, bgr])
            else:
                hits += 1
                rbc, bgr = rule

            rule = rule = self.cache.get((blue, green, red, T1, T2, recon,))
            if rule == -1:
                missing += 1
                bgr, rc, rc_recon, rc_open = nscale.segmentNucleiStg2Py(bgr, (recon,))
                self.cache.set((blue, green, red, T1, T2, recon,), [bgr, rc, rc_recon, rc_open])
            else:
                hits += 1
                bgr, rc, rc_recon, rc_open = rule
            
            rule = rule = self.cache.get((blue, green, red, T1, T2, recon, fillHoles, G1,))
            if rule == -1:
                missing += 1
                rc, rc_recon, rc_open, bw1, diffIm  = nscale.segmentNucleiStg3Py([rc, rc_recon, rc_open], (fillHoles, G1,))
                self.cache.set((blue, green, red, T1, T2, recon, fillHoles, G1,), [rc, rc_recon, rc_open, bw1, diffIm])
            else:
                hits += 1
                rc, rc_recon, rc_open, bw1, diffIm = rule

            rule = rule = self.cache.get((blue, green, red, T1, T2, recon, fillHoles, G1, minSize, maxSize,))
            if rule == -1:
                missing += 1
                bw1, bw1_t = nscale.segmentNucleiStg4Py(bw1, (minSize, maxSize,))
                self.cache.set((blue, green, red, T1, T2, recon, fillHoles, G1, minSize, maxSize,), [bw1, bw1_t])
            else:
                hits += 1
                bw1, bw1_t = rule 

            rule = rule = self.cache.get((blue, green, red, T1, T2, recon, fillHoles, G1, minSize, maxSize, G2,))
            if rule == -1:
                missing += 1
                diffIm, bw1_t, rbc, seg_open  = nscale.segmentNucleiStg5Py([diffIm, bw1_t, rbc], (G2,))
                self.cache.set((blue, green, red, T1, T2, recon, fillHoles, G1, minSize, maxSize, G2, ), [diffIm, bw1_t, rbc, seg_open])
            else:
                hits += 1
                diffIm, bw1_t, rbc, seg_open = rule

            rule = rule = self.cache.get((blue, green, red, T1, T2, recon, fillHoles, G1, minSize, maxSize, G2, minSizePl, water,))
            if rule == -1:
                missing += 1
                seg_open, seg_nonoverlap  = nscale.segmentNucleiStg6Py([img, seg_open], (minSizePl, water,))
                self.cache.set((blue, green, red, T1, T2, recon, fillHoles, G1, minSize, maxSize, G2, minSizePl, water,), [seg_open, seg_nonoverlap])
            else:
                hits += 1
                seg_open, seg_nonoverlap = rule

            rule = rule = self.cache.get((blue, green, red, T1, T2, recon, fillHoles, G1, minSize, maxSize, G2, minSizePl, water, minSizeSeg, maxSizeSeg,))
            if rule == -1:
                missing += 1
                seg_nonoverlap, output  = nscale.segmentNucleiStg7Py(seg_nonoverlap, (minSizeSeg, maxSizeSeg, fillHoles,))
                self.cache.set((blue, green, red, T1, T2, recon, fillHoles, G1, minSize, maxSize, G2, minSizePl, water, minSizeSeg, maxSizeSeg,), [output])
            else:
                hits += 1
                output = rule
        
        else:
            hits += 1
            output = rule

        return [hits, missing, output]

    
    def execute_task(self, task):
        
        #task definition 
        # img: Imagem inicial de entrada. É usada uma imagem RGB.
        # output: Imagem final binária (máscara binária das regiões segmentadas).
        # blue/red/green: Variáveis de threshold para encontrar o background da imagem. Pode usar como valor inicial 200/200/200.
        # T1/T2: Variáveis usadas como peso para as crominâncias Blue e Green para verificar se existem áreas candidatas suficientes a serem segmentadas. Pode usar como valor inicial 1/2.
        # G1/G2: Valores de threshold para binarização das imagens com regiões candidatas e regiões segmentadas. Pode usar como valor inicial 20/4.
        # minSize/maxSize: Tamanhos mínimos e máximos de abertura de áreas candidatas. Pode usar como valor inicial 10/100
        # minSizePl: Parâmetro de abertura das áreas candidatas a núcleos em pixels. Pode usar como valor inicial 20.
        # minSizeSeg/maxSizeSeg: Tamanhos mínimos e máximos, em pixels, que podem ser identificados como núcleos. Pode usar como valor inicial 10/5000.
        # fillHolesConnectivity: 4 ou 8, representando quais pixels devem ser considerados para realizar a operação de fillHoles. Usando 8 o custo computacional aumenta. Pode usar como valor inicial 4.
        # reconConnectivity:  4 ou 8, representando quais pixels devem ser considerados para realizar a operação de seleção de núcleos. Usando 8 o custo computacional aumenta. Pode usar como valor inicial 4.
        # watershedConnectivity 4 ou 8 
        
        #prepare inputs
        img = cv2.imread(self.__input)
        
        blue  = task[0]
        green = task[1]
        red   = task[2]
        
        T1    = task[3]
        T2    = task[4]

        G1    = task[5]
        G2    = task[6]

        minSize = task[7]
        maxSize = task[8]

        minSizePl = task[9]

        minSizeSeg = task[10]
        maxSizeSeg = task[11]

        fillHoles = task[12]
        recon     = task[13]
        water     = task[14]

        t1 = time.time()
        hits, missing, output = self.__segmentNuclei(img, blue, green, red, T1, T2, G1, G2, minSize, maxSize, minSizePl, minSizeSeg, maxSizeSeg, fillHoles, recon, water)
        self.times['segmentNuclei'] = time.time() - t1 if 'segmentNuclei' not in self.times else self.times['segmentNuclei'] + (time.time() - t1)

        #cv2.imwrite(self.__output, output)
        self.info_cache['hits'] += hits
        self.info_cache['missing'] += missing

        return [hits,missing]
        



