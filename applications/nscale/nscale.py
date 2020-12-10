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
        img = cv2.imread(task[0])
        
        blue  = task[1]
        green = task[2]
        red   = task[3]
        
        T1    = task[4]
        T2    = task[5]

        G1    = task[6]
        G2    = task[7]

        minSize = task[8]
        maxSize = task[9]

        minSizePl = task[10]

        minSizeSeg = task[11]
        maxSizeSeg = task[12]

        fillHolesConnectivity = task[13]
        reconConnectivity     = task[14]
        watershedConnectivity = task[15]

        rbc, bgr                            = nscale.segmentNucleiStg1Py(img, (blue, green, red, T1, T2,))
        brg, rc, rc_recon, rc_open          = nscale.segmentNucleiStg2Py(bgr, (reconConnectivity,))
        rc, rc_recon, rc_open, bw1, diffIm  = nscale.segmentNucleiStg3Py([rc, rc_recon, rc_open], (fillHolesConnectivity, G1,))
        bw1, bw1_t                          = nscale.segmentNucleiStg4Py(bw1, (minSize, maxSize,))
        diffIm, bw1_t, rbc, seg_open        = nscale.segmentNucleiStg5Py([diffIm, bw1_t, rbc], (G2,))
        seg_open, seg_nonoverlap            = nscale.segmentNucleiStg6Py([img, seg_open], (minSizePl, watershedConnectivity,))
        seg_nonoverlap, output              = nscale.segmentNucleiStg7Py(seg_nonoverlap, (minSizeSeg, maxSizeSeg, fillHolesConnectivity,))

        cv2.imwrite(task[16], output)
        self.times['cache'] = time.time()

        return [0,0]
        



