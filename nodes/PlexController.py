    ####################################################################
    # A Simple UDI Poloyglot Controller to Listen for Plex Webhooks.   #
    ####################################################################

try:
    import polyinterface
except ImportError:
    import pgc_interface as polyinterface

from http.server import HTTPServer, BaseHTTPRequestHandler
#from nodes import PlexClientNode
import json
import sys

# Create a LOGGER to Polyglot.
LOGGER = polyinterface.LOGGER

# Basic HTTP Listener Service
class PlexListener(BaseHTTPRequestHandler):

    def do_GET(self):
        # For Testing and Troubleshooting
        # Should see socket open to receive PLEX Webhooks. 
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'This service is only to receive Plex WebHooks')
    
    def do_POST(self):
        
        # Read in the POST message body in bytes
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length) 

        # Parse/Convert Body into Dict, looking for Plex JSON/event data only.
        payload = PlexJSONParse(body)

        # If not from Plex parser will return NONE, then ignore POST.
        if payload == None: 
            LOGGER.info('Invalid-Plex POST Recieved and Ignored.')
            return  
        
        # CODE HERE
        LOGGER.info('Plex POST Recieved from {}'.format("TEMP-IPHERE"))
    
    def PlexJSONParse(sBody):
        #########################################################
        # This function is a simple HTTP Post Request Parser.   #
        # If the POST includes JSON and contains a key "event"  #
        # then it assumes it is Plex Webhooks JSON data.        #
        # If Plex JSON/event is not found returns NONE.         #
        #########################################################
        try:
            # First ensure parameter was passed as a string. (In Not Convert)
            if not isinstance(sBody, str): sBody = sBody.decode("utf-8","ignore")
        except:
            return None

        # Parse sBody into a List with sep = '\r\n'
        RequestList = sBody.split('\r\n')

        # Loop through each line looking for 'Content-Type: application/json'
        # Once found it will look for JSON data with a key 'event'.
        bJSON = False
        for line in RequestList:
            if "Content-Type: application/json" in line: bJSON = True
            if "event" in line and bJSON == True:
                try:
                    return(json.loads(line))  # Return Plex Event JSON data as DICT.
                except:
                    return None
        return None # If Plex JSON/event is not found in HTTP Body.

# Main UDI Polyglot Controller
class PlexController(polyinterface.Controller):

    # Pointer to the HTTP.
    httpService = None

    def __init__(self, polyglot):
        super(PlexController, self).__init__(polyglot)
        self.name = 'Plex Webhook Listener'

    def start(self):
        # Open the server.json file and collect the data within it. 
        with open('server.json') as data:
            SERVERDATA = json.load(data)
            data.close()
        try:
            VERSION = SERVERDATA['credits'][0]['version']
            LOGGER.info('Plex Poly Version {} found.'.format(VERSION))
        except (KeyError, ValueError):
            LOGGER.info('Plex Poly Version not found in server.json.')
            VERSION = '0.0.0'

        # Show values on startup if desired.
        LOGGER.info('Started Plex NodeServer {}'.format(VERSION))
        self.setDriver('ST', 1)
        LOGGER.debug('ST=%s',self.getDriver('ST'))
        # Start the HTTP Service to Listen for POSTs from PMS. 
        self.httpService = HTTPServer(('192.168.2.15', 90), PlexListener)
        self.setDriver('GPV', '192.168.2.15')
        # httpService.serve_forever() # I do not think this is needed as the Polyglot will run.
        self.poly.add_custom_config_docs("<b>This is some custom config docs data. CH</b>")

    def stop(self):
        self.httpService = None
        self.setDriver('ST', 0)
        self.setDriver('GPV', 'Stopped')
        LOGGER.debug('Plex Webhook NodeServer stopped.')

    id = 'plexcontroller'

    drivers = [
        {'driver': 'ST', 'value': 0, 'uom': 2},
        {'driver': 'GPV', 'value': '', 'uom': 56}, 
    ]
