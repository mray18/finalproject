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
    {'phone_number': TO_NUMBER, 'first': 'Fiona', 'last': 'Kim', 'date': '12/10/2017', 'fromTime': '21:00', 'toTime': '22:00', 'room': 'Brush Mountain A' }, # 9PM - 10PM
    {'phone_number': TO_NUMBER, 'first': 'Fiona', 'last': 'Kim', 'date': '12/10/2017', 'fromTime': '22:00', 'toTime': '22:30', 'room': 'Brush Mountain A' }, # 10PM - 10:30PM
    {'phone_number': TO_NUMBER, 'first': 'Fiona', 'last': 'Kim', 'date': '12/10/2017', 'fromTime': '22:30', 'toTime': '23:00', 'room': 'Brush Mountain A' }  # 10:30PM - 11PM
    ]

def sendMessage(name, room):
    client.messages.create(
    to=TO_NUMBER, 
    from_=TWILIO_NUMBER,
    body='{}, this is a reminder for your room reservation! \n You have reserved {} from {} to {}.'.format(name, room, fromTime, toTime))

one_hour = timedelta(hours=1)
time_to_send = datetime.strptime('{} {}'.format(reservations[0]['date'], reservations[0]['toTime']), '%m/%d/%Y %H:%M')
print (time_to_send - one_hour)

now = datetime.now()
todays_date = datetime.strftime(now, '%m/%d/%Y')
print (todays_date)

while 1:
    now = datetime.now() + one_hour
    # Make API call here
    for reservation in reservations:
        reservation_time = datetime.strptime('{} {}'.format(reservation['date'], reservation['toTime']), '%m/%d/%Y %H:%M')
        if reservation_time <= now:
            name = reservation['first'] + reservation['last']
            room = reservation['room']
            # Make the times standard 12 HR format
            fromTime = datetime.strptime(reservation['fromTime'], '%H:%M')
            fromTime = datetime.strftime(fromTime, '%-I:%-M %p')
            print(fromTime)
            toTime = reservation['toTime']
            # sendMessage(name, room, fromTime, toTime)