    ####################################################################
    # A Simple UDI Poloyglot Controller to Listen for Plex Webhooks.   #
    ####################################################################

try:
    import polyinterface
except ImportError:
    import pgc_interface as polyinterface

from http.server import HTTPServer, BaseHTTPRequestHandler
#from nodes import PlexClientNode
from threading import Thread
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
        LOGGER.info('HTTP GET Recieved on {} from {}'.format(self.server.server_address,self.client_address))

    
    def do_POST(self):
        LOGGER.info('testing-POST')
        # Read in the POST message body in bytes
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length) 

        # Parse/Convert Body into Dict, looking for Plex JSON/event data only.
        payload = self.PlexJSONParse(body)

        # If not from Plex parser will return NONE, then ignore POST.
        if payload == None: 
            LOGGER.info('Invalid-Plex POST Recieved and Ignored.')
            return  
        
        # CODE HERE
        LOGGER.info('Plex POST Recieved from {}'.format(self.client_address))
        self.parent.post_handler(payload)
        
    def PlexJSONParse(self,sBody):
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

    def __init__(self, polyglot):
        self.parent = self
        self.logger = LOGGER
        self.httpService = None                          # Pointer for HTTP Service.
        self.logger.info('Initializing Plex Webhook Polyglot...')
        super(PlexController, self).__init__(polyglot)
        self.name = 'Plex Webhook Listener'
        #self.address = 'udiplexpoly'
        #self.primary = self.address

    def start(self):
        # Show values on startup if desired.
        self.logger.info('Starting Plex Webhook Polyglot...')
        self.setDriver('ST', 1)
        self.logger.debug('ST=%s',self.getDriver('ST'))

        # Get a handler and set parent to myself, so we can process the POST requests.
        handle = PlexListener
        handle.parent = self

        # Start the HTTP Service to Listen for POSTs from PMS. 
        self.httpService = HTTPServer(('192.168.2.15', 9090), PlexListener)
        self.thread  = Thread(target=self.httpService.serve_forever)
        self.thread.name = 'PlexListener'
        self.thread.daemon = True
        self.thread.start()
        
        self.setDriver('GV0', 'Server IP: 192.168.2.15')
        # httpService.serve_forever() # I do not think this is needed as the Polyglot will run.
        self.poly.add_custom_config_docs("<b>This is some custom config docs data. CH</b>")
        #self.heartbeat()
        return True

    def post_handler(self,payload):
        self.logger.debug('Post Handler Passed {}.'.format(type(payload)))

    def longPoll(self):
        if self.thread.is_alive(): self.logger.info('longPoll - All Good')
        else: self.logger.debug('longPoll - Thread closed?')
        #self.heartbeat()

    def stop(self):
        self.httpService.shutdown()
        self.httpService.server_close()
        if self.thread.is_alive(): self.logger.debug('Thread still alive.')
        self.httpService = None
        self.setDriver('ST', 0)
        self.setDriver('GPV', 'Stopped')
        self.logger.debug('Plex Webhook NodeServer stopped.')

    id = 'plexcontroller'

    drivers = [
        {'driver': 'ST', 'value': 0, 'uom': 2},
        {'driver': 'GV0', 'value': '', 'uom': 56}, 
    ]
