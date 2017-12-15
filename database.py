#!/usr/bin/env python3

from pymongo import MongoClient
import time
import calendar

print('intializing mongo client')
client = MongoClient() # by default is connected to localhost
client.drop_database('reservations') # clear any previous entry from local db
db = client.reservations # re-initialize rover database
reservations = db.reservations # reservations

now = datetime.now()
todays_date = datetime.strftime(now, '%m/%d/%Y')

# default data
reservations.insert([
    {'phone_number': "+17039695397", 'first': 'Fiona', 'last': 'Kim', 'date': todays_date, 'fromTime': '21:00', 'toTime': '22:00', 'room': 'Brush Mountain A'}, 
    {'phone_number': "+17039695397", 'first': 'Fiona', 'last': 'Kim', 'date': todays_date, 'fromTime': '22:10', 'toTime': '22:30', 'room': 'Brush Mountain B' }, 
    {'phone_number': "+17039695397", 'first': 'Fiona', 'last': 'Kim', 'date': todays_date, 'fromTime': '23:18', 'toTime': '23:59', 'room': 'Brush Mountain A' }
])
