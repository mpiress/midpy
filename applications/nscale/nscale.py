from core.managers.worker import BaseWorkerInfo
from containers.wrapper.wrappers import LibraryWrapper
from utils import package_builder, package_extractor

import cv2
from ctypes import *
import numpy as np
import pbcvt

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
        
        #stdcpp= cdll.LoadLibrary("libstdc++.so.6")
        
        #out = Popen(args="nm ../../lib/x64/libsegment.so", shell=True, stdout=PIPE).communicate()[0].decode("iso-8859-1")
        #attrs = [i.split(" ")[-1].replace("\r", "") for i in out.split("\n") if " T " in i]
        #functions = [i for i in attrs if hasattr(lib, i)]
        #print(functions)
        
        #prepare inputs
        img = cv2.imread(task[0])
        
        blue  = task[1]
        green = task[2]
        red   = task[3]
        T1    = task[4]
        T2    = task[4]

        args = (blue, green, red, T1, T2)

        pbcvt.segmentNucleiStg1Py(img, args)

        
        



