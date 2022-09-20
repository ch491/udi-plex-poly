# UDI Plex Poly
This is an integation of [Plex Webhooks](https://support.plex.tv/articles/115002267687-webhooks/) for the ISY994i via PolyglotV2.
Please report any problems on [GitHub Repository](https://github.com/ch491/udi-plex-poly/issues).
(c) 2020 Chad Hoevenaars
MIT license.

This node server is intended to support the [Plex Media Server Webhooks](https://support.plex.tv/articles/115002267687-webhooks/)

This node server will listen for POSTs "Webhooks" from a Plex Media Server.
1) You can create programs to react to Plex client events.
 i.e. When you start a movie change your lighting. 
      When the movie is 90% done, (Plex calls this a Scobble) you can return lights to normal. 
2) It has a special feature 'rapid_trigger' that when on can alert you is a user is causing too many events in a given time. 
 i.e. If you have kids that think it is fun to play/pause repeatedly you can write a program to alert you. 

## Installation

1. Backup Your ISY in case of problems!
   * Really, do the backup, please
2. Go to the Polyglot Store in the UI and install.
3. Add NodeServer in Polyglot Web
   * After the install completes it waits 10 seconds to start the node server.
4. You should reload your ISY Admin to get all the setting. 
5. After the node server starts you can read the log or goto the Configuration Help page (on Ployglot Web Interface) to see the IP and port the nodeserver is listening on. 
6. Goto your Plex Media Server (PMS) and under settings you will see 'Webhooks' set the URL to the path from step 5.   
7. Under Settings / Network on the Plex Server turn on (check box) Webhooks. 
8. Then all you have to do is goto any Plex Client (Player) and cause an event. 
9. When the node server sees any new client event, it will create a Client Node in your ISY.
10. To remove old clients goto the Ployglot Web Interface / Plex-Webhook / Details / Nodes and you can click Delete [X] to delete that node. 

### Node Settings
The settings for this node server are:

#### Short Poll
   If your have turned on the rapid_trigger feature this will reset the Rapid Trigger flag to false every shortPoll.
#### Long Poll
   Checks that the HTTP Listener is still running and will restart if stopped. 

#### Custom Parameters 
   * Add custom parameters with by suppling the name (port or rapid_trigger)
   * Setting 'port' to a value between 1024-49151 will override the listening port (Default 9090). 
   * Setting 'rapid_trigger' to a value in seconds that is used to determine the window for rapid events. (Default is 0 - Feature Off)


## Requirements

1. Polyglot V2.
2. This has only been tested with ISY v5.0.16C so it is not guaranteed to work with any other version.

# Upgrading

Open the Polyglot web page, go to nodeserver store and click "Update" for "Plex-WebHook".

# Release Notes

- 1.0.0 08/24/2020
   - Full creation of Plex WebHook Polyglot NodeServer.
