from flask import Flask
from flask_sockets import Sockets
from flask import request, render_template
from datetime import datetime
import random

import threading

from oscpy.server import OSCThreadServer
import time
from time import sleep
import json

# remove this
import scipy


app = Flask(__name__, static_url_path='/static')
sockets = Sockets(app)



# PARTICIPANTS
unique_ips = []

participant_dict = {'participants': []}


# HANDLE USERS
def create_user(ip):
	one_participant = {ip: {'noin_balance': 0, 'tmp_value': 0}}
	participant_dict['participants'].append(one_participant)

def dict_to_file(input_data, fname):
	print("yaaas")
	print(input_data)
	with open('files/'+fname, 'w+') as f:
		f.write(json.dumps(input_data))


# class Noiner():
#
#     def __init__(self, name):
#     self.name = name


# TEMPORARY GLOBALS
noin_ios = 0
tmp_ios = 0



# GENERAL PURPOSE
def activity2noin(difference, weight, max_value, minimization):
	# normalized = (x-min(x))/(max(x)-min(x))
	tmp = (difference-(weight+1))/(max_value-(weight+1))
	out = 1-tmp
	print("OUT: ", out)

	# disqualify the scenario when someone just leaves the phone on the table as invalid noining
	if out >= 1:
		return 0
	elif out < 0:
		return 0
	else:
		return out/minimization


def activity2noin_intense(difference):
	if 12 < difference < 17:
		return difference/100
	elif 17 < difference < 27:
		return difference/1000
	else:
		return 0



def intensity_calculator(input_data, tmp, weight, equalizer):
	if input_data['sensor'] == 'accelerometer':
		cur_vals = [abs(float(n)) for n in input_data['message']]
		cur_val = sum(cur_vals*equalizer)

		if cur_val < weight:
			cur_val = tmp
		else:
			pass

		#print("CUR_VAL: ", cur_val)
		#print("TMP: ", tmp)
		difference = abs(tmp-cur_val)
		print("DIFF: ", difference)

		#new_diff = activity2noin(difference, weight, max_value, 1000)
		new_diff = activity2noin_intense(difference)
		new_diff_small = new_diff/10000

		#print(new_diff)
		# this second value depends on the range of
		#new_diff = activity2noin(normalized, max_value)
		print("NEW DIFF: ", new_diff_small)
		return new_diff_small
	else:
		return 0


# LANDING PAGE
@app.route('/noin')
def one():
	return render_template('index.html', results=participant_dict)


@app.route('/instructions')
def two():
	return render_template('instructions.html')

@app.route('/second')
def three():
	return render_template('noin.html')


@app.route('/whitepaper')
def four():
	return render_template('whitepaper.html')

# @app.route('/chart-data')
# def chart_data():
#     global participant_dict
#     def generate_random_data():
#         while True:
#             json_data = json_dumps(participant_dict)
#             yield f"data:{json_data}\n\n"
#             time.sleep(1)
#     return Response(generate_random_data(), mimetype='text/event-stream')

# print("TEST GRD: ", participant_dict)
# json_data = json.dumps(participant_dict)
# yield f"data:{json_data}\n\n"
# time.sleep(1)

# ANDROID
@sockets.route('/accelerometer')
def echo_socket(ws):
	#f=open("accelerometer.txt","a")
	#noin = 0
	#tmp = 0

	# handle users
	ip = request.remote_addr
	print(ip)

	if ip not in unique_ips:
		unique_ips.append(ip)
		create_user(ip)
	else:
		pass


	#print(participant_dict)
	participant = participant_dict['participants'][0][str(ip)]
	#print(participant)

	#print("Participant: ", participant)
	noin = participant['noin_balance']
	tmp = participant['tmp_value']
	#print("Noin: ", noin)
	#print("Tmp: ", tmp)


	while True:
		message = ws.receive()
		#print(message)
		#ip = request.remote_addr
		ws.send(message)
		vals = message.split(',')
		output = {'ip': ip, 'sensor': 'accelerometer', 'message': vals}
		#if it's below one don't sum anything
		#print(output)

		difference = intensity_calculator(output, tmp, 12, 1)
		#print('New difference: ', difference)

		noin += difference
		participant['noin_balance'] = noin
		participant['tmp_value'] = difference
		print(participant)
		print(output)

		participant_dict['participants'][0][str(ip)].update(participant)

		#print('Yaaas mined: ', ip, noin )
		#print('Noins mined:', participant)
		#dict_to_file(participant_dict, 'wallet.json', 5)

		#print(noin, file=f)
		#tmp = difference

		# IPHONE TESTING
		# output = {'ip': ip, 'sensor': 'accelerometer', 'message': message}
		# print(output)
		#print(participant_dict)
		dict_to_file(participant_dict, 'wallet.json')


# IOS


def identify_me(values):
    print(osc.get_sender())

def callback_ios(*values):
	# THIS IS HOW YOU PRINT EVERYTHING FROM KWARGS
	#print(dir(values))
	print(repr(values))


	#vals = [x,y,z]
	#global tmp_ios
	#global noin_ios
	#ip = request.remote_addr
	#print(ip)
	#print(vals)
	#return vals
	#print(list)
	# output = {'ip': 'fakeip', 'sensor': 'accelerometer', 'message': vals}
	# #print(output)
	#
	# difference = intensity_calculator(output, tmp_ios, 12, 10)
	# print("DIFF: ", difference)
	# noin_ios += difference
	#
	# print('Noins mined: ', noin_ios )




def loop_android():
	while True:
		server = pywsgi.WSGIServer(('0.0.0.0', 5000), app, handler_class=WebSocketHandler, log=app.logger)
		server.serve_forever()

		# print('android works!')
		# time.sleep(1)

		# call handler function

def loop_ios():
	while True:
		# print("IOS works!")
		# time.sleep(1)
		osc = OSCThreadServer()
		sock = osc.listen(address='0.0.0.0', port=7400, default=True)

		#osc.bind(b'/accxyz', callback_ios)
		osc.bind(b'/accxyz', callback_ios, get_address=True)

		sleep(10000)
		osc.stop()

if __name__ == "__main__":
	from gevent import pywsgi
	from geventwebsocket.handler import WebSocketHandler


	x = threading.Thread(target=loop_android)
	x.start()

	y = threading.Thread(target=loop_ios)
	y.start()
