import re
import socket, struct

class create_IP_pool:

    def __init__ (self, IP_pool):
        self.IP_pool = IP_pool
    
    def __create_IP_range (self):
        list_ip = self.IP_pool.split('-')
        start = struct.unpack('>I', socket.inet_aton(list_ip[0]))[0]
        end = struct.unpack('>I', socket.inet_aton(list_ip[1]))[0]
        return [socket.inet_ntoa(struct.pack('>I', i)) for i in range(start, end+1)]
    
    def __change_str (self):
        if re.match(r'\d{,3}\.\d{,3}\.\d{,3}\.\d{,3}-\d{,3}\.\d{,3}\.\d{,3}\.\d{,3}', self.IP_pool) !=None:
            list_ip = self.__create_IP_range()
            return list_ip
        elif re.match(r'\d{,3}\.\d{,3}\.\d{,3}\.\d{,3}', self.IP_pool) != None and  re.search(r'\-', self.IP_pool)== None:
            list_ip = [self.IP_pool]
            return list_ip
        else:
            raise Exception ('Wrong ip addres or pool: ', self.IP_pool)
    
    def IP (self):
        if type(self.IP_pool) == list:
            out = self.IP_pool
        elif type(self.IP_pool) == str:
            out = self.__change_str()
        else:
            raise Exception ('Something wrong')
        return out
