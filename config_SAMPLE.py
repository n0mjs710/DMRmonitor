REPORT_NAME     = 'system.domain.name'  # Name of the monitored DMRlink system
CONFIG_INC      = True                  # Include DMRlink stats
BRIDGES_INC     = True                  # Include Bridge stats (confbrige.py)
DMRLINK_IP      = '127.0.0.1'           # DMRlink's IP Address
DMRLINK_PORT    = 4321                  # DMRlink's TCP reporting socket
FREQUENCY       = 10                    # Frequency to push updates to web clients
WEB_SERVER_PORT = 8080                  # Has to be above 1024 if you're not running as root

# Files and stuff for loading alias files for mapping numbers to names
PATH            = './'                          # MUST END IN '/'
PEER_FILE       = 'peer_ids.json'                # Will auto-download from DMR-MARC
SUBSCRIBER_FILE = 'subscriber_ids.json'          # Will auto-download from DMR-MARC
TGID_FILE       = 'talkgroup_ids.json'           # User provided, should be in "integer TGID, TGID name" format
LOCAL_SUB_FILE  = 'local_subscriber_ids.json'    # User provided (optional, leave '' if you don't use it), follow the format of DMR-MARC
LOCAL_PEER_FILE = 'local_peer_ids.json'          # User provided (optional, leave '' if you don't use it), follow the format of DMR-MARC
FILE_RELOAD     = 7                             # Number of days before we reload DMR-MARC database files
PEER_URL        = 'https://www.radioid.net/static/rptrs.json'
SUBSCRIBER_URL  = 'https://www.radioid.net/static/users.json'
# Settings for log files
LOG_PATH        = PATH
LOG_NAME        = 'webtables.log'
