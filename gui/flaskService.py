#/flask/bin/python3
from flask import *
import netifaces

ips = netifaces.ifaddresses('wlan0')
tempList = ips[2]
var = tempList[0]
address = var['addr']

app = Flask(__name__)
@app.route('/')
def home(iaddress=address):
    return render_template('index.html', iaddress=iaddress)

@app.route('/createEvent')
def create():
   return render_template('newEvent.html')
@app.route('/updateEvent')
def update():
   return render_template('updateEvent.html')



app.run(host=address, port=9000, debug=False)