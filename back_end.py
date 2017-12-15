from flask import Flask, request
import database

app = Flask(__name__)

#Mongo DB Connection
connection = MongoClient('localhost', 27017)
db = connection.reservations

@app.route('/reservations', methods=['GET', 'POST', 'PUT', 'DELETE'])
def eventfunc():
    method = request.method
    if method == "POST":
        newevent()
    elif method == "GET":
        userevents()
    elif method == "PUT":
        deleteevent()
        newevent()
    elif method == "DELETE":
        deleteevent()

@app.route('/reservations/<path:date>', methods=['GET'])
def twiliofunc(date):
    method = request.method
    if method == "GET":
        dailysearch(date)

def newevent(phone_num, first, last, day, from_time, to_time, room):
    results = db.reservations.find({"date"=day},{"room":room})
    if not results:
        db.reservations.insert({'phone_number': phone_num 'first': first, 'last': last, 'date': day, 'fromTime': from_time, 'toTime': to_time, 'room': room })
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
            db.reservations.insert({'phone_number': phone_num 'first': first, 'last': last, 'date': day, 'fromTime': from_time, 'toTime': to_time, 'room': room })
    
def userevents(phone_num):
    results = db.reservations.find({"phone_number":phone_num})
    return results
    
def deleteevent(phone_num, first, last, day, from_time, to_time, room):
    db.reservations.delete_one({'phone_number': phone_num 'first': first, 'last': last, 'date': day, 'fromTime': from_time, 'toTime': to_time, 'room': room })
        
def dailysearch(day):
    results = db.reservations.find({"date": day})
    return results

if __name__ == '__main__':
    app.run('0.0.0.0', debug=True)