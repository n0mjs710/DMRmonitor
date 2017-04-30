from __future__ import print_function

from twisted.internet.protocol import Factory, Protocol
from twisted.internet import reactor

from hmac import new as hmac_new
from hashlib import sha1

STATS = 'network'
STATS_PORT = 8000
MAX_CLIENTS = 2
SALT = 'jimmy'


class report(Protocol):
    def __init__(self):
        pass

    def connectionMade(self):
        report_server.clients.append(self)
        print(self.transport.getPeer())

    def connectionLost(self, reason):
        print('{} connection lost'.format(self.transport.getPeer()))
        report_server.clients.remove(self)

    def dataReceived(self, data):
        if data == 'test\r\n':
            for client in report_server.clients:
                client.message(str(client)+'\n')
                client.message(authhash(repr(client))+'\n')
                client.message(str(MAX_CLIENTS)+'\n')
    
    def message(self, message):
        self.transport.write(message)


class reportFactory(Factory):
    def __init__(self):
        pass
        
    def buildProtocol(self, addr):
        if len(report_server.clients) < MAX_CLIENTS:
            return report()
        else:
            return None


if __name__ == '__main__':
    if STATS == 'network': 
        
        REP_OPC = {}
        
        def authhash(_data):
            return hmac_new(SALT,_data[:10],sha1).digest()
    
        report_server = reportFactory()
        report_server.clients = []
    
        reactor.listenTCP(8000, reportFactory())
        reactor.run()