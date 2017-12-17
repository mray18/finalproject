from __future__ import print_function
from flask import Flask, request
import database
import json
from bson import json_util
from bson.objectid import ObjectId
from pymongo import MongoClient
from datetime import datetime, timedelta
app = Flask(__name__)

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

    if method == "POST":
        return newevent(phone_num, first, last, day, from_time, to_time, room)
    elif method == "PUT":
        id = json_obj['_id']['$oid']
        print ('ObjectId: ', ObjectId(id))
        return editevent(id, phone_num, first, last, day, from_time, to_time, room)
    elif method == "DELETE":
        return deleteevent(phone_num, first, last, day, from_time, to_time, room)

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
<<<<<<< HEAD
            print('no conflict!')
            entry_id = db.reservations.insert({'phone_number': phone_num, 'first': first, 'last': last, 'date': day, 'fromTime': from_time, 'toTime': to_time, 'room': room })
            return toJSON(db.reservations.find({'_id': ObjectId(entry_id)}))
    error_obj = {'error': 'time conflict found'}
    return json.dumps(error_obj, indent=2)
    
=======
            print('you\'re good')
            db.reservations.insert({'phone_number': phone_num, 'first': first, 'last': last, 'date': day, 'fromTime': from_time, 'toTime': to_time, 'room': room })
			
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
            print ('Event created: %s' % (event.get('htmlLink')))
	    #----------------------------------------------------------------------------------
			
>>>>>>> 761aed37b07f70fff2aac6a1716480bfeccae969
def userevents(phone_num):
    results = db.reservations.find({'phone_number':phone_num})
    return toJSON(results)

def editevent(id, phone_num, first, last, day, from_time, to_time, room):
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
            return toJSON(db.reservations.find({'_id': ObjectId(id)}))
    
    error_obj = {'error': 'time conflict found'}
    return json.dumps(error_obj, indent=2)

def deleteevent(phone_num, first, last, day, from_time, to_time, room):
    result = db.reservations.delete_one({'phone_number': phone_num, 'first': first, 'last': last, 'date': day, 'fromTime': from_time, 'toTime': to_time, 'room': room })
    delete_obj = {'deleted count': result.deleted_count}
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
