from twilio.rest import Client
from twilio_keys import twilio
from datetime import datetime, timedelta
import requests

# Twilio Initialization
ACCOUNT_SID = twilio['account_sid']
AUTH_TOKEN = twilio['auth_token']
TWILIO_NUMBER = twilio['twilio_number']
TO_NUMBER = '+17039695397'

client = Client(ACCOUNT_SID, AUTH_TOKEN)

def sendMessage(name, room, fromTime, toTime):
    client.messages.create(
    to=TO_NUMBER, 
    from_=TWILIO_NUMBER,
    body='{}, this your room reservation reminder! \n You have reserved {} from {} to {}.'.format(name, room, fromTime, toTime))


one_hour = timedelta(hours=1)

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
        r = requests.get('http://localhost:5000/reservations/{}'.format(todays_date))
        reservations = r.json()
        print(reservations)

        for reservation in reservations:
            reservation_time = reservation['fromTime']
            if reservation_time == current_time:
                name = reservation['first'] + ' ' + reservation['last']
                room = reservation['room']
                # Make the times standard 12 HR format
                fromTime = datetime.strptime(reservation['fromTime'], '%H:%M')
                fromTime = datetime.strftime(fromTime, '%-I:%M %p')
                toTime = datetime.strptime(reservation['toTime'], '%H:%M')
                toTime = datetime.strftime(toTime, '%-I:%M %p')
                sendMessage(name, room, fromTime, toTime)
