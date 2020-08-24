#!/usr/bin/env python3
'''
PlexClient Node used by PlexController
'''
try:
    import polyinterface
except ImportError:
    import pgc_interface as polyinterface

from datetime import datetime, timedelta

# Define Plex strings and their numerical values. 
# pulled from Plex Webhooks https://support.plex.tv/articles/115002267687-webhooks/
dEvents = {
    "media.stop":0, 
    "media.play":1, 
    "media.pause":2, 
    "media.resume":3, 
    "media.rate":4, 
    "media.scrobble":5
    }

dLibraries = {
    "movie":1, 
    "show":1,
    "artist":2,
    "photo":3,
    }

dMediaTypes = {
    "episode":1, 
    "movie":2,
    "track":3,
    "photo":4,
    }

# These are pulled/combined from thetvdb.com and themoviedb.org
# If update required numberic values must match profile/nls-en/us.txt.
dRatings = {
    "NR":1, "NOT RATED":1, 
    "G":2, "TV-G":2, "ca/G":2,
    "Y":3, "TV-Y":3, 
    "Y7":4, "TV-Y7":4,
    "PG":5, "TV-PG":5, "PG-13":5, "ca/13+":5, "ca/PG":5, "12":5,
    "14":6, "TV-14":6, "ca/F":6, "ca/14":6, "ca/14A":6,
    "MA":7, "TV-MA":7, "M+15":7, "ca/16+":7, "16":7,
    "NC-17":8,
    "R":9, "TV-18+":9, "ca/18A":9, "ca/R":9, "18":9
    }

class PlexClient(polyinterface.Node):

    def __init__(self, controller, primary, address, name, logger, rapid_trigger):
        super().__init__(controller, primary, address, name)
        self.ctrl = controller
        self.pri = primary
        self.name = name
        self.logger = logger
        self.postCount = 0
        self.lastPost = datetime.now()
        self.rapidFlag = False
        self.rapid_trigger = rapid_trigger
        self.logger.info('Plex Client Node Created {} {}.'.format(name,address))

    def start(self):
        # Load Previous postCount from ISY GV5 driver and reset rapidFlag. 
        gv0 = self.getDriver('GV0')
        if gv0 != None: self.postCount = int(gv0)
        self.rapidFlag = False
        self.setDriver("GV0",self.postCount)

    def resetFlag(self):
        # Reset the Flag called by PlexController.shortPoll()
        if self.rapidFlag:
            self.rapidFlag = False
            self.setDriver("GV5",0) 

    def update(self,time,payload):
        # Called from controller.post_handler() 
        # Parameter "payload" must be a dictionary from the JSON/POST. 
        self.logger.info('Client update from: {}'.format(self.name))
        
        # Create a list to store numerical values. [local,event,lib,type,rating]
        parms = [] 
        
        try: #If any errors just ignore post/update. 
            # Collect Keys provided in metadata (subset of payload). 
            metakeys = payload["Metadata"].keys() if "Metadata" in payload.keys() else None

            # Lookup in dictionaies (above) what numerical value to stored.
            parms.append(1 if payload["Player"]["local"] else 0)
            try: parms.append(dEvents[payload["event"]])
            except: parms.append(0)
            #Check for each value in Metadata incase it is not provided.
            if metakeys != None:
                try: parms.append(dLibraries[payload["Metadata"]["librarySectionType"]])
                except: parms.append(0)
                try: parms.append(dMediaTypes[payload["Metadata"]["type"]])
                except: parms.append(0)
                try: parms.append(dRatings[payload["Metadata"]["contentRating"]])
                except: parms.append(0)
            else: parms += [0,0,0] # Defaults if no Metadata section. 

            # ---------------------------  Saved for Beta Testing --------------------------------
            #self.logger.debug('Lib,Media Values: {},{}'.format(payload["Metadata"]["librarySectionType"],payload["Metadata"]["type"]))
            #self.logger.debug('Lib,Media Numbers: {},{}'.format(dLibraries[payload["Metadata"]["librarySectionType"]],dMediaTypes[payload["Metadata"]["type"]]))
            
            # Increment the number of valid POSTs from this client and add to parms. 
            self.postCount += 1
            parms.append(self.postCount)

            # Update the drivers for ISY. 
            for id, driver in enumerate(("ST", "GV1", "GV2", "GV3", "GV4", "GV0")):
                self.setDriver(driver, parms[id])
            self.reportDrivers()

        except: 
            self.logger.error('Error Parsing JSON Data from {}, update ignored.'.format(self.name))
            return
                
        ###########################################################################################
        #     If all goes well with update then check for Rapid changes in client status.         #
        #  This feature was requested to monitor if thier kids are pushing play/pause repeatedly. #
        ###########################################################################################
        if self.rapid_trigger != 0:
            # Convert Time string format "Sat, 22 Aug 2020 14:26:29 GMT" into System Date.
            newPost = datetime.strptime(time,'%a, %d %b %Y %H:%M:%S %Z')

            # Compare time to previous time if less then self.rapid_trigger between POSTs then raise rapidFlag.  
            delta = newPost - self.lastPost
            if delta <= timedelta(seconds=self.rapid_trigger):
                # If second rapidFlag is raise then set ISY Node.GV5 to True.
                if self.rapidFlag: self.setDriver("GV5", 1) 
                else: self.rapidFlag = True         # First rapidFlag
            # Store current post as the last POST received.
            self.lastPost = newPost 

    def reset_values(self,command):
        self.postCount = 0
        self.rapidFlag = False
        self.lastPost = datetime.now()
        self.setDriver("GV5",0)
        parms = [0,0,0,0,0,0] # Reset All Metadata fields.
        for id, driver in enumerate(("ST", "GV1", "GV2", "GV3", "GV4", "GV0")):
            self.setDriver(driver, parms[id])
        self.reportDrivers()
    
    def reset_post_count(self,command):
        self.postCount = 0
        self.setDriver("GV0", self.postCount)
        self.reportDrivers()

    id = 'plexclient'

    drivers = [
        {'driver': 'ST', 'value': 0, 'uom': 2},
        {'driver': 'GV0', 'value': 0, 'uom': 56}, 
        {'driver': 'GV1', 'value': 0, 'uom': 25},
        {'driver': 'GV2', 'value': 0, 'uom': 25},
        {'driver': 'GV3', 'value': 0, 'uom': 25},
        {'driver': 'GV4', 'value': 0, 'uom': 25},
        {'driver': 'GV5', 'value': 0, 'uom': 2},
    ]

    commands = { 
        'RESET': reset_values,
        'RESET_POST': reset_post_count
         }
    