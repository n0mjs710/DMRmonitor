# -*- coding: utf-8 -*-
from __future__ import print_function

from pprint import pprint
from dmr_utils.utils import int_id
import jinja2
from jinja2 import Environment, PackageLoader, select_autoescape


CONFIG = {'IPSC-2': {'LOCAL': {'AUTH_KEY': '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xc0\xff\xee', 'RADIO_ID': '\x00\x04\xc3#', 'ENABLED': True, 'TS1_LINK': True, 'RCM': False, 'AUTH_ENABLED': True, 'DATA_CALL': False, 'NUM_PEERS': 0, 'XNL_MASTER': False, 'MASTER_PEER': False, 'CSBK_CALL': False, 'PORT': 51000, 'MODE': 'j', 'TS2_LINK': True, 'CON_APP': False, 'IP': '192.241.209.207', 'GROUP_HANGTIME': 1, 'FLAGS': '\x00\x00\x00\x14', 'IPSC_MODE': 'DIGITAL', 'ALIVE_TIMER': 15, 'XNL_CALL': False, 'VOICE_CALL': True, 'MAX_MISSED': 4, 'PEER_OPER': True}, 'PEERS': {}, 'MASTER': {'STATUS': {'KEEP_ALIVES_MISSED': 0, 'KEEP_ALIVE_RX_TIME': 1495740812, 'KEEP_ALIVES_OUTSTANDING': 0, 'CONNECTED': True, 'PEER_LIST': True, 'KEEP_ALIVES_RECEIVED': 39, 'KEEP_ALIVES_SENT': 39}, 'MODE_DECODE': {'TS_2': True, 'PEER_MODE': 'DIGITAL', 'TS_1': True, 'PEER_OP': True}, 'FLAGS_DECODE': {'CSBK': True, 'CON_APP': False, 'XNL_CON': False, 'XNL_SLAVE': False, 'AUTH': True, 'RCM': False, 'MASTER': True, 'VOICE': True, 'DATA': True, 'XNL_MASTER': True}, 'IP': '107.170.223.160', 'RADIO_ID': '\x00\x14\x05\x01', 'FLAGS': '\x00\x02\x80]', 'MODE': 'j', 'PORT': 56002}}, 'K0PRO': {'LOCAL': {'AUTH_KEY': '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01!#', 'RADIO_ID': '\x00\xc85\x94', 'ENABLED': True, 'TS1_LINK': True, 'RCM': False, 'AUTH_ENABLED': True, 'DATA_CALL': False, 'NUM_PEERS': 0, 'XNL_MASTER': False, 'MASTER_PEER': True, 'CSBK_CALL': False, 'PORT': 50916, 'MODE': 'j', 'TS2_LINK': True, 'CON_APP': False, 'IP': '192.241.209.207', 'GROUP_HANGTIME': 1, 'FLAGS': '\x00\x00\x00\x15', 'IPSC_MODE': 'DIGITAL', 'ALIVE_TIMER': 15, 'XNL_CALL': False, 'VOICE_CALL': True, 'MAX_MISSED': 4, 'PEER_OPER': True}, 'PEERS': {}, 'MASTER': {'STATUS': {'KEEP_ALIVES_MISSED': 0, 'KEEP_ALIVE_RX_TIME': 0, 'KEEP_ALIVES_OUTSTANDING': 0, 'CONNECTED': False, 'PEER_LIST': False, 'KEEP_ALIVES_RECEIVED': 0, 'KEEP_ALIVES_SENT': 0}, 'MODE_DECODE': '', 'FLAGS_DECODE': '', 'IP': '', 'RADIO_ID': '\x00\x00\x00\x00', 'FLAGS': '\x00\x00\x00\x00', 'MODE': '\x00', 'PORT': ''}}, 'K0USY-CB': {'LOCAL': {'AUTH_KEY': '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xde\xad\xbe\xef', 'RADIO_ID': '\x00\xc85\x8e', 'ENABLED': True, 'TS1_LINK': True, 'RCM': False, 'AUTH_ENABLED': True, 'DATA_CALL': False, 'NUM_PEERS': 0, 'XNL_MASTER': False, 'MASTER_PEER': False, 'CSBK_CALL': False, 'PORT': 50910, 'MODE': 'j', 'TS2_LINK': True, 'CON_APP': True, 'IP': '192.241.209.207', 'GROUP_HANGTIME': 1, 'FLAGS': '\x00\x00 \x14', 'IPSC_MODE': 'DIGITAL', 'ALIVE_TIMER': 15, 'XNL_CALL': False, 'VOICE_CALL': True, 'MAX_MISSED': 4, 'PEER_OPER': True}, 'PEERS': {}, 'MASTER': {'STATUS': {'KEEP_ALIVES_MISSED': 0, 'KEEP_ALIVE_RX_TIME': 1495740812, 'KEEP_ALIVES_OUTSTANDING': 0, 'CONNECTED': True, 'PEER_LIST': True, 'KEEP_ALIVES_RECEIVED': 39, 'KEEP_ALIVES_SENT': 39}, 'MODE_DECODE': {'TS_2': True, 'PEER_MODE': 'DIGITAL', 'TS_1': True, 'PEER_OP': True}, 'FLAGS_DECODE': {'CSBK': True, 'CON_APP': True, 'XNL_CON': False, 'XNL_SLAVE': True, 'AUTH': True, 'RCM': True, 'MASTER': True, 'VOICE': True, 'DATA': True, 'XNL_MASTER': False}, 'IP': '164.113.198.13', 'RADIO_ID': '\x00\xc82e', 'FLAGS': '\x00\x00\xe0=', 'MODE': 'j', 'PORT': 50001}}, 'BRANDMEISTER': {'LOCAL': {'AUTH_KEY': '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01#E', 'RADIO_ID': '\x00\xc85\x93', 'ENABLED': True, 'TS1_LINK': True, 'RCM': False, 'AUTH_ENABLED': False, 'DATA_CALL': False, 'NUM_PEERS': 1, 'XNL_MASTER': False, 'MASTER_PEER': False, 'CSBK_CALL': False, 'PORT': 50915, 'MODE': 'j', 'TS2_LINK': True, 'CON_APP': False, 'IP': '192.241.209.207', 'GROUP_HANGTIME': 1, 'FLAGS': '\x00\x00\x00\x04', 'IPSC_MODE': 'DIGITAL', 'ALIVE_TIMER': 15, 'XNL_CALL': False, 'VOICE_CALL': True, 'MAX_MISSED': 4, 'PEER_OPER': True}, 'PEERS': {}, 'MASTER': {'STATUS': {'KEEP_ALIVES_MISSED': 0, 'KEEP_ALIVE_RX_TIME': 1495740812, 'KEEP_ALIVES_OUTSTANDING': 0, 'CONNECTED': True, 'PEER_LIST': True, 'KEEP_ALIVES_RECEIVED': 39, 'KEEP_ALIVES_SENT': 39}, 'MODE_DECODE': {'TS_2': True, 'PEER_MODE': 'DIGITAL', 'TS_1': True, 'PEER_OP': True}, 'FLAGS_DECODE': {'CSBK': True, 'CON_APP': False, 'XNL_CON': False, 'XNL_SLAVE': True, 'AUTH': False, 'RCM': False, 'MASTER': True, 'VOICE': True, 'DATA': True, 'XNL_MASTER': False}, 'IP': '74.91.114.19', 'RADIO_ID': '\x00\x00\x0c\x1e', 'FLAGS': '\x00\x00\x80-', 'MODE': 'j', 'PORT': 55001}}, 'K0USY': {'LOCAL': {'AUTH_KEY': '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xc0\xff\xee', 'RADIO_ID': '\x00\xc85\x92', 'ENABLED': True, 'TS1_LINK': True, 'RCM': False, 'AUTH_ENABLED': True, 'DATA_CALL': False, 'NUM_PEERS': 5, 'XNL_MASTER': False, 'MASTER_PEER': True, 'CSBK_CALL': False, 'PORT': 50914, 'MODE': 'j', 'TS2_LINK': True, 'CON_APP': True, 'IP': '192.241.209.207', 'GROUP_HANGTIME': 1, 'FLAGS': '\x00\x00 \x15', 'IPSC_MODE': 'DIGITAL', 'ALIVE_TIMER': 15, 'XNL_CALL': False, 'VOICE_CALL': True, 'MAX_MISSED': 4, 'PEER_OPER': True}, 'PEERS': {'\x00\x04\xc2\xc9': {'STATUS': {'KEEP_ALIVES_MISSED': 0, 'KEEP_ALIVE_RX_TIME': 1495740813, 'KEEP_ALIVES_OUTSTANDING': 0, 'CONNECTED': True, 'KEEP_ALIVES_RECEIVED': 36, 'KEEP_ALIVES_SENT': 0}, 'MODE_DECODE': {'TS_2': True, 'PEER_MODE': 'DIGITAL', 'TS_1': True, 'PEER_OP': True}, 'FLAGS_DECODE': {'CSBK': True, 'CON_APP': False, 'XNL_CON': False, 'XNL_SLAVE': False, 'AUTH': True, 'RCM': False, 'MASTER': False, 'VOICE': True, 'DATA': True, 'XNL_MASTER': True}, 'IP': '129.130.114.221', 'FLAGS': '\x00\x00\x80\\', 'MODE': 'j', 'PORT': 50000}, '\x00\x04\xc2\xc5': {'STATUS': {'KEEP_ALIVES_MISSED': 0, 'KEEP_ALIVE_RX_TIME': 1495740813, 'KEEP_ALIVES_OUTSTANDING': 0, 'CONNECTED': True, 'KEEP_ALIVES_RECEIVED': 36, 'KEEP_ALIVES_SENT': 0}, 'MODE_DECODE': {'TS_2': True, 'PEER_MODE': 'DIGITAL', 'TS_1': True, 'PEER_OP': True}, 'FLAGS_DECODE': {'CSBK': True, 'CON_APP': False, 'XNL_CON': False, 'XNL_SLAVE': False, 'AUTH': True, 'RCM': False, 'MASTER': False, 'VOICE': True, 'DATA': True, 'XNL_MASTER': True}, 'IP': '174.71.148.130', 'FLAGS': '\x00\x00\x80\\', 'MODE': 'j', 'PORT': 44779}, '\x00\x04\xc2\xc3': {'STATUS': {'KEEP_ALIVES_MISSED': 0, 'KEEP_ALIVE_RX_TIME': 1495740813, 'KEEP_ALIVES_OUTSTANDING': 0, 'CONNECTED': True, 'KEEP_ALIVES_RECEIVED': 36, 'KEEP_ALIVES_SENT': 0}, 'MODE_DECODE': {'TS_2': True, 'PEER_MODE': 'DIGITAL', 'TS_1': True, 'PEER_OP': True}, 'FLAGS_DECODE': {'CSBK': True, 'CON_APP': False, 'XNL_CON': False, 'XNL_SLAVE': False, 'AUTH': True, 'RCM': False, 'MASTER': False, 'VOICE': True, 'DATA': True, 'XNL_MASTER': True}, 'IP': '209.114.113.233', 'FLAGS': '\x00\x00\x80\\', 'MODE': 'j', 'PORT': 50000}, '\x00\xc85\xa4': {'STATUS': {'KEEP_ALIVES_MISSED': 0, 'KEEP_ALIVE_RX_TIME': 1495740825, 'KEEP_ALIVES_OUTSTANDING': 0, 'CONNECTED': True, 'KEEP_ALIVES_RECEIVED': 39, 'KEEP_ALIVES_SENT': 0}, 'MODE_DECODE': {'TS_2': True, 'PEER_MODE': 'DIGITAL', 'TS_1': True, 'PEER_OP': True}, 'FLAGS_DECODE': {'CSBK': False, 'CON_APP': False, 'XNL_CON': False, 'XNL_SLAVE': False, 'AUTH': True, 'RCM': False, 'MASTER': False, 'VOICE': True, 'DATA': False, 'XNL_MASTER': False}, 'IP': '69.28.91.79', 'FLAGS': '\x00\x00\x00\x14', 'MODE': 'j', 'PORT': 50932}, '\x00\x04\xc2\xc1': {'STATUS': {'KEEP_ALIVES_MISSED': 0, 'KEEP_ALIVE_RX_TIME': 1495740813, 'KEEP_ALIVES_OUTSTANDING': 0, 'CONNECTED': True, 'KEEP_ALIVES_RECEIVED': 36, 'KEEP_ALIVES_SENT': 0}, 'MODE_DECODE': {'TS_2': True, 'PEER_MODE': 'DIGITAL', 'TS_1': True, 'PEER_OP': True}, 'FLAGS_DECODE': {'CSBK': True, 'CON_APP': False, 'XNL_CON': False, 'XNL_SLAVE': False, 'AUTH': True, 'RCM': False, 'MASTER': False, 'VOICE': True, 'DATA': True, 'XNL_MASTER': True}, 'IP': '24.124.21.73', 'FLAGS': '\x00\x00\x80\\', 'MODE': 'j', 'PORT': 50000}}, 'MASTER': {'STATUS': {'KEEP_ALIVES_MISSED': 0, 'KEEP_ALIVE_RX_TIME': 0, 'KEEP_ALIVES_OUTSTANDING': 0, 'CONNECTED': False, 'PEER_LIST': False, 'KEEP_ALIVES_RECEIVED': 0, 'KEEP_ALIVES_SENT': 0}, 'MODE_DECODE': '', 'FLAGS_DECODE': '', 'IP': '', 'RADIO_ID': '\x00\x00\x00\x00', 'FLAGS': '\x00\x00\x00\x00', 'MODE': '\x00', 'PORT': ''}}}

TABLE = {}

#pprint(CONFIG)

'''
env = Environment(
    loader=PackageLoader('htmlmaker', 'templates'),
    autoescape=select_autoescape(['html', 'xml'])
)

template = env.get_template('table.html')
print(template.render(something='stuff'))
'''

print()

for _ipsc, _ipsc_data in CONFIG.iteritems():
    TABLE[_ipsc] = {}
    TABLE[_ipsc]['MASTER'] = CONFIG[_ipsc]['LOCAL']['MASTER_PEER']
    TABLE[_ipsc]['PEERS'] = {}
    if TABLE[_ipsc]['MASTER'] == False:
        _peer = CONFIG[_ipsc]['MASTER']['RADIO_ID']
        _peer_data = CONFIG[_ipsc]['MASTER']
        TABLE[_ipsc]['PEERS'][CONFIG[_ipsc]['MASTER']['RADIO_ID']] = {}
        TABLE[_ipsc]['PEERS'][_peer]['TYPE'] = 'Master'
        TABLE[_ipsc]['PEERS'][_peer]['RADIO_ID'] = int_id(_peer)
        TABLE[_ipsc]['PEERS'][_peer]['CONNECTED'] = _peer_data['STATUS']['CONNECTED']
        TABLE[_ipsc]['PEERS'][_peer]['KEEP_ALIVES_SENT'] = _peer_data['STATUS']['KEEP_ALIVES_SENT']
        TABLE[_ipsc]['PEERS'][_peer]['KEEP_ALIVES_RECEIVED'] = _peer_data['STATUS']['KEEP_ALIVES_RECEIVED']
        TABLE[_ipsc]['PEERS'][_peer]['KEEP_ALIVES_MISSED'] = _peer_data['STATUS']['KEEP_ALIVES_MISSED']
        TABLE[_ipsc]['PEERS'][_peer]['TS1'] = {'STATUS': '', 'SOURCE': '', 'SUBSCRIBER': '', 'DESTINATION': ''}
        TABLE[_ipsc]['PEERS'][_peer]['TS2'] = {'STATUS': '', 'SOURCE': '', 'SUBSCRIBER': '', 'DESTINATION': ''}
    for _peer, _peer_data in CONFIG[_ipsc]['PEERS'].iteritems():
        TABLE[_ipsc]['PEERS'][_peer] = {}
        TABLE[_ipsc]['PEERS'][_peer]['TYPE'] = 'Peer'
        TABLE[_ipsc]['PEERS'][_peer]['RADIO_ID'] = int_id(_peer)
        TABLE[_ipsc]['PEERS'][_peer]['CONNECTED'] = _peer_data['STATUS']['CONNECTED']
        TABLE[_ipsc]['PEERS'][_peer]['KEEP_ALIVES_SENT'] = _peer_data['STATUS']['KEEP_ALIVES_SENT']
        TABLE[_ipsc]['PEERS'][_peer]['KEEP_ALIVES_RECEIVED'] = _peer_data['STATUS']['KEEP_ALIVES_RECEIVED']
        TABLE[_ipsc]['PEERS'][_peer]['KEEP_ALIVES_MISSED'] = _peer_data['STATUS']['KEEP_ALIVES_MISSED']
        TABLE[_ipsc]['PEERS'][_peer]['TS1'] = {'STATUS': '', 'SOURCE': '', 'SUBSCRIBER': '', 'DESTINATION': ''}
        TABLE[_ipsc]['PEERS'][_peer]['TS2'] = {'STATUS': '', 'SOURCE': '', 'SUBSCRIBER': '', 'DESTINATION': ''}
    


pprint(TABLE)

for item in TABLE:
    print(item, len(TABLE[item]['PEERS']))


    #if not CONFIG[_IPSC]['LOCAL']['MASTER_PEER']:
    #    print('     IPSC: {} MPEER: {}, CONNECTED: {}'.format(_IPSC, int_id(CONFIG[_IPSC]['MASTER']['RADIO_ID']), CONFIG[_IPSC]['MASTER']['STATUS']['CONNECTED']))
