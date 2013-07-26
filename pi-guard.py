'''
Created on 2013-7-22

@author: turbin
'''
#coding: GBK 
import smtplib
import re
import urllib.request 
import pickle
import os.path
import threading
import time

import logging
import time
import logging.handlers

from email.mime.multipart import MIMEMultipart 
from email.mime.text import MIMEText 
from email.header import Header



from_addr = 'fly_3@163.com'
to_addr = '86800684@qq.com'
db_path = ' '

# class configLoader:
#     '''
#     configuration file loader
#     file format as:
#     from_addr=XXXX@mail.com
#     passwd=xxxxxx
#     to_addr=xxxx@mail.com
#     '''
#     def __init__(self,path):
#         with open(path+'config') as data:
            

class RecoderFactry:
    '''
    classdocs
    '''
    _logFilePath='./pi-guard-db/'
    _formatter = None
    _handler = None

    def __init__(self,maxBytes = 1024*1024, backupCounts = 2):
        '''
        Constructor
        '''
        if self._handler == None:
            self._logFilePath =self._logFilePath +'pi-guard-'+self.getLocalTime() + '.log'
            print(self._logFilePath)
            self._handler = logging.handlers.RotatingFileHandler(self._logFilePath, maxBytes, backupCounts) # 实例化handler
            fmt = '%(asctime)s - %(filename)s:%(lineno)s - %(name)s - %(message)s'
            formatter = logging.Formatter(fmt)   # 实例化formatter  
            self._handler.setFormatter(formatter)      # 为handler添加formatter

    def getRecoder(self, level, tag):        
        recoder = logging.getLogger(tag)
        recoder.addHandler(self._handler)
        if level == 'debug':
            lv = logging.DEBUG
        elif level == 'error':
            lv = logging.ERROR
        elif level == 'warning':
            lv = logging.WARNING
        elif level == 'critical':
            lv = logging.CRITICAL
        elif level == 'info':
            lv = logging.INFO
        elif level == 'notset':
            lv = logging.NOTSET
        else:
            lv = logging.NOTSET
            
        recoder.setLevel(lv)
        return recoder
    
    def getLocalTime(self):
        return time.strftime('%Y-%m-%d',time.localtime(time.time()))


class MailSender:
    _subject = ''
    _from = ''
    _to = ''
    
    def setSubject(self,subject):
        self._subject = Header(subject, 'utf-8')
    
    def setFrom(self,from_addr):
        self._from = from_addr
        
    def setTo(self,to_addr):
        self._to = to_addr
        
    def send(self,message):
        recorder = RecoderFactry().getRecoder('error','MailSender')
        try:
            server = smtplib.SMTP('smtp.163.com',25)
            server.login(from_addr,'3s7f6t0##')
    
            msg=MIMEMultipart('alternative')
            msg['Subject'] = self._subject
            msg['From'] = self._from
            msg['To'] = self._to
            msg['Cc'] = None

            content = MIMEText(message, 'plain')
            msg.attach(content)         
            server.sendmail(self._from ,self._to, msg.as_string())
            server.quit()
            return 'ok'
        except  smtplib.SMTPAuthenticationError as e:
            recorder.exception('stmp error'+str(e))
            server.quit()
            return 'faild'
        except smtplib.SMTPSenderRefused as e:
            recorder.exception('stmp error'+str(e))
            server.quit()   
            return 'faild'
        except smtplib.SMTPDataError as e:
            recorder.exception('stmp error'+str(e))     
            server.quit()
            return 'faild'
        else:
            recorder.exception('stmp error'+str(e))   
            server.quit()
            return 'faild'
 
class IPManager:
    _file_name = 'ip_addr.pickle'
    _recoder = RecoderFactry().getRecoder('warning', 'IP Manager')
    def __init__(self, path):
        self._file_name = path + self._file_name
        #print('path '+self._file_name+' is exsits '+str(os.path.exists(self._file_name)))
        if os.path.exists(self._file_name): 
            return
        with open(self._file_name,'wb+') as data:
            #print('create ip_addr.pickle')
            pickle.dump('0.0.0.0', data)
        
    def getPublicIP(self):
    #url_group=['http://checkip.dyndns.org/','http://www.ip138.com/ip2city.asp']
        myip = self.visit('http://checkip.dyndns.org')
        return str(myip)
        
    def visit(self,url):  
        response = urllib.request.urlopen(url)
        html = response.read()
        html = html.decode('utf-8')
        #print('html '+html)
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
            self._recoder.warning(self._file_name+' was missing!')
            return 'none'
        
    def record(self, ip):
        try:
            with open(self._file_name,'wb+') as data:
                #print('write ip '+str(ip)+"in "+self._file_name)
                pickle.dump(ip, data)
#             with open(self._file_name,'rb') as data:
#                 ip_addr = pickle.load(data)
                #print('reload ip '+str(ip_addr)+"in "+self._file_name)

        except IOError:
            self._recoder.warning(self._file_name+' was missing!')
            pass
            #print('The ip_addr.pickle is missing!')

def chekcIp(mail_sender, ip_manager):
    newIp = ip_manager.getPublicIP()
    recoder =  RecoderFactry().getRecoder("info", "check ip")
    #print("check ip"+newIp)

    if newIp != ip_manager.getRecord():
        recoder.info('IP Changed !!! send email')
        mail_sender.setSubject('IP Changed!')
        mail_sender.send('system start at ip '+str(newIp)+" time "+getLocalTime())
        ip_manager.record(newIp)
        
    t = threading.Timer(10.0, chekcIp(mail_sender, ip_manager))
    t.start()
    
def getLocalTime():
    return time.strftime('%Y-%m-%d,%H:%M:%S',time.localtime(time.time()))
    
if __name__ == '__main__':
    curdir = os.path.curdir
    if os.path.exists(curdir+'/pi-guard-db') == False:
        os.mkdir('pi-guard-db')
        
    db_path = curdir+'/pi-guard-db/'
    
    print("system start")
    recoder =  RecoderFactry().getRecoder("info", "main")
    recoder.info('system start !!!')
    
    sender = MailSender()
    sender.setFrom(from_addr)
    sender.setTo(to_addr)
    sender.send('system start'+getLocalTime())
    manager = IPManager(db_path)

    t = threading.Timer(500.0, chekcIp(sender, manager))
    t.start()
    
#     if newIp != manager.getRecord():
#         sender.setSubject('IP Changed!')
#         sender.send('system start at ip '+list2Str(newIp)+'')
#         manager.record(newIp)
        
    