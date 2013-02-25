from event_interface import EventInterface
from event_feature import EventFeature
from photo_interface import PhotoInterface
from photo import Photo
from region import Region
from event import Event
from caption_parser import CaptionParser
from stopwords import Stopwords
from bson.objectid import ObjectId

import operator
import string
import types
import random
import math


#unique_id = set()
#photo_n = 0
#event_n = 0


ei = EventInterface()
ei.setDB('citybeat')
ei.setCollection('candidate_event_25by25_merged')

events = ei.getAllDocuments()
for event in events:
	e = Event(event)
	if event['actual_value'] < 10:
		continue
	try:
		for photo in event['photos']:
			print Photo(photo).getLocationName()
	except Exception as e:
		print 


