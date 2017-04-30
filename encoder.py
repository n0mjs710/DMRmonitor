from __future__ import print_function

import socket

from cPickle import dumps as pickle_dumps
from pprint import pprint
from hmac import new as hmac_new
from hashlib import sha1

from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from twisted.internet import task

BRIDGES = {
    'KANSAS': [
            {'SYSTEM': 'LAWRENCE',     'TS': 2, 'TGID': 3120,  'ACTIVE': True, 'TIMEOUT': .5, 'TO_TYPE': 'ON',  'ON': [2,], 'OFF': [9,]},
            {'SYSTEM': 'C-BRIDGE',     'TS': 2, 'TGID': 3120,  'ACTIVE': True, 'TIMEOUT': 2, 'TO_TYPE': 'NONE',  'ON': [2,], 'OFF': [9,]},
            {'SYSTEM': 'BRANDMEISTER', 'TS': 2, 'TGID': 3120,  'ACTIVE': True, 'TIMEOUT': 2, 'TO_TYPE': 'NONE',  'ON': [2,], 'OFF': [9,]},
        ],
    'BYRG': [
            {'SYSTEM': 'LAWRENCE',     'TS': 1, 'TGID': 3100,  'ACTIVE': True, 'TIMEOUT': 2, 'TO_TYPE': 'NONE', 'ON': [3,], 'OFF': [8,]},
            {'SYSTEM': 'BRANDMEISTER', 'TS': 2, 'TGID': 31201, 'ACTIVE': True, 'TIMEOUT': 2, 'TO_TYPE': 'NONE', 'ON': [3,], 'OFF': [8,]},
        ],
    'ENGLISH': [
            {'SYSTEM': 'LAWRENCE', 'TS': 1, 'TGID': 13,    'ACTIVE': True, 'TIMEOUT': 2, 'TO_TYPE': 'NONE', 'ON': [4,], 'OFF': [7,]},
            {'SYSTEM': 'C-BRIDGE', 'TS': 1, 'TGID': 13,    'ACTIVE': True, 'TIMEOUT': 2, 'TO_TYPE': 'NONE', 'ON': [4,], 'OFF': [7,]},
        ]
}

ADDR = '127.0.0.1'
PORT = 1234
name = 'jimmy'
monitor = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

salt = 'myPassword'
data = pickle_dumps(BRIDGES)
digest = hmac_new(salt,data[:10],sha1).digest()

print(repr(digest))
message = '\x11'+digest+data

class STAT_SENDER(DatagramProtocol):
    def __init__(self, name):
        pass
    
    def startProtocol(self):
        pass
    
    def datagramReceived(self, data, (host, port)):
        opcode = data[0:1]
        auth_hash = data[1:21]
        pobject= data[21:]
        check_hash = hmac_new(salt,data[21:31],sha1).digest()
        dictobject = pickle_loads(pobject)
        
        print('OPCODE: {}'.format(repr(opcode)))
        print('AUTH  HASH: {}'.format(repr(auth_hash)))
        print('CHECK HASH: {}'.format(repr(check_hash)))
        auth = compare_digest(auth_hash, check_hash)
        if auth:
            print('Authentication Succeeded:')
            pprint(dictobject)
        else:
            print('Authentication Failed - Message Discarded')

if __name__ == '__main__':
    sender = STAT_SENDER(name)
    reactor.listenUDP(PORT, sender, ADDR)
    reactor.run()

