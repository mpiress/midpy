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
import os 
import random

from containers import constants

os.environ['PYRO_LOGLEVEL'] = "ERROR"
os.environ["PYRO_LOGFILE"] = "logs/pyro.log"

from threading import Thread
from queue import Queue
import time, socket

import Pyro4
from Pyro4.naming import startNSloop, locateNS
Pyro4.config.COMPRESSION = False
Pyro4.config.METADATA = False
Pyro4.config.SOCK_REUSE = False
Pyro4.config.THREADPOOL_SIZE = 8192
Pyro4.config.SERIALIZER = 'marshal'
Pyro4.config.SERIALIZERS_ACCEPTED.add('marshal')

PROXIES = {}

##############################################################################################################
#                                            REMOTE OBJECT CLASSES                                           #
##############################################################################################################

#@Pyro4.behavior(instance_mode="single")
class LookupWids:

    def __init__(self, nworkers, wpool):
        self.__wids         = Queue()
        self.__nworkers     = nworkers
        self.__wpool        = wpool
        self.__execution_id = None
        self.serializer = Pyro4.util.get_serializer(Pyro4.config.SERIALIZER)

    def set(self, execution_id):
        self.__wids = Queue()
        [self.__wids.put(wid) for wid in range(self.__nworkers)]
        [self.__wids.put('EXIT') for wid in range(self.__wpool)]
        self.__execution_id = execution_id

    @Pyro4.expose
    def update_execution_id(self, execution_id):
        self.__execution_id = execution_id
        
    @Pyro4.expose
    def get(self, execution_id):
        while execution_id != self.__execution_id:
            time.sleep(1)     
        return self.__wids.get()
        

#@Pyro4.behavior(instance_mode="single")
class ResultQueues:
    def __init__(self, nworkers):
        self.__tasks = {k:Queue() for k in range(nworkers)}
        self.__nworkers = nworkers
        
    @Pyro4.expose
    def reset_queue(self, wid):
        self.__tasks[wid] = Queue()
    
    @Pyro4.expose
    def get(self, wid):
        return self.__tasks[wid].get()
    
    @Pyro4.expose
    def put(self, item, wid):
        self.__tasks[wid].put(item)
        
    @Pyro4.expose
    def get_qsize(self, wid):
        return self.__tasks[wid].qsize()
    
    @Pyro4.expose
    def empty(self, wid):
        return self.__tasks[wid].empty()


#@Pyro4.behavior(instance_mode="single")
class TaskQueues:
    def __init__(self):
        self.__tasks = Queue()
        
    @Pyro4.expose
    def reset_queue(self):
        self.__tasks = Queue()
    
    @Pyro4.expose
    def get(self):
        return self.__tasks.get()
    
    @Pyro4.expose
    def put(self, item):
        self.__tasks.put(item)
        
    @Pyro4.expose
    def get_qsize(self):
        return self.__tasks.qsize()
    
    @Pyro4.expose
    def empty(self):
        return self.__tasks.empty()
    


#@Pyro4.behavior(instance_mode="single")
class WorkerInfo:
    
    def __init__(self, nworkers):
        self.__workers_info = {wid:{'avg_runtime':0, 'size_of_work':0} for wid in range(nworkers)}
        self.__idle_workers = [wid for wid in range(nworkers)]
        
    @Pyro4.expose
    def update(self, wid, avgttl, sworkload):
        self.__workers_info[wid] = {'avg_runtime':avgttl, 'size_of_work':sworkload}
    
    @Pyro4.expose
    def get(self, wid):
        return self.__workers_info[wid]
    
    @Pyro4.expose
    def rem_idle_worker(self, wid):
        if wid in self.__idle_workers:
            del(self.__idle_workers[self.__idle_workers.index(wid)])
    
    @Pyro4.expose
    def add_idle_worker(self, wid):
        if wid not in self.__idle_workers:
            self.__idle_workers.append(wid)
        
    @Pyro4.expose
    def get_idle_workers(self):
        return self.__idle_workers
    
    @Pyro4.expose
    def clear_worker(self, wid):
        self.__workers_info[wid] = {'avg_runtime':0, 'size_of_work':0}
        self.add_idle_worker(wid)
                      

##############################################################################################################
#                                            SUPPORT METHODS                                                 #
##############################################################################################################

def waiting_named_server(conn, isverbose):
    print('[INFO]: waiting for named server to start in ',conn.server, ' in the port ', conn.port) if isverbose else None
    while True:
        try:
            if os.path.exists(constants.BUFFER + 'server.csv'):
                with open(constants.BUFFER+'server.csv', 'r') as file:
                    conn.server = file.read()
                locateNS(host=conn.server, port=conn.port, hmac_key=str.encode(constants.AUTHKEY))
                break
        except:
            time.sleep(random.uniform(0,1))
            
    return conn.server
            

def obj_publisher(obj, prefix, name, conn):
    with locateNS(host=conn.server, port=conn.port, hmac_key=str.encode(constants.AUTHKEY)) as ns:  
        name = prefix+name+constants.GID
        daemon = Pyro4.core.Daemon(host=conn.server)
        uri = daemon.register(obj)
        ns.register(name, uri, metadata={name})
        Thread(target=daemon.requestLoop).start()   
    return (name, daemon)
        

def obj_finalize(conn, daemons):
    with locateNS(host=conn.server, port=conn.port, hmac_key=str.encode(constants.AUTHKEY)) as ns:
        for name in daemons:
            if ns.list(metadata_any={name}):
                daemons[name].shutdown()
                ns.remove(name)
                    

def start_named_server(conn):
    try:
        startNSloop(host=conn.server, port=conn.port, hmac=str.encode(constants.AUTHKEY), enableBroadcast=conn.broadcast, storage='memory')
    except Exception as e:
        print(e)
        print('[ERROR]: binding can not connect to such ip and port: [', conn.server,', ', conn.port,']')
        

def lookup(conn, uri):
    global PROXIES
    
    with locateNS(host=conn.server, port=conn.port, hmac_key=str.encode(constants.AUTHKEY)) as ns:
        while True:
            try:
                name = uri+constants.GID
                if ns.list(metadata_any={name}):
                    if name not in PROXIES:
                        proxy = Pyro4.Proxy(ns.lookup(name))
                        PROXIES[name] = proxy
                        return proxy
                    else:
                        return PROXIES[name]
                else:
                    time.sleep(random.uniform(0,1))
            except:
                time.sleep(1)
                    
    
     

    
    
                      

    


