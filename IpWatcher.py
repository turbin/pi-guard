'''
Created on Jul 23, 2013

@author: turbinyan
'''
import pickle
import os.path

import re
import urllib.request 

class IpWacher:
    '''
    containt ip addr
    '''
    _file_name = 'ip_addr.pickle'
    _ip_addr = ''
            
    def __init__(self, path):
        self._file_name = path + self._file_name
        print('path '+self._file_name+' is exsits '+str(os.path.exists(self._file_name)))
        if os.path.exists(self._file_name): 
            return
        with open(self._file_name,'wb+') as data:
            print('create ip_addr.pickle')
            pickle.dump('0.0.0.0', data)
    
    # for public api
    def currentIP(self):
        self._ip_addr = self.visit('http://checkip.dyndns.org')
        return  self._ip_addr
        
    def hasChanged(self):
        if self.currentIP() != self.getRecord():
            return True
        else
            return False
    def recode(self):
        return _record(self)
    
    # for private API
    def visit(self,url):  
        response = urllib.request.urlopen(url)
        html = response.read()
        html = html.decode('utf-8')
        print('html '+html)
        ip_addr = re.findall('\d+\.\d+\.\d+\.\d+', html)
        return ip_addr

    def getRecord(self):
        try:
            with open(self._file_name,'rb') as data:
                ip_addr = pickle.load(data)
                print('load ip '+str(ip_addr)+'in path '+self._file_name)
                return str(ip_addr)
#                 return re.findall('\d+\.\d+\.\d+\.\d+', ip_addr).group(0)
        except IOError:
            print('The ip_addr.pickle is missing!')
            return 'none'
        
    def _record(self, ip):
        try:
            with open(self._file_name,'wb+') as data:
                print('write ip '+str(ip)+"in "+self._file_name)
                pickle.dump(ip, data)
            with open(self._file_name,'rb') as data:
                ip_addr = pickle.load(data)
                print('reload ip '+str(ip_addr)+"in "+self._file_name)

        except IOError:
            print('The ip_addr.pickle is missing!')
    