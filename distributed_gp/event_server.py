#!/usr/bin/python
# -*- coding: utf8 -*-

import cherrypy
import foursquare
import config
import json
import time


from utility.event_interface import EventInterface
from utility.event import Event



class Root:
    def __init__(self):
        self.ei = EventInterface('candidate_event_10by10_merged')
        pass
    
    def getAllEvents(self):
        events = ei.getAllDocuments()
        return events
    getAllEvents.exposed = True 
    
    def getTopKeywords(self, event_id):
        event = ei.getEventByID(event_id)
        # call compute keywords component here
        return [('nyc',1),('ahahah',2)]
    getTopKeywords.exposed = True

    def setLabel(self, event_id, label):
        label = str(label)
        event = ei.getEventByID(event_id)
        event.setLabel(int(label))
        ei.updateDocument(event)

global_conf = {
        'global':{'server.environment': 'production',
            'engine.autoreload_on': True,
            'engine.autoreload_frequency':5,
            'server.socket_host': '0.0.0.0',
            'server.socket_port':7887,
            }
        }

cherrypy.config.update(global_conf)
cherrypy.quickstart(Root(), '/', global_conf)
