from __future__ import print_function

from twisted.internet.protocol import ReconnectingClientFactory, Protocol
from twisted.protocols.basic import NetstringReceiver

from twisted.internet import reactor, task

from pprint import pprint
from time import time, strftime, localtime
#from hmac import new as hmac_new
from hashlib import sha1
from cPickle import loads
from binascii import b2a_hex as h
from dmr_utils.utils import int_id, get_alias
from os.path import getmtime 

from pprint import pprint

DMRLINK_HTML    = '../dmrlink_stats.html'
CONFBRIDGE_HTML = '../confbridge_stats.html'
CONFIG = {}
CONFIG_RX = ''
BRIDGES = {}
BRIDGES_RX = ''
SERVER_PORT = 4321
FREQUENCY = 10
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

def write_file(_file, _data):
    try:
        with open(_file, 'w') as file:
            file.write(_data)
            file.close()
    except IOError as detail:
        print('I/O Error: {}'.format(detail))
    except EOFError:
        print('EOFError')

def build_dmrlink_table():
    _cnow = strftime('%Y-%m-%d %H:%M:%S', localtime(time()))
    table =  'Table Last Updated: {} <br>'.format(_cnow)
    table += 'Data Last Updated: {} <br>'.format(CONFIG_RX)

    table += '<style>table, td, th {border: .5px solid black; padding: 2px; border-collapse: collapse}</style>'
    
    for ipsc in CONFIG:
        stat = CONFIG[ipsc]['MASTER']['STATUS']
        master = CONFIG[ipsc]['LOCAL']['MASTER_PEER']
        
        table += '<table style="width:90%; font: 10pt arial, sans-serif">'
        
        table += '<colgroup>\
            <col style="width: 10%" />\
            <col style="width: 20%" />\
            <col style="width: 20%" />\
            <col style="width: 10%" />\
            <col style="width: 15%" />\
            <col style="width: 15%" />\
            <col style="width: 10%" />\
            </colgroup>'
        
        table += '<caption>{} '.format(ipsc)
        if master:
            table += '(master)'
        else:
            table += '(peer)'
        table +='</caption>'
        
        table += '<tr><th rowspan="2">Type</th>\
                <th rowspan="2">Radio ID</th>\
                <th rowspan="2">IP Address</th>\
                <th rowspan="2">Connected</th>\
                <th colspan="3">Keep Alives</th></tr>\
                <tr><th>Sent</th><th>Received</th><th>Missed</th></tr>'
                
        if not master:
            table += '<tr><td>Master</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>'.format(\
                    str(int_id(CONFIG[ipsc]['MASTER']['RADIO_ID'])).rjust(8,'0'),\
                    CONFIG[ipsc]['MASTER']['IP'],\
                    stat['CONNECTED'],\
                    stat['KEEP_ALIVES_SENT'],\
                    stat['KEEP_ALIVES_RECEIVED'],\
                    stat['KEEP_ALIVES_MISSED'],)
    
        if master:
            for peer in CONFIG[ipsc]['PEERS']:
                stat = CONFIG[ipsc]['PEERS'][peer]['STATUS']
                table += '<tr><td>Peer</td><td>{}</td><td>{}</td><td>{}</td><td>n/a</td><td>{}</td><td>n/a</td></tr>'.format(\
                    str(int_id(peer)).rjust(8,'0'),\
                    CONFIG[ipsc]['PEERS'][peer]['IP'],\
                    stat['CONNECTED'],\
                    stat['KEEP_ALIVES_RECEIVED'])
                
        else:
            for peer in CONFIG[ipsc]['PEERS']:
                stat = CONFIG[ipsc]['PEERS'][peer]['STATUS']
                if peer != CONFIG[ipsc]['LOCAL']['RADIO_ID']:
                    table += '<tr><td>Peer</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>'.format(\
                        str(int_id(peer)).rjust(8,'0'),\
                        CONFIG[ipsc]['PEERS'][peer]['IP'],\
                        stat['CONNECTED'],\
                        stat['KEEP_ALIVES_SENT'],\
                        stat['KEEP_ALIVES_RECEIVED'],\
                        stat['KEEP_ALIVES_MISSED'])
        table += '</table><br>'
    return table

def build_bridge_table():
    _now = time()
    _cnow = strftime('%Y-%m-%d %H:%M:%S', localtime(_now))
        
    table =  'Table Last Updated: {}<br>'.format(_cnow)
    table += 'Data Last Updated: {}<br>'.format(BRIDGES_RX)
    
    #style="font: 10pt arial, sans-serif;"
    
    for bridge in BRIDGES:
        table += '<style>table, td, th {border: .5px solid black; padding: 2px; border-collapse: collapse}</style>'
        table += '<table style="width:90%; font: 10pt arial, sans-serif">'    
        table += '<colgroup>\
            <col style="width: 20%" />\
            <col style="width: 5%"  />\
            <col style="width: 5%"  />\
            <col style="width: 10%" />\
            <col style="width: 10%" />\
            <col style="width: 10%" />\
            <col style="width: 10%" />\
            <col style="width: 10%" />\
            <col style="width: 10%" />\
            </colgroup>'
        table += '<caption>{}</caption>'.format(bridge)
        table += '<tr><th>System</th>\
                      <th>Slot</th>\
                      <th>TGID</th>\
                      <th>Status</th>\
                      <th>Timeout</th>\
                      <th>Timeout Action</th>\
                      <th>ON Triggers</th>\
                      <th>OFF Triggers</th></tr>'
        
        
        for system in BRIDGES[bridge]:
            on = ''
            off = ''
            active = '<td bgcolor="#FFFF00">Unknown</td>'
            
            if system['TO_TYPE'] == 'ON' or system['TO_TYPE'] == 'OFF':
                if system['TIMER'] - _now > 0:
                    exp_time = int(system['TIMER'] - _now)
                else:
                    exp_time = 'Expired'
                if system['TO_TYPE'] == 'ON':
                    to_action = 'Turn OFF'
                else:
                    to_action = 'Turn ON'
            else:
                exp_time = 'N/A'
                to_action = 'None'
            
            if system['ACTIVE'] == True:
                active = '<td bgcolor="#00FF00">Connected</td>'
            elif system['ACTIVE'] == False:
                active = '<td bgcolor="#FF0000">Disconnected</td>'
                
            for trigger in system['ON']:
                on += str(int_id(trigger)) + ' '
                
            for trigger in system['OFF']:
                off += str(int_id(trigger)) + ' '

            table += '<tr> <td>{}</td> <td>{}</td> <td>{}</td> {} <td>{}</td> <td>{}</td> <td>{}</td> <td>{}</td> </tr>'.format(\
                    system['SYSTEM'],\
                    system['TS'],\
                    int_id(system['TGID']),\
                    active,\
                    exp_time,\
                    to_action,\
                    on,\
                    off)

        table += '</table><br>'
    return table
        
def build_stats():
    if CONFIG:
        table = build_dmrlink_table()
        write_file(DMRLINK_HTML, table)
    if BRIDGES:
        table = build_bridge_table()
        write_file(CONFBRIDGE_HTML, table)
         
def process_message(_message):
    global CONFIG, BRIDGES, CONFIG_RX, BRIDGES_RX
    opcode = _message[:1]
    if opcode == OPCODE['CONFIG_SND']:
        print('got CONFIG_SND opcode')
        CONFIG = load_dictionary(_message)
        CONFIG_RX = strftime('%Y-%m-%d %H:%M:%S', localtime(time()))
    elif opcode == OPCODE['BRIDGE_SND']:
        print('got BRIDGE_SND opcode')
        BRIDGES = load_dictionary(_message)
        BRIDGES_RX = strftime('%Y-%m-%d %H:%M:%S', localtime(time()))
    elif opcode == OPCODE['LINK_EVENT']:
        print('LINK_EVENT Received: {}'.format(repr(_message[1:])))
    else:
        print('got unknown opcode: {}, message: {}'.format(repr(opcode), repr(_message[1:])))
    
def load_dictionary(_message):
    data = _message[1:]
    return loads(data)
    print('Successfully decoded dictionary')

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
    update_stats = task.LoopingCall(build_stats)
    update_stats.start(FREQUENCY)
    reactor.connectTCP('127.0.0.1', 4321, reportClientFactory())
    reactor.run()