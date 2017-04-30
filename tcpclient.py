from __future__ import print_function

from twisted.internet.protocol import ReconnectingClientFactory, Protocol
from twisted.protocols.basic import NetstringReceiver

from twisted.internet import reactor

from hmac import new as hmac_new
from hashlib import sha1
from cPickle import loads

from pprint import pprint

SERVER_PORT = 4321

OPCODE = {
    'CONFIG_REQ': '\x00',
    'CONFIG_SND': '\x01',
    'BRIDGE_REQ': '\x02',
    'BRIDGE_SND': '\x03',
    'CONFIG_UPD': '\x04',
    'BRIDGE_UPD': '\x05',
    'LINK_EVENT': '\x06',
    'BRDG_EVENT': '\x07'
    }


def process_message(_message):
    opcode = _message[:1]
    if opcode == OPCODE['CONFIG_SND']:
        print('got CONFIG_SND opcode')
        decode_config(_message)
    elif opcode == OPCODE['BRIDGE_SND']:
        print('got BRIDGE_SND opcode')
        decode_bridge(_message)
    elif opcode == OPCODE['LINK_EVENT']:
        print('LINK_EVENT Received: {}'.format(repr(_message[1:])))
    else:
        print('got unknown opcode: {}, message: {}'.format(repr(opcode), repr(_message[1:])))
    
def decode_config(_message):
    opcode = _message[:1]
    data = _message[1:]
    CONFIG = loads(data)
    print('Successfully loaded CONFIG dictionary')
    
def decode_bridge(_message):
    opcode = _message[:1]
    data = _message[1:]
    BRIDGES = loads(data)
    print('Successfully loaded BRIDGES dictionary')

class report(NetstringReceiver):
    def __init__(self):
        pass

    def connectionMade(self):
        pass
        #self.sendString(OPCODE['CONFIG_REQ'])

    def connectionLost(self, reason):
        pass
        
    def stringReceived(self, data):
        process_message(data)

class reportClientFactory(ReconnectingClientFactory):
    def __init__(self):
        pass
        
    def startedConnecting(self, connector):
        print('Initiating Connection to Server.')

    def buildProtocol(self, addr):
        print('Connected.')
        print('Resetting reconnection delay')
        self.resetDelay()
        return report()

    def clientConnectionLost(self, connector, reason):
        print('Lost connection.  Reason:', reason)
        ReconnectingClientFactory.clientConnectionLost(self, connector, reason)

    def clientConnectionFailed(self, connector, reason):
        print('Connection failed. Reason:', reason)
        ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)


if __name__ == '__main__':
        reactor.connectTCP('127.0.0.1', 4321, reportClientFactory())
        reactor.run()