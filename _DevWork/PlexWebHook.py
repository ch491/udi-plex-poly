from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
#from nodes import PlexClientNode
from threading import Thread
import json


class PlexListener(BaseHTTPRequestHandler):

    def do_GET(self):
        # For Testing and Troubleshooting
        # Should see socket open to receive PLEX Webhooks.
        print(self.server.server_address)
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'This service is only to receive Plex WebHooks')
    
    def do_POST(self):
        print('POST Received') ## -- CONVERT to LOGGER in Polyglot --

        # Read in the POST message body in bytes
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length) 

        # Parse/Convert Body into Dict, looking for Plex JSON/event data only.
        payload = PlexJSONParse(body)

        # If not from Plex parser will return NONE, then ignore POST.
        if payload == None: return  ## -- CONVERT to LOGGER in Polyglot --
        print(self.client_address)
        ## --- FOR TESTING REMOVE ---
        for key in payload.keys():
            if key == "Metadata":
                for skey in payload[key].keys():
                    print(key, skey, " = ",payload[key][skey],"\n")
            else:
                print(key," = ",payload[key],"\n")
        
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

#httpd = HTTPServer(('192.168.2.100', 90), plexListener)
#httpd.serve_forever()

httpService = ThreadingHTTPServer(('192.168.2.100', 90), PlexListener)
thread  = Thread(target=httpService.serve_forever)
thread.name = 'PlexListener'
thread.daemon = True
thread.start()

while True:
    pass


