#/flask/bin/python3
from flask import *
import netifaces
import zero-configuration

ips = netifaces.ifaddresses('wlan0')
tempList = ips[2]
var = tempList[0]
address = var['addr']

BACKEND_IP = 'http://' + zero-configuration.get_address() + ':5000/reservations'

app = Flask(__name__)
@app.route('/')
def home(iaddress=address):
    return render_template('index.html', iaddress=iaddress)

@app.route('/createEvent')
def create(iaddress=address):
   return render_template('newEvent.html', iaddress=iaddress)
@app.route('/updateEvent')
def update():
   return render_template('updateEvent.html')

@app.route('/postmethod', methods = ['POST'])
def get_post_javascript_data():
    jsdata = request.form['javascript_data']
    return json.loads(jsdata)[0]




app.run(host=address, port=9000, debug=False)