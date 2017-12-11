#/flask/bin/python3
from flask import *
import netifaces


app = Flask(__name__)
@app.route('/')
def home():
   return render_template('newEvent.html')

ips = netifaces.ifaddresses('wlan0')
tempList = ips[2]
var = tempList[0]
address = var['addr']


app.run(host=address, port=9000, debug=False)