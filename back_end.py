#!/usr/bin/env python3

from __future__ import print_function
from flask import Flask, request
import database
import json
from bson import json_util
from bson.objectid import ObjectId
from pymongo import MongoClient
from datetime import datetime, timedelta
app = Flask(__name__)

#--------------------For Google Calendar---------------------
import httplib2
import os

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools

import datetime
#------------------------------------------------------------

#---------------Possible Zero-Configuration------------------
import sys
import time
import logging
import socket
from zeroconf import ServiceInfo, Zeroconf

#Get the IP address of the back-end Raspberry Pi
def get_ip_address():
    ip_address = '';
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8",80))
    ip_address = s.getsockname()[0]
    s.close()
    return ip_address
	
try:
    # From this link: https://github.com/jstasiak/python-zeroconf/blob/master/examples/registration.py
    logging.basicConfig(level=logging.DEBUG)
    if len(sys.argv) > 1:
        assert sys.argv[1:] == ['--debug']
        logging.getLogger('zeroconf').setLevel(logging.DEBUG)
        
    desc = {'Description': 'Zero-configuration for Team 14-Final Project in ECE 4564.'}

    #Get the local IP address of the Pi running led.py
    localip = socket.inet_aton(get_ip_address())
    
    info = ServiceInfo("_http._tcp.local.",
                       "Team14RaspberryRoomReservation._http._tcp.local.",
                       localip, 8081, 0, 0, desc
                       )
    
    zeroconf = Zeroconf()
    zeroconf.register_service(info)
    print("Zeroconf service registered.")
        
except:
    pass
#------------------------------------------------------------

#Mongo DB Connection
connection = MongoClient('localhost', 27017)
db = connection.reservations

@app.route('/reservations', methods=['POST', 'PUT', 'DELETE'])
def eventfunc():
    method = request.method
    json_obj = request.get_json()
    phone_num = json_obj['phone_number'] 
    first = json_obj['first']
    last = json_obj['last']
    day = json_obj['date']
    from_time = json_obj['fromTime']
    to_time = json_obj['toTime']
    room = json_obj['room']
	
    #--new--
    gcal_id = json_obj['gcal_id']
    #-------

    if method == "POST":
        return newevent(phone_num, first, last, day, from_time, to_time, room)
    elif method == "PUT":
        id = json_obj['_id']['$oid']
        print ('ObjectId: ', ObjectId(id))
        return editevent(id, phone_num, first, last, day, from_time, to_time, room, gcal_id)
    elif method == "DELETE":
        return deleteevent(phone_num, first, last, day, from_time, to_time, room, gcal_id)

@app.route('/reservations/<string:phone_num>', methods=['GET'])
def phonefunc(phone_num):
    method = request.method
    phone_num = '+1' + phone_num
    if method == "GET":
        return userevents(phone_num)

@app.route('/reservations/<path:date>', methods=['GET'])
def twiliofunc(date):
    method = request.method
    if method == "GET":
        return dailysearch(date)


#---------------------Google Calendar credentials---------------------
SCOPES = 'https://www.googleapis.com/auth/calendar'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Calendar API Python'


def get_credentials():
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'calendar-python.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials
#----------------------------------------------------------------------

def newevent(phone_num, first, last, day, from_time, to_time, room):
    results = db.reservations.find({'date':day}, {'room':room})
    json_results = []
    for result in results:
        json_results.append(result)
    # check is array is empty
    if not json_results:
        entry_id = db.reservations.insert({'phone_number': phone_num, 'first': first, 'last': last, 'date': day, 'fromTime': from_time, 'toTime': to_time, 'room': room })
        return toJSON(db.reservations.find({'_id': ObjectId(entry_id)}))
    for result in results:
        from_time1 = datetime.strptime(result["from_time"], '%H:%M')
        to_time1 = datetime.strptime(result["to_time"], '%H:%M')

        # time attempting to add
        from_time_obj = datetime.strptime(from_time, '%H:%M')
        to_time_obj = datetime.strptime(to_time, '%H:%M')

        # sees if the fromTime is within the range of the original time slot
        if from_time_obj >= from_time1 and from_time_obj <= to_time1:
            print('from_time time conflict!')

        # sees if the toTime is within the range of the original time slot
        elif to_time_obj >= from_time1 and to_time_obj<= to_time1:
            print('to_time time conflict!')

        else:
#<<<<<<< HEAD
            print('no conflict!')
	    #---------------------Create the event in Google Calendar-------------------------
            credentials = get_credentials()
            http = credentials.authorize(httplib2.Http())
            service = discovery.build('calendar', 'v3', http=http)
			
            event = {
              'summary': 'Raspberry Room Reservation',
              'location': room,
              'description': ("Reservation for {}, created by {} {}.").format(room,first,last),
              'start': {
                    'dateTime': ("{}T{}").format(day,from_time),
                    'timeZone': 'EST',
              },
              'end': {
                    'dateTime': ("{}T{}").format(day,to_time),
                    'timeZone': 'EST',
              },
              'attendees': {
                    'phone': phone_num,
              },
            }
            event = service.events().insert(calendarId='primary', body=event).execute()
            calendarid = event.get('id')
            print ('You may confirm your event here: %s' % (event.get('htmlLink')))
            #----------------------------------------------------------------------------------
            entry_id = db.reservations.insert({'phone_number': phone_num, 'first': first, 'last': last, 'date': day, 'fromTime': from_time, 'toTime': to_time, 'room': room , 'gcal_id' : calendarid})
            print('you\'re good')
            return toJSON(db.reservations.find({'_id': ObjectId(entry_id)}))
    error_obj = {'error': 'time conflict found'}
    return json.dumps(error_obj, indent=2)
    
#=======		
			
#>>>>>>> 761aed37b07f70fff2aac6a1716480bfeccae969
def userevents(phone_num):
    results = db.reservations.find({'phone_number':phone_num})
    return toJSON(results)

def editevent(id, phone_num, first, last, day, from_time, to_time, room, gcal_id):
    results = db.reservations.find({'date':day, 'room':room})
    json_results = []
    for result in results:
        json_results.append(result)
    # check is array is empty
    if not json_results:
        db.reservations.update_one({'_id': ObjectId(id)}, {'$set':{'phone_number': phone_num, 'first': first, 'last': last, 'date': day, 'fromTime': from_time, 'toTime': to_time, 'room': room }})
        return toJSON(db.reservations.find({'_id': ObjectId(id)}))
    for result in results:
        from_time1 = datetime.strptime(result['from_time'], '%H:%M')
        to_time1 = datetime.strptime(result['to_time'], '%H:%M')

        # time attempting to add
        from_time_obj = datetime.strptime(from_time, '%H:%M')
        to_time_obj = datetime.strptime(to_time, '%H:%M')

        # sees if the fromTime is within the range of the original time slot
        if from_time_obj >= from_time1 and from_time_obj <= to_time1:
            print('from_time time conflict!')

        # sees if the toTime is within the range of the original time slot
        elif to_time_obj >= from_time1 and to_time_obj<= to_time1:
            print('to_time time conflict!')

        else:
            print('you\'re good')
            db.reservations.update_one({'_id': ObjectId(id)}, {'$set':{'phone_number': phone_num, 'first': first, 'last': last, 'date': day, 'fromTime': from_time, 'toTime': to_time, 'room': room }})
				
	    #---------------------Edit the event in Google Calendar-------------------------
            credentials = get_credentials()
            http = credentials.authorize(httplib2.Http())
            service = discovery.build('calendar', 'v3', http=http)
			
            event = service.events().get(calendarId='primary', eventId=id).execute()
			
            event['summary'] = 'Raspberry Room Reservation'
            event['location'] = room
            event['description'] = ("Reservation for {}, created by {} {}.").format(room,first,last)
            event['start'] = {
                    'dateTime': ("{}T{}").format(day,from_time),
                    'timeZone': 'EST',
            }
            event['end'] = {
                    'dateTime': ("{}T{}").format(day,to_time),
                    'timeZone': 'EST',
            }
            event['attendees'] = {
                    'phone': phone_num,
            }
            
            updated_event = service.events().update(calendarId='primary', eventId=gcal_id, body=event).execute()
            print("Your event has been updated!")
            print('Please feel free to confirm your changes here: %s' % (event.get('htmlLink')))
	    #----------------------------------------------------------------------------------
            return toJSON(db.reservations.find({'_id': ObjectId(id)}))
    
    error_obj = {'error': 'time conflict found'}
    return json.dumps(error_obj, indent=2)

def deleteevent(phone_num, first, last, day, from_time, to_time, room, gcal_id):
    result = db.reservations.delete_one({'phone_number': phone_num, 'first': first, 'last': last, 'date': day, 'fromTime': from_time, 'toTime': to_time, 'room': room, 'gcal_id': gcal_id})
    delete_obj = {'deleted count': result.deleted_count}
    service.events().delete(calendarId='primary', eventId=gcal_id).execute()
    return json.dumps(delete_obj, indent=2)
    
def dailysearch(day):
    results = db.reservations.find({"date": day})
    return toJSON(results)

# Helper function to take PyMongo cursor objects,
# iterate through them, and convert them to JSON arrays.
def toJSON(results):
    json_results = []
    for result in results:
        json_results.append(result)
    return json.dumps(json_results, default=json_util.default)

if __name__ == '__main__':
    app.run('0.0.0.0', debug=True)
