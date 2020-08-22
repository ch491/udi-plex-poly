#!/usr/bin/env python3
"""
Plex Webhooks NodeServer for UDI Polyglot v2
by ch491 (Chad Hoevenaars) ch491@yahoo.com
"""
import polyinterface
import sys
# Grab the Plex Controller Class Definition from .\Nodes folder.
from nodes import PlexController

# Create a LOGGER to Polyglot.
LOGGER = polyinterface.LOGGER

if __name__ == "__main__":
    try:
        # Instantiate and Start the Interface to Polyglot & Plex Controller.
        polyglot = polyinterface.Interface('udi-plex-poly')
        polyglot.start()
        
        # Creates the Controller Node and passes in the Interface
        control = PlexController(polyglot,LOGGER)
        
        # Sit around and do nothing forever, keeping your program running.
        control.runForever()
        
    except (KeyboardInterrupt, SystemExit):
        # Catch SIGTERM or Control-C and exit cleanly.
        LOGGER.warning("Received interrupt or exit...")
        polyglot.stop()
        sys.exit(0)

    except Exception as err:
        LOGGER.error('Exception: {0}'.format(err), exc_info=True)
        sys.exit(0)
    
