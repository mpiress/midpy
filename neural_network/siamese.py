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

from typing import Counter
import warnings
from tensorflow.keras.utils import to_categorical

warnings.filterwarnings('ignore')
import tensorflow as tf

import numpy as np
import pandas as pd
import os, time, math, ast
from matplotlib import pyplot as plt
from imblearn.over_sampling import RandomOverSampler

from containers import constants
from collections import Counter
from scipy.stats.mstats import mquantiles
from sklearn import preprocessing
from sklearn.preprocessing import MinMaxScaler

from imblearn.over_sampling import RandomOverSampler

class SIAMESE():


    def __init__(self, nhidden=[1024, 1024], epochs=200, lr=1e-4, dropout=0.2, descriptor=None, job=None):
        
        np.random.seed(42)

        self.__epochs       = epochs
        self.__nhidden      = nhidden
        self.__input        = 1
        self.__out          = 1
        self.__classes      = None
        self.__lr           = lr
        self.__dropout      = dropout
        self.__job          = job
        self.__descriptor   = descriptor 


        self.__load_model()

        
    def __eval_abs(self, t1, t2):
        return tf.keras.backend.abs(t1 - t2)

    
    def __nnmodel(self):
        T1  = tf.keras.layers.Input((self.__input,), name='t1')
        T2  = tf.keras.layers.Input((self.__input,), name='t2')
        
        initializer = tf.keras.initializers.he_uniform(seed=42)
        bias_init   = 'zeros'
        
        self.__model = tf.keras.Sequential()
        
        
        for h in self.__nhidden[0:-1]:
            self.__model.add(tf.keras.layers.Dense(h, activation='relu', use_bias=True, kernel_initializer=initializer, bias_initializer=bias_init))
            self.__model.add(tf.keras.layers.Dropout(rate=self.__dropout, seed=42))
            
        self.__model.add(tf.keras.layers.Dense(self.__nhidden[-1], activation='relu', use_bias=True, kernel_initializer=initializer, bias_initializer=bias_init))
        
        #encoding inputs based on T1 and T2 
        ET1 = self.__model(T1)
        ET2 = self.__model(T2)

        # Add a customized layer to compute the absolute difference between the encodings
        L1 = tf.keras.layers.Lambda(lambda tensors:self.__eval_abs(tensors[0], tensors[1]))
        L1F = L1([ET1, ET2])
        
        # Add a dense layer with a softmax unit to generate the similarity score
        pred = tf.keras.layers.Dense(self.__out, activation='softmax', use_bias=True, kernel_initializer=initializer, bias_initializer=bias_init)(L1F)
        
        self.__model = tf.keras.Model(inputs=[T1, T2], outputs=pred)
        
        self.__model.compile(optimizer=tf.keras.optimizers.Adam(lr=self.__lr, amsgrad=True), loss='sparse_categorical_crossentropy', metrics=['acc'])
        

        return self.__model

    
    def __get_train_and_test(self):
        scaler = MinMaxScaler()
        
        if not os.path.exists(constants.BUFFERNN+self.__job+'_train.csv'):
            print('[ERROR]: The training set is not saved in the buffer folder')
            exit(1)
        
        X = []
        Y = []
        df = pd.read_csv(constants.BUFFERNN+self.__job+'_train.csv')
        for line in df.itertuples():
            X += self.__descriptor.read_pair_of_tasks(line[1], line[2])
            Y.append(line[3])
            Y.append(line[3])
            
        #IDX_Y = Counter(Y)
        
        #quantiles = mquantiles(list(IDX_Y.values()))
        #qmax      = math.ceil(quantiles[0])/2
        #qmin      = math.ceil(qmax/2)
        
        #IDX_Y = {idx:[] for idx in IDX_Y.keys()}
        #for line in df.itertuples():
        #    if line[3] in IDX_Y and len(IDX_Y[line[3]]) < qmax:
        #        IDX_Y[line[3]] += self.__descriptor.read_pair_of_tasks(line[1], line[2])
 
        #X = []
        #Y = []
        #idx = list(IDX_Y.keys())
        #for i in idx:
        #    if len(IDX_Y[i]) < qmin:
        #        del(IDX_Y[i])
        #    else:
        #        X += IDX_Y[i]
        #        Y += [i]*len(IDX_Y[i])

        self.__descriptor.clear_all()
        
        le = preprocessing.LabelEncoder()
        le.fit(Y)
        Y = le.transform(Y)
        
        smt = RandomOverSampler(random_state=42)
        X, Y = smt.fit_resample(X, Y)
        data = {y:[] for y in set(Y)}
        for t1, t2, y in zip(X[0::2], X[1::2], Y[0::2]):
            data[y].append(t1)
            data[y].append(t2)
        
        print('CLASSES:', Counter(Y))

        trainX = []
        trainY = []
        testX  = []
        testY  = []
        for key in data:
            tsize = math.ceil(len(data[key])*0.20)
            tsize = tsize if tsize % 2 == 0 else tsize + 1
            trainX += data[key][tsize:]
            testX  += data[key][0:tsize]
            trainY += [key]*len(data[key][tsize:])
            testY  += [key]*tsize

        classes = list(data.keys())
        sizeof_task = self.__descriptor.get_task_dimensionality()
        sizeof_output = len(classes)
        
        data = {'classes':[classes], 'sizeof_task':sizeof_task, 'sizeof_output':sizeof_output}
        df = pd.DataFrame(data)
        df.to_csv(constants.BUFFERNN+self.__job+'_config.pkl', index=None)
        
        return np.array(trainX), np.array(trainY), np.array(testX), np.array(testY)

        
        
    def __load_model(self):
        trainX, trainY, testX, testY = None, None, None, None

        checkpoint = constants.BUFFERNN + self.__job + "_model_"+str(self.__nhidden[0])+".h5"
        if not os.path.exists(checkpoint):
            trainX, trainY, testX, testY = self.__get_train_and_test()

        config = pd.read_csv(constants.BUFFERNN+self.__job+'_config.pkl')
        config['classes'].apply(lambda s: list(ast.literal_eval(s)))

        self.__classes = config['classes'].apply(lambda s: list(ast.literal_eval(s))).tolist()[0]
        self.__input   = config['sizeof_task'].values.tolist()[0]
        self.__out     = config['sizeof_output'].values.tolist()[0]
        
        self.__nnmodel()
        
        if os.path.exists(checkpoint):
            self.__model.load_weights(checkpoint)
        
        else:
            
            #trainY = to_categorical(trainY)
            #testY  = to_categorical(testY)
            
            t1 = time.time() 
            cp = tf.keras.callbacks.ModelCheckpoint(checkpoint, verbose=0, save_weights_only=True, period=self.__epochs)
            history = self.__model.fit({'t1':trainX[0::2], 't2':trainX[1::2]}, trainY[0::2], epochs=self.__epochs, callbacks=[cp],\
                                       validation_data=({'t1':testX[0::2], 't2':testX[1::2]}, testY[0::2]))
            data = history.history
            data['Runtime'] = t1 - time.time()

            plt.xlabel('epochs ('+str(self.__epochs)+')')
            plt.ylabel('accuracy')
            plt.plot(data['acc'], label='train')
            plt.plot(data['val_acc'], label='test')
            plt.legend()
            plt.savefig(constants.BUFFERNN + self.__job + '_accuracy_'+str(self.__nhidden[0])+'.png')
            plt.close()

            plt.xlabel('epochs ('+str(self.__epochs)+')')
            plt.ylabel('loss')
            plt.plot(data['loss'], label='train')
            plt.plot(data['val_loss'], label='test')
            plt.legend()
            plt.savefig(constants.BUFFERNN + self.__job + '_loss_'+str(self.__nhidden[0])+'.png')
            plt.close()

            self.__descriptor.load()
        

    def predict(self, t1, t2): 
        
        t1 = np.array(t1)
        t2 = np.array(t2)

        pred = self.__model.predict({'t1':t1, 't2':t2})
        resp = [self.__classes[np.argmax(p)] for p in pred]
        return resp

