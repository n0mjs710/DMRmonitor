#!/usr/bin/env python
#
###############################################################################
#   Copyright (C) 2016  Cortney T. Buffington, N0MJS <n0mjs@me.com>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software Foundation,
#   Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301  USA
###############################################################################

'''

THIS IS EXTREMELY IMPORTANT:

Using this program effectively requires that you make certain changes in
your dmrlink configuration. In order for this program to work correctly,
All systems must be configured with:

RCM: True
CON_APP: True

'''

from __future__ import print_function

# Standard modules
import logging
import sys

# Twisted modules
from twisted.internet.protocol import ReconnectingClientFactory, Protocol
from twisted.protocols.basic import NetstringReceiver
from twisted.internet import reactor, task
from twisted.web.server import Site
from twisted.web.static import File
from twisted.web.resource import Resource

# Autobahn provides websocket service under Twisted
from autobahn.twisted.websocket import WebSocketServerProtocol, WebSocketServerFactory

# Specific functions to import from standard modules
from pprint import pprint
from time import time, strftime, localtime
from cPickle import loads
from binascii import b2a_hex as h
from os.path import getmtime
from collections import deque

# Web templating environment
from jinja2 import Environment, PackageLoader, select_autoescape

# Utilities from K0USY Group sister project
from dmr_utils.utils import int_id, get_alias, try_download, mk_full_id_dict

# Configuration variables and IPSC constants
from config import *
from ipsc_const import *

# Opcodes for reporting protocol to DMRlink
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

# Global Variables:
CONFIG      = {}
CTABLE      = {}
BRIDGES     = {}
BTABLE      = {}
BTABLE['BRIDGES'] = {}
BRIDGES_RX  = ''
CONFIG_RX   = ''
LOGBUF      = deque(100*[''], 100)
RED         = '#ff0000'
GREEN       = '#00ff00'
BLUE        = '#0000ff'
ORANGE      = '#ff8000'
WHITE       = '#ffffff'


# For importing HTML templates
def get_template(_file):
    with open(_file, 'r') as html:
        return html.read()

# Alias string processor
def alias_string(_id, _dict):
    alias = get_alias(_id, _dict, 'CALLSIGN', 'CITY', 'STATE')
    if type(alias) == list:
        for x,item in enumerate(alias):
            if item == None:
                alias.pop(x)
        return ', '.join(alias)
    else:
        return alias

def alias_short(_id, _dict):
    alias = get_alias(_id, _dict, 'CALLSIGN', 'NAME')
    if type(alias) == list:
        for x,item in enumerate(alias):
            if item == None:
                alias.pop(x)
        return ', '.join(alias)
    else:
        return str(alias)

def alias_call(_id, _dict):
    alias =  get_alias(_id, _dict, 'CALLSIGN')
    if type(alias) == list:
        return str(alias[0])
    else:
        return str(alias)

def alias_tgid(_id, _dict):
    alias = get_alias(_id, _dict, 'NAME')
    if type(alias) == list:
        return str(alias[0])
    else:
        return str(alias)

#
# REPEATER CALL MONITOR (RCM) PACKET PROCESSING
#
def process_rcm(_data):
    now = time()
    _payload = _data.split(',', 1)
    _name = _payload[0]
    _data = _payload[1]
    _packettype = _data[0]
    if _packettype == CALL_MON_STATUS:
        logging.debug('RCM STATUS: {}: {}'.format(_name, repr(_data)))
        _source   = _data[1:5]
        _src_peer = int_id(_data[5:9])
        #_seq_num  = _data[9:13]
        _ts       = int_id(_data[13])+1
        _status   = STATUS[_data[15]] # suspect [14:16] but nothing in leading byte?
        _src_sub  = int_id(_data[16:19])
        _dest     = int_id(_data[19:22])
        _type     = TYPE[_data[22]]
        #_prio     = _data[23]
        #_sec      = _data[24]
        
        if _status != 'End' and _status != 'BSID ON':
            CTABLE[_name]['PEERS'][_source][_ts]['STATUS'] = _status
            CTABLE[_name]['PEERS'][_source][_ts]['TYPE'] = _type
            CTABLE[_name]['PEERS'][_source][_ts]['SRC_SUB'] = alias_string(_src_sub, subscriber_ids)
            CTABLE[_name]['PEERS'][_source][_ts]['SRC_PEER'] = alias_string(_src_peer, peer_ids)
            CTABLE[_name]['PEERS'][_source][_ts]['DEST'] = _dest
            CTABLE[_name]['PEERS'][_source][_ts]['COLOR'] = GREEN
            CTABLE[_name]['PEERS'][_source][_ts]['LAST'] = now
        else:
            CTABLE[_name]['PEERS'][_source][_ts]['STATUS'] = ''
            CTABLE[_name]['PEERS'][_source][_ts]['TYPE'] = ''
            CTABLE[_name]['PEERS'][_source][_ts]['SRC_SUB'] = ''
            CTABLE[_name]['PEERS'][_source][_ts]['SRC_PEER'] = ''
            CTABLE[_name]['PEERS'][_source][_ts]['DEST'] = ''
            CTABLE[_name]['PEERS'][_source][_ts]['COLOR'] = WHITE
            CTABLE[_name]['PEERS'][_source][_ts]['LAST'] = now
        
    elif _packettype == CALL_MON_RPT:
        logging.debug('RCM REPEAT: {}: {}'.format(_name, repr(_data)))
        _source   = _data[1:5]
        _ts_state = [0, _data[5], _data[6]]
        for i in range(1,3):
            if _ts_state[i] == '\x01':
                CTABLE[_name]['PEERS'][_source][i]['STATUS'] = 'Repeating'
                CTABLE[_name]['PEERS'][_source][i]['COLOR'] = GREEN
            elif _ts_state[i] == '\x03':
                CTABLE[_name]['PEERS'][_source][i]['STATUS'] = 'Disabled'
                CTABLE[_name]['PEERS'][_source][i]['COLOR'] = RED
            elif _ts_state[i] == '\x04':
                CTABLE[_name]['PEERS'][_source][i]['STATUS'] = 'Enabled'
                CTABLE[_name]['PEERS'][_source][i]['COLOR'] = GREEN
            else:
                CTABLE[_name]['PEERS'][_source][i]['STATUS'] = ''
                CTABLE[_name]['PEERS'][_source][i]['COLOR'] = WHITE
            CTABLE[_name]['PEERS'][_source][i]['LAST'] = now
        
    elif _packettype == CALL_MON_NACK:
        logging.debug('RCM NACK: {}: {}'.format(_name, repr(_data)))
        _source = _data[1:5]
        _nack = _data[5]
        if _nack == '\x05':
            for i in range(1,3):
                CTABLE[_name]['PEERS'][_source][i]['STATUS'] = 'BSID ON'
                CTABLE[_name]['PEERS'][_source][i]['COLOR'] = ORANGE
        elif _nack == '\x06':
            for i in range(1,3):
                CTABLE[_name]['PEERS'][_source][i]['STATUS'] = ''
                CTABLE[_name]['PEERS'][_source][i]['COLOR'] = WHITE
                
        for i in range(1,3):
            #CTABLE[_name]['PEERS'][_source][i]['TYPE'] = ''
            #CTABLE[_name]['PEERS'][_source][i]['SRC_SUB'] = ''
            #CTABLE[_name]['PEERS'][_source][i]['SRC_PEER'] = ''
            #CTABLE[_name]['PEERS'][_source][i]['DEST'] = ''
            CTABLE[_name]['PEERS'][_source][i]['LAST'] = now
    else:
        logging.error('unknown call mon recieved: {}'.format(repr(_packettype)))
        return

    build_stats()

# DMRlink Table Functions
def add_peer(_stats_peers, _peer, _config_peer_data, _type):
    now = time()
    logging.debug('Adding peer: {}'.format(repr(_peer)))
    _stats_peers[_peer] = {}
    _stats_peers[_peer]['TYPE'] = _type
    _stats_peers[_peer]['RADIO_ID'] = int_id(_peer)
    _stats_peers[_peer]['ALIAS'] = alias_string(int_id(_peer), peer_ids)
    _stats_peers[_peer]['IP'] = _config_peer_data['IP']
    _stats_peers[_peer]['CONNECTED'] = _config_peer_data['STATUS']['CONNECTED']
    _stats_peers[_peer]['KEEP_ALIVES_SENT'] = _config_peer_data['STATUS']['KEEP_ALIVES_SENT']
    _stats_peers[_peer]['KEEP_ALIVES_RECEIVED'] = _config_peer_data['STATUS']['KEEP_ALIVES_RECEIVED']
    _stats_peers[_peer]['KEEP_ALIVES_MISSED'] = _config_peer_data['STATUS']['KEEP_ALIVES_MISSED']
    _stats_peers[_peer][1] = {'STATUS': '', 'TYPE': '', 'SRC_PEER': '', 'SRC_SUB': '', 'DEST': '', 'COLOR': WHITE, 'LAST': now}
    _stats_peers[_peer][2] = {'STATUS': '', 'TYPE': '', 'SRC_PEER': '', 'SRC_SUB': '', 'DEST': '', 'COLOR': WHITE, 'LAST': now}
    
def update_peer(_stats_peers, _peer, _config_peer_data):
    logging.debug('Updateing peer: {}'.format(repr(_peer)))
    _stats_peers[_peer]['CONNECTED'] = _config_peer_data['STATUS']['CONNECTED']
    _stats_peers[_peer]['KEEP_ALIVES_SENT'] = _config_peer_data['STATUS']['KEEP_ALIVES_SENT']
    _stats_peers[_peer]['KEEP_ALIVES_RECEIVED'] = _config_peer_data['STATUS']['KEEP_ALIVES_RECEIVED']
    _stats_peers[_peer]['KEEP_ALIVES_MISSED'] = _config_peer_data['STATUS']['KEEP_ALIVES_MISSED']
    
def delete_peers(_peers_to_delete, _stats_table_peers):
    for _peer in _peers_to_delete:
        del _stats_table_peers[_peer]
        logging.debug('Deleting peer: {}'.format(repr(_peer)))

def build_dmrlink_table(_config, _stats_table):
    for _ipsc, _ipsc_data in _config.iteritems():
        _stats_table[_ipsc] = {}
        _stats_table[_ipsc]['PEERS'] = {}
        _stats_table[_ipsc]['MASTER'] = _config[_ipsc]['LOCAL']['MASTER_PEER']
        _stats_table[_ipsc]['RADIO_ID'] = int_id(_config[_ipsc]['LOCAL']['RADIO_ID'])
        _stats_table[_ipsc]['IP'] = _config[_ipsc]['LOCAL']['IP']
        _stats_peers = _stats_table[_ipsc]['PEERS']
        
        # if this peer is the master
        if _stats_table[_ipsc]['MASTER'] == False:
            _peer = _config[_ipsc]['MASTER']['RADIO_ID']
            _config_peer_data = _config[_ipsc]['MASTER']
            add_peer(_stats_peers, _peer, _config_peer_data, 'Master')

        # for all peers that are not the master
        for _peer, _config_peer_data in _config[_ipsc]['PEERS'].iteritems():
            if _peer != _config[_ipsc]['LOCAL']['RADIO_ID']:
                add_peer(_stats_peers, _peer, _config_peer_data, 'Peer')


def update_dmrlink_table(_config, _stats_table):

    for _ipsc, _ipsc_data in _config.iteritems():
        _stats_peers = _stats_table[_ipsc]['PEERS']
        
        # if this peer is the master
        if _stats_table[_ipsc]['MASTER'] == False:
            _peer = _config[_ipsc]['MASTER']['RADIO_ID']
            _config_peer_data = _config[_ipsc]['MASTER']
            
            _stats_peers[_peer]['RADIO_ID'] = int_id(_peer)
            update_peer(_stats_peers, _peer, _config_peer_data)

        # for all of the peers that are not the master... update or add
        for _peer, _config_peer_data in _config[_ipsc]['PEERS'].iteritems():
            if _peer != _config[_ipsc]['LOCAL']['RADIO_ID']:
                _stats_peers = _stats_table[_ipsc]['PEERS']
            
                # update the peer if we already have it
                if _peer in _stats_table[_ipsc]['PEERS']:
                    update_peer(_stats_peers, _peer, _config_peer_data)
            
                # addit if we don't have it
                if _peer not in _stats_table[_ipsc]['PEERS']:
                    add_peer(_stats_peers, _peer, _config_peer_data, 'peer')

        # for peers that need to be removed, never the master. This is complicated
        peers_to_delete = []
        
        # find any peers missing in the config update    
        for _peer, _stats_peer_data in _stats_table[_ipsc]['PEERS'].iteritems():
            if _peer not in _config[_ipsc]['PEERS'] and _peer != _config[_ipsc]['MASTER']['RADIO_ID']:
                peers_to_delete.append(_peer)
        
        # delte anything identified from the right part of the stats table
        delete_peers(peers_to_delete, _stats_table[_ipsc]['PEERS'])


#
# CONFBRIDGE TABLE FUNCTIONS
#
def build_bridge_table(_bridges):
    _stats_table = {}
    _now = time()
    _cnow = strftime('%Y-%m-%d %H:%M:%S', localtime(_now))
    
    for _bridge, _bridge_data in _bridges.iteritems():
        _stats_table[_bridge] = {}

        for system in _bridges[_bridge]:
            _stats_table[_bridge][system['SYSTEM']] = {}
            _stats_table[_bridge][system['SYSTEM']]['TS'] = system['TS']
            _stats_table[_bridge][system['SYSTEM']]['TGID'] = int_id(system['TGID'])
            
            if system['TO_TYPE'] == 'ON' or system['TO_TYPE'] == 'OFF':
                if system['TIMER'] - _now > 0:
                    _stats_table[_bridge][system['SYSTEM']]['EXP_TIME'] = int(system['TIMER'] - _now)
                else:
                    _stats_table[_bridge][system['SYSTEM']]['EXP_TIME'] = 'Expired'
                if system['TO_TYPE'] == 'ON':
                    _stats_table[_bridge][system['SYSTEM']]['TO_ACTION'] = 'Disconnect'
                else:
                    _stats_table[_bridge][system['SYSTEM']]['TO_ACTION'] = 'Connect'
            else:
                _stats_table[_bridge][system['SYSTEM']]['EXP_TIME'] = 'N/A'
                _stats_table[_bridge][system['SYSTEM']]['TO_ACTION'] = 'None'
            
            if system['ACTIVE'] == True:
                _stats_table[_bridge][system['SYSTEM']]['ACTIVE'] = 'Connected'
                _stats_table[_bridge][system['SYSTEM']]['COLOR'] = GREEN
            elif system['ACTIVE'] == False:
                _stats_table[_bridge][system['SYSTEM']]['ACTIVE'] = 'Disconnected'
                _stats_table[_bridge][system['SYSTEM']]['COLOR'] = RED
            
            for i in range(len(system['ON'])):
                system['ON'][i] = str(int_id(system['ON'][i]))
                    
            _stats_table[_bridge][system['SYSTEM']]['TRIG_ON'] = ', '.join(system['ON'])
            
            for i in range(len(system['OFF'])):
                system['OFF'][i] = str(int_id(system['OFF'][i]))
                
            _stats_table[_bridge][system['SYSTEM']]['TRIG_OFF'] = ', '.join(system['OFF'])
    
    return _stats_table

#
# BUILD DMRLINK AND CONFBRIDGE TABLES FROM CONFIG/BRIDGES DICTS
#          THIS CURRENTLY IS A TIMED CALL
#
build_time = time()
def build_stats():
    global build_time
    now = time()
    if True: #now > build_time + 1:
        if CONFIG:
            table = 'd' + dtemplate.render(_table=CTABLE)
            dashboard_server.broadcast(table)
        if BRIDGES:
            table = 'b' + btemplate.render(_table=BTABLE['BRIDGES'])
            dashboard_server.broadcast(table)
        build_time = now

#
# PROCESS IN COMING MESSAGES AND TAKE THE CORRECT ACTION DEPENING ON THE OPCODE
#
def process_message(_message):
    global CONFIG, BRIDGES, CONFIG_RX, BRIDGES_RX
    opcode = _message[:1]
    _now = strftime('%Y-%m-%d %H:%M:%S %Z', localtime(time()))
    
    if opcode == OPCODE['CONFIG_SND']:
        logging.debug('got CONFIG_SND opcode')
        CONFIG = load_dictionary(_message)
        CONFIG_RX = strftime('%Y-%m-%d %H:%M:%S', localtime(time()))
        if CTABLE:
            update_dmrlink_table(CONFIG, CTABLE)
        else:
            build_dmrlink_table(CONFIG, CTABLE)
    elif opcode == OPCODE['BRIDGE_SND']:
        logging.debug('got BRIDGE_SND opcode')
        BRIDGES = load_dictionary(_message)
        BRIDGES_RX = strftime('%Y-%m-%d %H:%M:%S', localtime(time()))
        BTABLE['BRIDGES'] = build_bridge_table(BRIDGES)
        
    elif opcode == OPCODE['LINK_EVENT']:
        logging.info('LINK_EVENT Received: {}'.format(repr(_message[1:])))
    elif opcode == OPCODE['RCM_SND']:
        process_rcm(_message[1:])
        logging.debug('RCM Message Received: {}'.format(repr(_message[1:])))
        #dashboard_server.broadcast('l' + repr(_message[1:]))
    elif opcode == OPCODE['BRDG_EVENT']:
        logging.info('BRIDGE EVENT: {}'.format(repr(_message[1:])))
        p = _message[1:].split(",")
        if p[0] == 'GROUP VOICE':
            if p[1] == 'END':
                log_message = '{}: {} {}:   IPSC: {:15.15s} PEER: {:8.8s} {:20.20s} SUB: {:8.8s} {:25.25s} TS: {} TGID: {:>5s} {:12.12s} DURATION: {}s'.format(_now, p[0], p[1], p[2], p[4], alias_call(int(p[4]), peer_ids), p[5], alias_short(int(p[5]), subscriber_ids), p[6], p[7], alias_tgid(int(p[7]), talkgroup_ids), p[8])
            elif p[1] == 'START':
                log_message = '{}: {} {}: IPSC: {:15.15s} PEER: {:8.8s} {:20.20s} SUB: {:8.8s} {:25.25s} TS: {} TGID: {:>5s} {:12.12s}'.format(_now, p[0], p[1], p[2], p[4], alias_call(int(p[4]), peer_ids), p[5], alias_short(int(p[5]), subscriber_ids), p[6], p[7], alias_tgid(int(p[7]), talkgroup_ids))
            elif p[1] == 'END WITHOUT MATCHING START':
                log_message = '{}: {} {}: IPSC: {:15.15s} PEER: {:8.8s} {:20.20s} SUB: {:8.8s} {:25.25s} TS: {} TGID: {:>5s} {:12.12s}'.format(_now, p[0], p[1], p[2], p[4], alias_call(int(p[4]), peer_ids), p[5], alias_short(int(p[5]), subscriber_ids), p[6], p[7], alias_tgid(int(p[7]), talkgroup_ids))
            else:
                log_message = '{}: UNKNOWN GROUP VOICE LOG MESSAGE'.format(_now)
        else:
            log_message = '{}: UNKNOWN LOG MESSAGE'.format(_now)
            
        dashboard_server.broadcast('l' + log_message)
        LOGBUF.append(log_message)
    else:
        logging.debug('got unknown opcode: {}, message: {}'.format(repr(opcode), repr(_message[1:])))


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
        self.sendMessage('d' + str(dtemplate.render(_table=CTABLE)))
        self.sendMessage('b' + str(btemplate.render(_table=BTABLE['BRIDGES'])))
        for _message in LOGBUF:
            if _message:
                self.sendMessage('l' + _message)

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
    logging.basicConfig(level=logging.INFO,filename = (LOG_PATH + LOG_NAME), filemode='a')
    
    # Download alias files
    result = try_download(PATH, 'peer_ids.csv', PEER_URL, (FILE_RELOAD * 86400))
    logging.info(result)
   
    result = try_download(PATH, 'subscriber_ids.csv', SUBSCRIBER_URL, (FILE_RELOAD * 86400))
    logging.info(result)
    
    # Make Alias Dictionaries
    peer_ids = mk_full_id_dict(PATH, PEER_FILE, 'peer')
    if peer_ids:
        logging.info('ID ALIAS MAPPER: peer_ids dictionary is available')
        
    subscriber_ids = mk_full_id_dict(PATH, SUBSCRIBER_FILE, 'subscriber')
    if subscriber_ids:
        logging.info('ID ALIAS MAPPER: subscriber_ids dictionary is available')
    
    talkgroup_ids = mk_full_id_dict(PATH, TGID_FILE, 'tgid')
    if talkgroup_ids:
        logging.info('ID ALIAS MAPPER: talkgroup_ids dictionary is available')
    
    local_subscriber_ids = mk_full_id_dict(PATH, LOCAL_SUB_FILE, 'subscriber')
    if local_subscriber_ids:
        logging.info('ID ALIAS MAPPER: local_subscriber_ids added to subscriber_ids dictionary')
        subscriber_ids.update(local_subscriber_ids)
        
    local_peer_ids = mk_full_id_dict(PATH, LOCAL_PEER_FILE, 'peer')
    if local_peer_ids:
        logging.info('ID ALIAS MAPPER: local_peer_ids added peer_ids dictionary')
        peer_ids.update(local_peer_ids)
    
    # Jinja2 Stuff
    env = Environment(
        loader=PackageLoader('web_tables', 'templates'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    dtemplate = env.get_template('dmrlink_table.html')
    btemplate = env.get_template('bridge_table.html')
    
    # Create Static Website index file
    index_html = get_template(PATH + 'index_template.html')
    index_html = index_html.replace('<<<system_name>>>', REPORT_NAME)
    
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
