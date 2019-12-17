# -*- coding: utf-8 -*-
__author__ = "vipksmosar"
__credits__ = ["vipksmosar"]
__version__ = "0.0.1"
__email__ = "admin@npfx.ru"
__status__ = "Sigma-test"

import time
import os
import sys

from tqdm import tqdm
import pandas as pd
import threading
import socket
import logging
import logging.config
import argparse
import subprocess
from support.import_file import import_file
from support.ip_range import create_IP_pool


path=sys.path[0]

arg_parser = argparse.ArgumentParser(description='ports_scanner_by_IP_from_xlsx_file')
arg_parser.add_argument('--filein', type=str, help="--filein 'C:/CSV/srv_vm2.xlsx'")
arg_parser.add_argument('--fileout', type=str, help="--fileout 'C:/CSV/HOSTS_VIRT_withScanned.csv'", default='out_file.csv')
arg_parser.add_argument('--ports',nargs='+', type=int, help="--ports 20 21 22 139 445 80 44")
arg_parser.add_argument('--ports_range',nargs='+', type=int, help="--ports_range 20 25", default=None)
arg_parser.add_argument('--ip_range', type=str, help="--ip_range 192.168.10.23-192.168.10.25", default=None)
arg_parser.add_argument('--IPcol', type=str, help="--IPcol 'IP' - default 'IP'", default='IP')
arg_parser.add_argument('--OneHost', type=bool, help="--OneHost True, default False", default=False)
arg_parser.add_argument('--Ping', type=bool, help="--Ping True, default False", default=False)
arg_parser.add_argument('--DNS', type=bool, help="--DNS True, default False", default=False)
args = arg_parser.parse_args()

logging.config.fileConfig(os.path.join(path,'logger.conf'), defaults={'logfilename': os.path.join(path,'portscan.log')})
logger = logging.getLogger('scanner')

class scanner:
    def __init__(self,  port_list, file_in, file_out, IP_col, flag_many_host, port_range, ip_range, flag_ping, flag_dns):
        self.IP_col = IP_col
        self.port_list = port_list
        self.file_in = file_in
        self.file_out = file_out
        self.flag_many_host = flag_many_host
        self.flag_ping = flag_ping
        self.ip_range = ip_range
        self.port_range = port_range
        self.flag_dns = flag_dns
    
    def __import_file (self):
        file = import_file(self.file_in)
        DF = file.read()
        IP_list = DF[self.IP_col].tolist()
        return IP_list
    
    def __ip_range (self):
        IP_range = create_IP_pool(self.ip_range)
        IP_list = IP_range.IP()
        return IP_list
    
    def __port_range (self):
        port_start = self.port_range[0]
        port_end = self.port_range[1]
        port_list = [i for i in range(port_start, port_end+1)]
        return port_list
    
    def scan (self):
        if self.ip_range:
            IP = self.__ip_range()
        else:
            IP = self.__import_file()  
        if self.flag_ping:
            icmp_ping = scann_icmp(IP, self.file_out)
            icmp_ping.start_scann()
        else:
            if self.port_range:
                ports = self.__port_range()
            else:
                ports = self.port_list
            print(self.file_out)
            tcp_ports = scann_ports(IP, ports, self.file_out, self.flag_dns)
            tcp_ports.start_scann()

class scann_ports(scanner):
    
    def __init__ (self, IP, ports, file_out, flag_dns):
        self.IP = IP
        self.ports = ports        
        self.file_out = file_out
        self.flag_dns = flag_dns
        
    def __to_IP (self, ip):
        try:
            dns = socket.gethostbyaddr(ip)[0]
            return dns
        except:
            return ip
    
    def __scan_hosts_ports(self, ip_host, port_to_scan):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.5)
        try:
            #try:
            #    ip_host = socket.gethostbyname(ip_host)
            #except Exception as E:
            #    self.list_of_scanned_hosts_not_resolved.append(ip_host)
            #    return None
            connection = s.connect((ip_host, port_to_scan))
            self.list_of_scanned_hosts.append(ip_host)
        except:
            self.list_of_scanned_hosts_false.append(ip_host)
            
    def __to_file (self, list_of_hosts, list_of_hosts_false, port):
        Data_hosts = pd.DataFrame(columns=[])
        Data_hosts_false = pd.DataFrame(columns=[])
        logger.info('create result DF: acess '+ str(len(list_of_hosts)) + ' , denied ' + str(len(list_of_hosts_false)))
        Data_hosts['IP'] = list(set(list_of_hosts))
        if self.flag_dns:
            logger.info('start to dns')
            Data_hosts['Name']=Data_hosts['IP'].apply(self.__to_IP)
            
        Data_hosts['port_number'] = port
        Data_hosts['result'] = 'ACESS'
        Data_hosts_false['IP'] = list(set(list_of_hosts_false))
        if self.flag_dns:
            logger.info('start to dns')
            Data_hosts_false['Name']=Data_hosts_false['IP'].apply(self.__to_IP)
        Data_hosts_false['port_number'] = port
        Data_hosts_false['result'] = 'DENIED'
        logger.info('start out DF')
        
        self.list_of_scanned_hosts_not_resolved
        
        DF = pd.concat([Data_hosts_false, Data_hosts])
        if os.path.isfile(self.file_out)==True:
            DF.to_csv(self.file_out, mode='a', sep='\t', encoding='utf-16', header=False, index=False)
        else:
            DF.to_csv(self.file_out, sep='\t', encoding='utf-16', index=False)
        logger.info(str(len(list_of_hosts))+' with open '+str(port))
        
    def start_scann(self):
        logger.info(str(self.IP)+str(self.ports))
        logger.info('SCAN START')
        for port in self.ports:
            self.list_of_scanned_hosts = []
            self.list_of_scanned_hosts_false = []
            self.list_of_scanned_hosts_not_resolved = []
            if type(self.IP) == list:
                for i in tqdm(self.IP):
                    thread_port = threading.Thread(target=self.__scan_hosts_ports, kwargs={'ip_host': i, 'port_to_scan': port})
                    thread_port.start()
                    while threading.active_count()>900 :
                        time.sleep(0.5)
            else:
                thread_port = threading.Thread(target=self.__scan_hosts_ports, kwargs={'ip_host': self.IP, 'port_to_scan': port})
                thread_port.start()  
                thread_port.join()
            while thread_port.isAlive() == True:
                time.sleep(1)
            self.__to_file( self.list_of_scanned_hosts, self.list_of_scanned_hosts_false, port)
        logger.info('SCAN IS OVER')
        
class scann_icmp(scanner):
    
    def __init__ (self, IP, file_out):
        self.IP = IP
        self.file_out = file_out
    
    def __ping (self, host):
        
        if sys.platform == 'linux':
            response = subprocess.call(["ping -c 1 " + host], shell=True,stdout=subprocess.PIPE)
            if response == 0:
                self.list_of_hosts_on.append(host)
            else:
                self.list_of_hosts_off.append(host)
        elif sys.platform == 'win32':
            response = subprocess.call("ping -n 1 " + host, shell=True,stdout=subprocess.PIPE)
            if response == 0:
                self.list_of_hosts_on.append(host)
            else:
                self.list_of_hosts_off.append(host)
        else:
            raise('Unknown OS')
    
    def __to_file (self, DF):
        if os.path.isfile(self.file_out)==True:
            DF.to_csv(self.file_out, mode='a', sep='\t', encoding='utf-16', header=False, index=False)
        else:
            DF.to_csv(self.file_out, sep='\t', encoding='utf-16', index=False)
        logger.info(str(len(self.list_of_hosts_on))+' ping OK')
        logger.info(str(len(self.list_of_hosts_on)+len(self.list_of_hosts_off))+' all in file')
            
    
    def start_scann(self):
        self.list_of_hosts_on = []
        self.list_of_hosts_off = []
        logger.info(str(self.IP))
        if type(self.IP) == list:
            for i in tqdm(self.IP):
                thread_icmp = threading.Thread(target=self.__ping, kwargs={'host': i})
                thread_icmp.start()
                while threading.active_count()>700 :
                    time.sleep(0.5)
        else:
            thread_icmp = threading.Thread(target=self.__ping, kwargs={'host': self.IP})
            thread_icmp.start()
        while thread_icmp.isAlive() == True:
            time.sleep(15)
        logger.info('all pings is over')
        DF_out_off = pd.DataFrame(columns={'host', 'result'})
        DF_out_off.host = self.list_of_hosts_off
        DF_out_off.result = 'FAIL PING'
        DF_out_on = pd.DataFrame(columns={'host', 'result'})
        DF_out_on.host = self.list_of_hosts_on
        DF_out_on.result = 'OK'
        DF = pd.concat([DF_out_off, DF_out_on])
        self.__to_file(DF)

        
    
scan_start = scanner(args.ports, args.filein, args.fileout, args.IPcol, args.OneHost, args.ports_range, args.ip_range, args.Ping, args.DNS)
scan_start.scan()
