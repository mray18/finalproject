#!/usr/bin/env python3

from pymongo import MongoClient
from datetime import datetime, timedelta

print('intializing mongo client')
client = MongoClient() # by default is connected to localhost
client.drop_database('reservations') # clear any previous entry from local db
db = client.reservations # re-initialize rover database
reservations = db.reservations # reservations

now = datetime.now()
todays_date = datetime.strftime(now, '%m/%d/%Y')

# default data
reservations.insert([
    {'phone_number': "+17039695397", 'first': 'Fiona', 'last': 'Kim', 'date': todays_date, 'fromTime': '21:00', 'toTime': '22:00', 'room': 'Brush Mountain A', 'gcal_id' : '0'}, 
    {'phone_number': "+17039695397", 'first': 'Fiona', 'last': 'Kim', 'date': todays_date, 'fromTime': '22:10', 'toTime': '22:30', 'room': 'Brush Mountain B', 'gcal_id' : '0'}, 
    {'phone_number': "+17039695397", 'first': 'Fiona', 'last': 'Kim', 'date': todays_date, 'fromTime': '23:18', 'toTime': '23:59', 'room': 'Brush Mountain A', 'gcal_id' : '0'},
    {'phone_number': "+17039695397", 'first': 'Fiona', 'last': 'Kim', 'date': '12/20/2017', 'fromTime': '23:18', 'toTime': '23:59', 'room': 'Brush Mountain A', 'gcal_id' : '0'}
])
