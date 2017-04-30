from __future__ import print_function

from cPickle import loads as pickle_loads
from cPickle import dumps as pickle_dumps
from pprint import pprint

from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from twisted.internet import task

from hmac import new as hmac_new
from hmac import compare_digest
from hashlib import sha1

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

OPCODES = {
    'RX_REG': '\x00',
    'REG_REPLY': '\x01',
    'MAIN_STRUCK': '\x10',
    'BRIDGE_STRUCT': '\x11',
}

# THIS END
name = 'jimmy'
ADDR = '127.0.0.1'
PORT = 1234
RETRY_INTERVAL = 10

# REMOTE END
SALT = 'myPassword'
RMT_ADDR = '127.0.0.1'
RMT_PORT = 2345

# TEST DATA
data = pickle_dumps(BRIDGES)
digest = hmac_new(SALT,data[:10],sha1).digest()

print(repr(digest))
message = '\x11'+digest+data




class STAT_ENGINE(DatagramProtocol):
    def __init__(self, name):
        pass
        
    def startProtocol(self):
        self._maintenance = task.LoopingCall(self.maintenance_loop)
        self._maintenance_loop = self._maintenance.start(RETRY_INTERVAL)
        
        self.transport.write(message, (ADDR, PORT))
        
        
    def maintenance_loop(self):
        print('SYSTEM NOT CONNECTED')
    
    def datagramReceived(self, data, (host, port)):
        opcode = data[0:1]
        auth_hash = data[1:21]
        pobject= data[21:]
        check_hash = hmac_new(SALT,data[21:31],sha1).digest()
        
        try:
            dictobject = pickle_loads(pobject)
        except:
            print('could not load data as pickle')    
        
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
    receiver = STAT_ENGINE(name)
    reactor.listenUDP(PORT, receiver, ADDR)
    reactor.run()