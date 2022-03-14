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

from core.managers.worker import BaseWorkerInfo

import cv2
import time, sys
from ctypes import *
import pbcvt


class NSCALE(BaseWorkerInfo):
    
    def __init__(self, input, output):
        self.__input  = input
        self.__output = output 
    
    def __segmentNuclei(self, img, blue, green, red, T1, T2, G1, G2, minSize, maxSize, minSizePl, minSizeSeg, maxSizeSeg, fillHoles, recon, water):
        hits, missing = 0, 0
        s1, s2, s3, s4, s5, s6, s7 = 0,0,0,0,0,0,0 
        
        rule = self.cache.get((blue, green, red, T1, T2, recon, fillHoles, G1, minSize, maxSize, G2, minSizePl, water, minSizeSeg, maxSizeSeg,), 8)
        
        if rule == -1:
            missing += 1

            s1 = time.time()
            rule = self.cache.get((blue, green, red, T1, T2,), 1)
            if rule == -1:
                missing += 1
                rbc, bgr = pbcvt.segmentNucleiStg1Py(img, (blue, green, red, T1, T2,))
                memory = sys.getsizeof((blue, green, red, T1, T2,))
                memory += sys.getsizeof(rbc)
                memory += sys.getsizeof(rbc)
                self.cache.set((blue, green, red, T1, T2,), [rbc, bgr], memory, 1)
                
            else:
                hits += 1
                rbc, bgr = rule
            s1 = time.time() - s1

            s2 = time.time()
            rule = self.cache.get((blue, green, red, T1, T2, recon,), 2)
            if rule == -1:
                missing += 1
                bgr, rc, rc_recon, rc_open = pbcvt.segmentNucleiStg2Py(bgr, (recon,))
                memory = sys.getsizeof((blue, green, red, T1, T2, recon,))
                memory += sys.getsizeof(bgr)
                memory += sys.getsizeof(rc)
                memory += sys.getsizeof(rc_recon)
                memory += sys.getsizeof(rc_open)
                self.cache.set((blue, green, red, T1, T2, recon,), [bgr, rc, rc_recon, rc_open], memory, 2)

            else:
                hits += 1
                bgr, rc, rc_recon, rc_open = rule
            s2 = time.time() - s2
            
            s3 = time.time()
            rule = self.cache.get((blue, green, red, T1, T2, recon, fillHoles, G1,), 3)
            if rule == -1:
                missing += 1
                rc, rc_recon, rc_open, bw1, diffIm  = pbcvt.segmentNucleiStg3Py([rc, rc_recon, rc_open], (fillHoles, G1,))
                memory = sys.getsizeof((blue, green, red, T1, T2, recon, fillHoles, G1,))
                memory += sys.getsizeof(rc)
                memory += sys.getsizeof(rc_recon)
                memory += sys.getsizeof(rc_open)
                memory += sys.getsizeof(bw1)
                memory += sys.getsizeof(diffIm)
                self.cache.set((blue, green, red, T1, T2, recon, fillHoles, G1,), [rc, rc_recon, rc_open, bw1, diffIm], memory, 3)
                    
            else:
                hits += 1
                rc, rc_recon, rc_open, bw1, diffIm = rule
            s3 = time.time() - s3
            
            s4 = time.time()
            rule = self.cache.get((blue, green, red, T1, T2, recon, fillHoles, G1, minSize, maxSize,), 4)
            if rule == -1:
                missing += 1
                bw1, bw1_t = pbcvt.segmentNucleiStg4Py(bw1, (minSize, maxSize,))
                memory = sys.getsizeof((blue, green, red, T1, T2, recon, fillHoles, G1, minSize, maxSize,))
                memory += sys.getsizeof(bw1)
                memory += sys.getsizeof(bw1_t)
                self.cache.set((blue, green, red, T1, T2, recon, fillHoles, G1, minSize, maxSize,), [bw1, bw1_t], memory, 4)
                    
            else:
                hits += 1
                bw1, bw1_t = rule 
            s4 = time.time() - s4

            s5 = time.time()
            rule = self.cache.get((blue, green, red, T1, T2, recon, fillHoles, G1, minSize, maxSize, G2,), 5)
            if rule == -1:
                missing += 1
                diffIm, bw1_t, rbc, seg_open  = pbcvt.segmentNucleiStg5Py([diffIm, bw1_t, rbc], (G2,))
                memory = sys.getsizeof((blue, green, red, T1, T2, recon, fillHoles, G1, minSize, maxSize, G2,))
                memory += sys.getsizeof(diffIm)
                memory += sys.getsizeof(bw1_t)
                memory += sys.getsizeof(rbc)
                memory += sys.getsizeof(seg_open)
                self.cache.set((blue, green, red, T1, T2, recon, fillHoles, G1, minSize, maxSize, G2,), [diffIm, bw1_t, rbc, seg_open], memory, 5)
                
            else:
                hits += 1
                diffIm, bw1_t, rbc, seg_open = rule
            s5 = time.time() - s5
            
            s6 = time.time()
            rule = self.cache.get((blue, green, red, T1, T2, recon, fillHoles, G1, minSize, maxSize, G2, minSizePl, water,), 6)
            if rule == -1:
                missing += 1
                seg_open, seg_nonoverlap  = pbcvt.segmentNucleiStg6Py([img, seg_open], (minSizePl, water,))
                memory = sys.getsizeof((blue, green, red, T1, T2, recon, fillHoles, G1, minSize, maxSize, G2, minSizePl, water,))
                memory += sys.getsizeof(seg_open)
                memory += sys.getsizeof(seg_nonoverlap)
                self.cache.set((blue, green, red, T1, T2, recon, fillHoles, G1, minSize, maxSize, G2, minSizePl, water,), [seg_open, seg_nonoverlap], memory, 6)
    
            else:
                hits += 1
                seg_open, seg_nonoverlap = rule
            s6 = time.time() - s6

            s7 = time.time()
            rule = self.cache.get((blue, green, red, T1, T2, recon, fillHoles, G1, minSize, maxSize, G2, minSizePl, water, minSizeSeg, maxSizeSeg,), 7)
            if rule == -1:
                missing += 1
                seg_nonoverlap, output  = pbcvt.segmentNucleiStg7Py(seg_nonoverlap, (minSizeSeg, maxSizeSeg, fillHoles,))
                memory = sys.getsizeof((blue, green, red, T1, T2, recon, fillHoles, G1, minSize, maxSize, G2, minSizePl, water, minSizeSeg, maxSizeSeg,))
                memory += sys.getsizeof(seg_nonoverlap)
                memory += sys.getsizeof(output)
                self.cache.set((blue, green, red, T1, T2, recon, fillHoles, G1, minSize, maxSize, G2, minSizePl, water, minSizeSeg, maxSizeSeg,), [seg_nonoverlap, output], memory, 7)
                
            else:
                hits += 1
                output = rule
            s7 = time.time() - s7
        
        else:
            hits += 1
            output = rule[1]

        #print('TEMPOS:: S1:', s1, ' S2:', s2, ' S3:', s3, ' S4:', s4, ' S5:', s5, ' S6:', s6, ' S7:', s7)
        #print("TEMPO:", s1+s2+s3+s4+s5+s6+s7)

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
        
        blue  = int(task[0])
        green = int(task[1])
        red   = int(task[2])
        
        T1    = float(task[3])
        T2    = float(task[4])

        G1    = int(task[5])
        G2    = int(task[6])

        minSize = int(task[7])
        maxSize = int(task[8])

        minSizePl = int(task[9])

        minSizeSeg = int(task[10])
        maxSizeSeg = int(task[11])

        fillHoles = int(task[12])
        recon     = int(task[13])
        water     = int(task[14])

        t1 = time.time()
        hits, missing, output = self.__segmentNuclei(img, blue, green, red, T1, T2, G1, G2, minSize, maxSize, minSizePl, minSizeSeg, maxSizeSeg, fillHoles, recon, water)
        self.times['segmentNuclei'] = time.time() - t1 if 'segmentNuclei' not in self.times else self.times['segmentNuclei'] + (time.time() - t1)

        #cv2.imwrite(self.__output, output)
        
        return [hits,missing]
        



