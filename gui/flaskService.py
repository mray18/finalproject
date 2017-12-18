#/flask/bin/python3
from flask import *
import netifaces
import zeroconfiguration

ips = netifaces.ifaddresses('wlan0')
tempList = ips[2]
var = tempList[0]
address = var['addr']

BACKEND_IP = 'http://' + zeroconfiguration.get_address() + ':5000/reservations'
backIP = zeroconfiguration.get_address()

app = Flask(__name__)
@app.route('/')
def home(iaddress=address, baddress=backIP):
    return render_template('index.html', iaddress=iaddress, baddress=baddress)

@app.route('/createEvent')
def create(iaddress=address, baddress=backIP):
   return render_template('newEvent.html', iaddress=iaddress, baddress=baddress)
@app.route('/updateEvent')
def update(baddress=backIP, iaddress=address):
   return render_template('updateEvent.html',baddress=baddress, iaddress=iaddress)

@app.route('/postmethod', methods = ['POST'])
def get_post_javascript_data():
    jsdata = request.form['javascript_data']
    return json.loads(jsdata)[0]




app.run(host=address, port=9000, debug=False)