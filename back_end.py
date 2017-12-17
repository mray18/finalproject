from __future__ import print_function
from flask import Flask, request
import database
import json
from bson import json_util
from bson.objectid import ObjectId
from pymongo import MongoClient
app = Flask(__name__)

#Mongo DB Connection
connection = MongoClient('localhost', 27017)
db = connection.reservations

@app.route('/reservations', methods=['GET', 'POST', 'PUT', 'DELETE'])
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
        newevent(phone_num, first, last, day, from_time, to_time, room)
    elif method == "GET":
        userevents(phone_num)
    elif method == "PUT":
        id = json_obj['_id']
        editevent(id, day, room, to_time, from_time)
    elif method == "DELETE":
        deleteevent(phone_num, first, last, day, from_time, to_time, room)

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
    results = db.reservations.find({'date':day},{'room':room})
    if not results:
        db.reservations.insert({'phone_number': phone_num, 'first': first, 'last': last, 'date': day, 'fromTime': from_time, 'toTime': to_time, 'room': room })
    for result in results:
        from_time1 = datetime.strptime(result["from_time"], '%H:%M')
        to_time1 = datetime.strptime(result["to_time"], '%H:%M')

        # time attempting to add
        from_time_obj = datetime.strptime(from_time, '%H:%M')
        to_time_obj = datetime.strptime(to_time, '%H:%M')

        # sees if the fromTime is within the range of the original time slot
        if from_time_obj >= from_time1 and from_time_obj <= to_time1:
            print('1 time conflict!')

        # sees if the toTime is within the range of the original time slot
        elif to_time_obj >= from_time1 and to_time_obj<= to_time1:
            print('2 time conflict!')

        else:
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
			
def userevents(phone_num):
    results = db.reservations.find({'phone_number':phone_num})
    return results

def editevent(id, day, room, to_time, from_time):
    results = db.reservations.find({'date':day},{'room':room})
    if not results:
        db.reservations.update_one({'_id': id}, {'$set':{'phone_number': phone_num, 'first': first, 'last': last, 'date': day, 'fromTime': from_time, 'toTime': to_time, 'room': room }})
    for result in results:
        from_time1 = datetime.strptime(result['from_time'], '%H:%M')
        to_time1 = datetime.strptime(result['to_time'], '%H:%M')

        # time attempting to add
        from_time_obj = datetime.strptime(from_time, '%H:%M')
        to_time_obj = datetime.strptime(to_time, '%H:%M')

        # sees if the fromTime is within the range of the original time slot
        if from_time_obj >= from_time1 and from_time_obj <= to_time1:
            print('1 time conflict!')

        # sees if the toTime is within the range of the original time slot
        elif to_time_obj >= from_time1 and to_time_obj<= to_time1:
            print('2 time conflict!')

        else:
            print('you\'re good')
            db.reservations.update_one({'_id': id}, {'$set':{'phone_number': phone_num, 'first': first, 'last': last, 'date': day, 'fromTime': from_time, 'toTime': to_time, 'room': room }})
    
def deleteevent(phone_num, first, last, day, from_time, to_time, room):
    db.reservations.delete_one({'phone_number': phone_num, 'first': first, 'last': last, 'date': day, 'fromTime': from_time, 'toTime': to_time, 'room': room })
    
def dailysearch(day):
    results = db.reservations.find({"date": day})
    json_results = []
    for result in results:
        json_results.append(result)
    return json.dumps(json_results, default=json_util.default)

if __name__ == '__main__':
    app.run('0.0.0.0', debug=True)
