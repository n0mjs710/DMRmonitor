HTML = {'HEAD': '\
            <head>\
            <title>DMRlink Activity Monitor</title>\
            </head>\
            \
            <script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/1.3/jquery.min.js"></script>\
            \
            <body style="font: 10pt arial, sans-serif">\
            \
            <center><h2>DMRlink Monitoring System</h2>\
            <p>{}</p>',
        'DMRLINK': '\
            <hr>\
            <h3>DMRlink System Connection Status</h3>\
            <div id="DMRlinkTable"></div>\
            <br>\
            <script language="javascript" type="text/javascript">\
            function refreshDMRlinkTable() {\
                $("#DMRlinkTable").load("dmrlink_stats.html", function(){\
                    $(this).unwrap();\
                });\
            };\
            refreshDMRlinkTable();\
            setInterval (function() {\
                refreshDMRlinkTable()\
            }, 15000);\
            </script>',
        'CONFBRIDGE': '\
            <hr>\
            <h3>Conference Bridge System Connection Status</h3>\
            <div id="ConfBridgeTable"></div>\
            <br>\
            <script language="javascript" type="text/javascript">\
            function refreshConfBridgeTable(){\
                $("#ConfBridgeTable").load("confbridge_stats.html", function(){\
                   $(this).unwrap();\
                });\
            };\
            refreshConfBridgeTable();\
            setInterval (function() {\
                refreshConfBridgeTable()\
            }, 15000);\
            </script>',
        'FOOT': '\
            <hr>\
            <p>Copyright (c) 2017 K0USY Group</p>\
            </center>\
            </body>\
            </html>'
        }