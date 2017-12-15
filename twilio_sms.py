from twilio.rest import Client
from twilio_keys import twilio
from datetime import datetime, timedelta


# Twilio Initialization
ACCOUNT_SID = twilio['account_sid']
AUTH_TOKEN = twilio['auth_token']
TWILIO_NUMBER = twilio['twilio_number']
TO_NUMBER = '+17039695397'

client = Client(ACCOUNT_SID, AUTH_TOKEN)

# Adding fake data
print('inserting fake data')
reservations = [
    {'phone_number': "+17039695397", 'first': 'Fiona', 'last': 'Kim', 'date': '12/10/2017', 'fromTime': '21:00', 'toTime': '22:00', 'room': 'Brush Mountain A'}, 
    {'phone_number': "+17039695397", 'first': 'Fiona', 'last': 'Kim', 'date': '12/10/2017', 'fromTime': '22:10', 'toTime': '22:30', 'room': 'Brush Mountain A' }, 
    {'phone_number': "+17039695397", 'first': 'Fiona', 'last': 'Kim', 'date': '12/10/2017', 'fromTime': '23:18', 'toTime': '23:59', 'room': 'Brush Mountain A' }
    ]

def sendMessage(name, room, fromTime, toTime):
    client.messages.create(
    to=TO_NUMBER, 
    from_=TWILIO_NUMBER,
    body='{}, this your room reservation reminder! \n You have reserved {} from {} to {}.'.format(name, room, fromTime, toTime))

one_hour = timedelta(hours=1)
time_to_send = datetime.strptime('{} {}'.format(reservations[0]['date'], reservations[0]['toTime']), '%m/%d/%Y %H:%M')

now = datetime.now()
todays_date = datetime.strftime(now, '%m/%d/%Y')
print ('todays date: ', todays_date)
now = datetime.now() + one_hour
while 1:
    old_time = datetime.strftime(now, '%H:%M')
    now = datetime.now() + one_hour
    current_time = datetime.strftime(now, '%H:%M')
    if old_time !=  current_time:
        print('\none minute passed')
        current_time = datetime.strftime(now, '%H:%M')

        for reservation in reservations:
            reservation_time = reservation['fromTime']
            if reservation_time == current_time:
                name = reservation['first'] + reservation['last']
                room = reservation['room']
                # Make the times standard 12 HR format
                fromTime = datetime.strptime(reservation['fromTime'], '%H:%M')
                fromTime = datetime.strftime(fromTime, '%-I:%M %p')
                toTime = datetime.strptime(reservation['toTime'], '%H:%M')
                toTime = datetime.strftime(toTime, '%-I:%M %p')
                sendMessage(name, room, fromTime, toTime)
