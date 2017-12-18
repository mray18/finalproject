#!/usr/bin/env python3

from __future__ import print_function
from flask import Flask, request
from flask_restful import abort
import database
import json
from bson import json_util
from bson.objectid import ObjectId
from pymongo import MongoClient
from datetime import datetime
app = Flask(__name__)

#--------------------For Google Calendar---------------------
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

# from apiclient import discovery
# import oauth2client
# from oauth2client import client
# from oauth2client import tools
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

#---------------------Google Calendar credentials---------------------
SCOPES = 'https://www.googleapis.com/auth/calendar'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Calendar API Python'


def get_credentials():
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir, 'calendar-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    flags = None
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

#Mongo DB Connection
connection = MongoClient('localhost', 27017)
db = connection.reservations

#---------------------GET by DATE for TWILIO-------------------------
@app.route('/reservations/<path:date>', methods=['GET'])
def twiliofunc(date):
    method = request.method
    if method == "GET":
        return dailysearch(date)

def dailysearch(day):
    results = db.reservations.find({"date": day})
    return toJSON(results)
#----------------------------------------------------------------------

#---------------------GET reservations by PHONE NUMBER---------------------
@app.route('/reservations/<string:phone_num>', methods=['GET'])
def phonefunc(phone_num):
    method = request.method
    phone_num = '+1' + phone_num
    if method == "GET":
        return userevents(phone_num)
    
def userevents(phone_num):
    results = db.reservations.find({'phone_number':phone_num})
    return toJSON(results)
#----------------------------------------------------------------------

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

    if method == "POST":
        return newevent(phone_num, first, last, day, from_time, to_time, room)
    elif method == "PUT":
        id = json_obj['_id']['$oid']
        gcal_id = json_obj['gcal_id']
        return editevent(id, phone_num, first, last, day, from_time, to_time, room, gcal_id)
    elif method == "DELETE":
        gcal_id = json_obj['gcal_id']
        return deleteevent(phone_num, first, last, day, from_time, to_time, room, gcal_id)

def newevent(phone_num, first, last, day, from_time, to_time, room):
    start = googleDate(day, from_time)
    end = googleDate(day, to_time)
    time_conflict = False
    results = db.reservations.find({'date':day, 'room':room})
    json_results = []
    for result in results:
        json_results.append(result)
    # check is array is empty
    if json_results:
        results = db.reservations.find({'date':day, 'room':room})
        for result in results:
            from_time1 = datetime.strptime(result["fromTime"], '%H:%M')
            to_time1 = datetime.strptime(result["toTime"], '%H:%M')
            # time attempting to add
            from_time_obj = datetime.strptime(from_time, '%H:%M')
            to_time_obj = datetime.strptime(to_time, '%H:%M')

            print('comparing the following: {} {} {}'.format(from_time_obj, from_time1, to_time1))
            print('comparing the following: {} {} {}'.format(to_time_obj, from_time1, to_time1))
            # sees if the fromTime is within the range of the original time slot
            if from_time_obj >= from_time1 and from_time_obj < to_time1:
                time_conflict = True
                print('from_time time conflict!')
            # sees if the toTime is within the range of the original time slot
            elif to_time_obj > from_time1 and to_time_obj<= to_time1:
                time_conflict = True
                print('to_time time conflict!')

    if time_conflict:
        error_obj = {'errorMessage': 'time conflict'}
        return json.dumps(error_obj), 403
    else:
        print('no conflict!')
        calendarid = postToGoogle(room, first, last, start, end, phone_num)
        entry_id = db.reservations.insert({'phone_number': phone_num, 'first': first, 'last': last, 'date': day, 'fromTime': from_time, 'toTime': to_time, 'room': room , 'gcal_id' : calendarid})
        return toJSON(db.reservations.find({'_id': ObjectId(entry_id)}))

def postToGoogle(room, first, last, start, end, phone_num):
    #---------------------Create the event in Google Calendar-------------------------
    credentials = get_credentials()
    print('\n\n\ncredentials: ', credentials)
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)
    
    event = {
        'summary': 'Raspberry Room Reservation',
        'location': room,
        'description': ("Reservation for {}, created by {} {}.").format(room,first,last),
        'start': {
            'dateTime': start,
            'timeZone': 'EST',
        },
        'end': {
            'dateTime': end,
            'timeZone': 'EST',
        },
        'attendees': {
            'phone': phone_num,
        },
    }
    event = service.events().insert(calendarId='primary', body=event).execute()
    calendarid = event.get('id')
    print ('You may confirm your event here: %s' % (event.get('htmlLink')))
    return calendarid
#----------------------------------------------------------------------------------

def editevent(id, phone_num, first, last, day, from_time, to_time, room, gcal_id):
    time_conflict = False
    results = db.reservations.find({'date':day, 'room':room})
    json_results = []
    for result in results:
        json_results.append(result)
    # check is array is empty
    # check is array is empty
    if json_results:
        results = db.reservations.find({'date':day, 'room':room})
        for result in results:
            from_time1 = datetime.strptime(result["fromTime"], '%H:%M')
            to_time1 = datetime.strptime(result["toTime"], '%H:%M')
            # time attempting to add
            from_time_obj = datetime.strptime(from_time, '%H:%M')
            to_time_obj = datetime.strptime(to_time, '%H:%M')
            # sees if the fromTime is within the range of the original time slot
            if from_time_obj >= from_time1 and from_time_obj < to_time1:
                time_conflict = True
                print('from_time time conflict!')
            # sees if the toTime is within the range of the original time slot
            elif to_time_obj > from_time1 and to_time_obj<= to_time1:
                time_conflict = True
                print('to_time time conflict!')

    if time_conflict:
        error_obj = {'errorMessage': 'time conflict'}
        return json.dumps(error_obj), 403
    else:
        print('you\'re good')
        # Edit in Google Calendar
        start = googleDate(day, from_time)
        end = googleDate(day, to_time)
        editGoogle(gcal_id, room, first, last, start, end, phone_num)
        # Edit in the Database
        db.reservations.update_one({'_id': ObjectId(id)}, {'$set':{'phone_number': phone_num, 'first': first, 'last': last, 'date': day, 'fromTime': from_time, 'toTime': to_time, 'room': room }})
        # return object to user
        return toJSON(db.reservations.find({'_id': ObjectId(id)}))

# Edit event in google calendar based off of gcal_id
def editGoogle(gcal_id, room, first, last, start, end, phone_num):   
     #---------------------Edit the event in Google Calendar-------------------------
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)
    
    event = service.events().get(calendarId='primary', eventId=gcal_id).execute()
    
    event['summary'] = 'Raspberry Room Reservation'
    event['location'] = room
    event['description'] = ("Reservation for {}, created by {} {}.").format(room,first,last)
    event['start'] = {
            'dateTime': start,
            'timeZone': 'EST',
    }
    event['end'] = {
            'dateTime': end,
            'timeZone': 'EST',
    }
    event['attendees'] = {
            'phone': phone_num,
    }
    
    updated_event = service.events().update(calendarId='primary', eventId=gcal_id, body=event).execute()
    print("Your event has been updated!")
    print('Please feel free to confirm your changes here: %s' % (event.get('htmlLink')))
#----------------------------------------------------------------------------------

def deleteevent(phone_num, first, last, day, from_time, to_time, room, gcal_id):
    # Delete from Google Calendar
    deleteGoogle(gcal_id)
    # Delete from MongoDB
    result = db.reservations.delete_one({'phone_number': phone_num, 'first': first, 'last': last, 'date': day, 'fromTime': from_time, 'toTime': to_time, 'room': room, 'gcal_id': gcal_id})
    # Return deleted object count to user
    delete_obj = {'deleted count': result.deleted_count}
    return json.dumps(delete_obj, indent=2)

def deleteGoogle(gcal_id):
    #---------------------Delete the event in Google Calendar-------------------------
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)
    service.events().delete(calendarId='primary', eventId=gcal_id).execute()
    print("Your event has been deleted :(")
#----------------------------------------------------------------------------------

# Helper function to take PyMongo cursor objects,
# iterate through them, and convert them to JSON arrays.
def toJSON(results):
    json_results = []
    for result in results:
        json_results.append(result)
    return json.dumps(json_results, default=json_util.default)

# Helper function to for google calendar's time field
def googleDate(day, time):
    date_obj= datetime.strptime('{} {}'.format(day, time), '%m/%d/%Y %H:%M')
    date_string = datetime.strftime(date_obj, '%Y-%m-%dT%H:%M:%S')
    return date_string


if __name__ == '__main__':
    app.run('0.0.0.0', debug=True)
