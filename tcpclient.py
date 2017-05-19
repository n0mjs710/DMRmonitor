from __future__ import print_function

import logging
import sys

from twisted.internet.protocol import ReconnectingClientFactory, Protocol
from twisted.protocols.basic import NetstringReceiver
from twisted.internet import reactor, task
from twisted.web.server import Site
from twisted.web.static import File
from twisted.web.resource import Resource

from autobahn.twisted.websocket import WebSocketServerProtocol, WebSocketServerFactory

from pprint import pprint
from time import time, strftime, localtime
from cPickle import loads
from binascii import b2a_hex as h
from dmr_utils.utils import int_id, get_alias, try_download, mk_id_dict, get_alias_list
from os.path import getmtime

from config import *
from ipsc_const import *

OPCODE = {
    'CONFIG_REQ': '\x00',
    'CONFIG_SND': '\x01',
    'BRIDGE_REQ': '\x02',
    'BRIDGE_SND': '\x03',
    'CONFIG_UPD': '\x04',
    'BRIDGE_UPD': '\x05',
    'LINK_EVENT': '\x06',
    'BRDG_EVENT': '\x07',
    'RCM_SND':    '\x08'
    }


def get_template(_file):
    with open(_file, 'r') as html:
        return html.read()

#
# REPEATER CALL MONITOR (RCM) PACKET PROCESSING
#
def call_mon_status(self, _payload):
    _payload = _data.split(',', 1)
    _name = _payload[0]
    _data = _payload[1]
    if not status:
        return
    _source =   _data[1:5]
    _ipsc_src = _data[5:9]
    _seq_num =  _data[9:13]
    _ts =       _data[13]
    _status =   _data[15] # suspect [14:16] but nothing in leading byte?
    _rf_src =   _data[16:19]
    _rf_tgt =   _data[19:22]
    _type =     _data[22]
    _prio =     _data[23]
    _sec =      _data[24]
    
def call_mon_rpt(self, _payload):
    _payload = _data.split(',', 1)
    _name = _payload[0]
    _data = _payload[1]
    if not rpt:
        return
    _source    = _data[1:5]
    _ts1_state = _data[5]
    _ts2_state = _data[6]
    
def call_mon_nack(self, _payload):
    _payload = _data.split(',', 1)
    _name = _payload[0]
    _data = _payload[1]
    if not nack:
        return
    _source = _data[1:5]
    _nack =   _data[5]


#
# TABLE TEMPLATE FOR DMRLINK STATUS
#    
def build_dmrlink_table():
    _cnow = strftime('%Y-%m-%d %H:%M:%S', localtime(time()))
    table =  '<p>Table Last Updated: {} <br>'.format(_cnow)
    table += 'Data Last Updated: {}</p>'.format(CONFIG_RX)

    table += '<style>table, td, th {border: .5px solid black; padding: 2px; border-collapse: collapse}</style>'
    
    for ipsc in CONFIG:
        master = CONFIG[ipsc]['LOCAL']['MASTER_PEER']
        
        table += '<table style="width:90%; font: 10pt arial, sans-serif">'
        
        table += '<colgroup>\
            <col style="width: 30%" />\
            <col style="width: 15%" />\
            <col style="width: 15%" />\
            <col style="width: 15%" />\
            <col style="width: 10%" />\
            <col style="width: 5%" />\
            <col style="width: 5%" />\
            <col style="width: 5%" />\
            </colgroup>'
        
        table += '<caption>{} '.format(ipsc)
        if master:
            table += '(master)'
        else:
            table += '(peer)'
        table +='</caption>'
        
        table += '<tr><th rowspan="2">Alias</th>\
                      <th rowspan="2">Type</th>\
                      <th rowspan="2">Radio ID</th>\
                      <th rowspan="2">IP Address</th>\
                      <th rowspan="2">Status</th>\
                      <th colspan="3">Keep Alives</th></tr>\
                  <tr><th>Sent</th><th>Received</th><th>Missed</th></tr>'
                
        if not master:
            stat = CONFIG[ipsc]['MASTER']['STATUS']
            
            if stat['CONNECTED'] == True:
                active = '<td bgcolor="#00FF00">Connected</td>'
            elif stat['CONNECTED'] == False:
                active = '<td bgcolor="#FF0000">Disconnected</td>'
                
            alias_list = get_alias_list(CONFIG[ipsc]['MASTER']['RADIO_ID'], peer_ids, 'CALLSIGN', 'CITY')
            alias = alias_list[1] + ', ' + alias_list[2]
            
            table += '<tr><td>{}</td><td>Master</td><td>{}</td><td>{}</td>{}<td>{}</td><td>{}</td><td>{}</td></tr>'.format(\
                    alias,\
                    str(int_id(CONFIG[ipsc]['MASTER']['RADIO_ID'])).rjust(8,'0'),\
                    CONFIG[ipsc]['MASTER']['IP'],\
                    active,\
                    stat['KEEP_ALIVES_SENT'],\
                    stat['KEEP_ALIVES_RECEIVED'],\
                    stat['KEEP_ALIVES_MISSED'],)
    
        if master:
            for peer in CONFIG[ipsc]['PEERS']:
                stat = CONFIG[ipsc]['PEERS'][peer]['STATUS']
                
                if stat['CONNECTED'] == True:
                    active = '<td bgcolor="#00FF00">Connected</td>'
                elif stat['CONNECTED'] == False:
                    active = '<td bgcolor="#FF0000">Disconnected</td>'
                
                alias_list = get_alias_list(peer, peer_ids, 'CALLSIGN', 'CITY')
                alias = alias_list[1] + ', ' + alias_list[2]
                
                table += '<tr><td>{}</td><td>Peer</td><td>{}</td><td>{}</td>{}<td>n/a</td><td>{}</td><td>n/a</td></tr>'.format(\
                    alias,\
                    str(int_id(peer)).rjust(8,'0'),\
                    CONFIG[ipsc]['PEERS'][peer]['IP'],\
                    active,\
                    stat['KEEP_ALIVES_RECEIVED'])
                
        else:
            for peer in CONFIG[ipsc]['PEERS']:
                stat = CONFIG[ipsc]['PEERS'][peer]['STATUS']
                
                if stat['CONNECTED'] == True:
                    active = '<td bgcolor="#00FF00">Connected</td>'
                elif stat['CONNECTED'] == False:
                    active = '<td bgcolor="#FF0000">Disconnected</td>'
                
                alias_list = get_alias_list(peer, peer_ids, 'CALLSIGN', 'CITY')
                alias = alias_list[1] + ', ' + alias_list[2]
                
                if peer != CONFIG[ipsc]['LOCAL']['RADIO_ID']:
                    table += '<tr><td>{}</td><td>Peer</td><td>{}</td><td>{}</td>{}<td>{}</td><td>{}</td><td>{}</td></tr>'.format(\
                        alias,\
                        str(int_id(peer)).rjust(8,'0'),\
                        CONFIG[ipsc]['PEERS'][peer]['IP'],\
                        active,\
                        stat['KEEP_ALIVES_SENT'],\
                        stat['KEEP_ALIVES_RECEIVED'],\
                        stat['KEEP_ALIVES_MISSED'])
        table += '</table><br>'
    return table


#
# TABLE TEMPLATE FOR CONFBRIDGE BRIDGE GROUP STATUS
#
def build_bridge_table():
    _now = time()
    _cnow = strftime('%Y-%m-%d %H:%M:%S', localtime(_now))
        
    table =  '<p>Table Last Updated: {}<br>'.format(_cnow)
    table += 'Data Last Updated: {}</p>'.format(BRIDGES_RX)
    
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

#
# BUILD DMRLINK AND CONFBRIDGE TABLES FROM CONFIG/BRIDGES DICTS - THIS IS A TIMED CALL
#
def build_stats():
    if CONFIG:
        table = 'd' + build_dmrlink_table()
        dashboard_server.broadcast(table)
    if BRIDGES:
        table = 'b' + build_bridge_table()
        dashboard_server.broadcast(table)
 

#
# PROCESS IN COMING MESSAGES AND TAKE THE CORRECT ACTION DEPENING ON THE OPCODE
#
def process_message(_message):
    global CONFIG, BRIDGES, CONFIG_RX, BRIDGES_RX
    opcode = _message[:1]
    if opcode == OPCODE['CONFIG_SND']:
        logging.debug('got CONFIG_SND opcode')
        CONFIG = load_dictionary(_message)
        CONFIG_RX = strftime('%Y-%m-%d %H:%M:%S', localtime(time()))
    elif opcode == OPCODE['BRIDGE_SND']:
        logging.debug('got BRIDGE_SND opcode')
        BRIDGES = load_dictionary(_message)
        BRIDGES_RX = strftime('%Y-%m-%d %H:%M:%S', localtime(time()))
    elif opcode == OPCODE['LINK_EVENT']:
        logging.info('LINK_EVENT Received: {}'.format(repr(_message[1:])))
    elif opcode == OPCODE['RCM_SND']:
        pass
        #logging.info('RCM Message Received: {}'.format(repr(_message[1:])))
        #dashboard_server.broadcast('l' + repr(_message[1:]))
    elif opcode == OPCODE['BRDG_EVENT']:
        logging.info('BRIDGE EVENT: {}'.format(repr(_message[1:])))
        dashboard_server.broadcast('l' + repr(_message[1:]))
    else:
        logging.info('got unknown opcode: {}, message: {}'.format(repr(opcode), repr(_message[1:])))


def load_dictionary(_message):
    data = _message[1:]
    return loads(data)
    logging.debug('Successfully decoded dictionary')

#
# COMMUNICATION WITH THE DMRLINK INSTANCE
#
class report(NetstringReceiver):
    def __init__(self):
        pass

    def connectionMade(self):
        pass

    def connectionLost(self, reason):
        pass
        
    def stringReceived(self, data):
        process_message(data)


class reportClientFactory(ReconnectingClientFactory):
    def __init__(self):
        pass
        
    def startedConnecting(self, connector):
        logging.info('Initiating Connection to Server.')
        if 'dashboard_server' in locals() or 'dashboard_server' in globals():
            dashboard_server.broadcast('q' + 'Connection to DMRlink Established')

    def buildProtocol(self, addr):
        logging.info('Connected.')
        logging.info('Resetting reconnection delay')
        self.resetDelay()
        return report()

    def clientConnectionLost(self, connector, reason):
        logging.info('Lost connection.  Reason: %s', reason)
        ReconnectingClientFactory.clientConnectionLost(self, connector, reason)
        dashboard_server.broadcast('q' + 'Connection to DMRlink Lost')

    def clientConnectionFailed(self, connector, reason):
        logging.info('Connection failed. Reason: %s', reason)
        ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)


#
# WEBSOCKET COMMUNICATION WITH THE DASHBOARD CLIENT
#
class dashboard(WebSocketServerProtocol):
        
    def onConnect(self, request):
        logging.info('Client connecting: %s', request.peer)

    def onOpen(self):
        logging.info('WebSocket connection open.')
        self.factory.register(self)
        self.sendMessage('d' + build_dmrlink_table())
        self.sendMessage('b' + build_bridge_table())

    def onMessage(self, payload, isBinary):
        if isBinary:
            logging.info('Binary message received: %s bytes', len(payload))
        else:
            logging.info('Text message received: %s', payload.decode('utf8'))

    def connectionLost(self, reason):
        WebSocketServerProtocol.connectionLost(self, reason)
        self.factory.unregister(self)

    def onClose(self, wasClean, code, reason):
        logging.info('WebSocket connection closed: %s', reason)


class dashboardFactory(WebSocketServerFactory):

    def __init__(self, url):
        WebSocketServerFactory.__init__(self, url)
        self.clients = []

    def register(self, client):
        if client not in self.clients:
            logging.info('registered client %s', client.peer)
            self.clients.append(client)

    def unregister(self, client):
        if client in self.clients:
            logging.info('unregistered client %s', client.peer)
            self.clients.remove(client)

    def broadcast(self, msg):
        logging.debug('broadcasting message to: %s', self.clients)
        for c in self.clients:
            c.sendMessage(msg.encode('utf8'))
            logging.debug('message sent to %s', c.peer)
            
#
# STATIC WEBSERVER
#
class web_server(Resource):
    isLeaf = True
    def render_GET(self, request):
        logging.info('static website requested: %s', request)
        if request.uri == '/':
            return index_html
        else:
            return 'Bad request'


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    # Make Alias Dictionaries
    peer_ids = mk_id_dict(PATH, PEER_FILE)
    if peer_ids:
        logging.info('ID ALIAS MAPPER: peer_ids dictionary is available')
        
    subscriber_ids = mk_id_dict(PATH, SUBSCRIBER_FILE)
    if subscriber_ids:
        logging.info('ID ALIAS MAPPER: subscriber_ids dictionary is available')
    
    talkgroup_ids = mk_id_dict(PATH, TGID_FILE)
    if talkgroup_ids:
        logging.info('ID ALIAS MAPPER: talkgroup_ids dictionary is available')
    
    local_ids = mk_id_dict(PATH, LOCAL_FILE)
    if local_ids:
        logging.info('ID ALIAS MAPPER: local_ids dictionary is available')
        peer_ids.update(local_ids)
        subscriber_ids.update(local_ids)
    
    # Create Static Website index file
    index_html = get_template('index_template.html')
    
    # Start update loop
    update_stats = task.LoopingCall(build_stats)
    update_stats.start(FREQUENCY)
    
    # Connect to DMRlink
    reactor.connectTCP(DMRLINK_IP, DMRLINK_PORT, reportClientFactory())
    
    # Create websocket server to push content to clients
    dashboard_server = dashboardFactory('ws://*:9000')
    dashboard_server.protocol = dashboard
    reactor.listenTCP(9000, dashboard_server)

    # Create static web server to push initial index.html
    website = Site(web_server())
    reactor.listenTCP(WEB_SERVER_PORT, website)

    reactor.run()