""" 
TODO:
	Security
	Service
	Control Pannel Home Page

"""

from flask import Flask, request, jsonify
from flask import url_for

app = Flask(__name__)

import iproute2 as ip2

@app.route('/')
def hello_world():
    return 'Hello, World!'

# TODO make iproute2 service in flask
@app.route('/api/v0/iproute2/neighbor', methods=['GET'])
def get_neighbors():
    return jsonify(ip2.neighbors())

@app.route('/api/v0/iproute2/route', methods=['GET'])
def get_routes():
    return jsonify(ip2.route())

@app.route('/api/v0/iproute2/maddr', methods=['GET'])
def get_maddr():
    return jsonify(ip2.maddr())

# TODO make POST or accept query parameters
@app.route('/api/v0/tc', methods=['GET'])
def get_tc():
    # TODO grab command values
    status, retval = ip2.tc("qdisc", "ls", "wlp3s0", {'statistics' : True, 'details': True})  
    return jsonify(retval)


if __name__ == '__main__':
    app.run(debug=True)
