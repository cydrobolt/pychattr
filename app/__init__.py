from flask import Flask, render_template, session, request
from flask.ext.socketio import SocketIO, join_room, leave_room, emit, send
from uuid import uuid4
import os, redis
from flask_kvsession import KVSessionExtension
from simplekv.memory.redisstore import RedisStore

store = RedisStore(redis.StrictRedis())
'''
# PyChattr Server
# [c] Copyright 2014 Chaoyi Zha
# </>ed w/ <3 in Philly in '14
# Authors: Chaoyi Zha <summermontreal@gmail.com>
# Licensed under GPLv2, or later. Read LICENSE for more info.
'''

app = Flask(__name__)

KVSessionExtension(store, app)

app.config['SECRET_KEY'] = 'secret!'
app.config['MUTUAL_SECRET'] = 'tcynAU*CT47KFe&s&8&' # keep this a secret
socketio = SocketIO(app)

tokens = dict() # dict of tokens
users = dict() # dict of users' online status
notices = dict() # list of notifications to send

@app.route('/client')
def client():
	return render_template('client.html')

@app.route('/gettoken/<user>/<token>/<pkey>')
def gettoken(user, pkey, token = False):
	# user = User the token is for
	# pkey = The private key that is used to ensure we are
	# 		 talking to the correct server
	try:
		# Check if the variables are defined
		a = str(user)+str(token)+str(pkey)
		missing_vars = False
	except:
		missing_vars = True
		return "Error: Missing argument"
	a = ""
	
	if pkey != app.config['MUTUAL_SECRET']:
		# Impostor?
		return "Error: Access Denied" # Deny access
	else:
		if token == False or token == "nil":
			# If the server does not desire a specific token
			# i.e, `rkey` from DB.
			# TODO: Automatically fetch `rkey` as token
			token = str(uuid4()) # generate a random token
			tokens[token] = str(user)
			return token
		else:
			# If the server wants a specific token to be set
			tokens[str(token)] = str(user)
			return token

@app.route('/getuser/<token>')
def getuser(token):
	try:
		user = tokens[token]
		return str(user)
	except:
		return "Not Found"

@socketio.on('connect', namespace='/pychattr')
def handle_connect():
	print "Client Connected"
	join_room("notify") # join notify room
	emit('auth', "Please authenticate with your token.")
	send("User has joined socket", room = "notify")

@socketio.on('auth', namespace='/pychattr')
def handle_auth(message):
	# Authenticate a user
	tok = message
	try:
		# Will succeed is user token is valid
		user = tokens[tok]
		send("Welcome, {}. You are connected.".format(user))
		users[str(user)] = "Online"
		session["username"] = user # store it in a session
		send(session['username']+" has come online.", room = "notify")
		return
	except:
		# User token invalid
		send("Sorry, but we could not establish your identity. \
		    Try logging in again")
		emit('disconnect', "auth") # tell the client to disconnect
	

@socketio.on('pmuser', namespace='/pychattr')
def handle_pmuser(message):
	# person to PM
	try:
		user = session["username"]
		room = str(user)+"+"+str(message)
		join_room(room)
		# notify other client, through notify channel
		send("{'tojoin': '{}', 'joined': '{}'}".format(message, user), room = "notify") # send a push event
		
	except:
		pass
		
@socketio.on('quitpm', namespace='/pychattr')
def handle_quitpm(message):
	try:
		user = session["username"]
		room = str(user)+"+"+str(message)
		leave_room(room)
	except:
		pass
		
		
@socketio.on('disconnect', namespace='/pychattr')
def handle_disconnect():
	user = session["username"]
	users[str(user)] = "Offline"
	send(user+" has disconnected.", room = "notify")

@socketio.on('status', namespace='/pychattr')
def handle_statuschange(message):
	try:
		new_status = message
		user = session["username"]
		users[str(user)] = message
	except:
		pass
	
app.secret_key = os.urandom(24)

if __name__ == '__main__':
#	try:
#	socketio.run(app)
	socketio.run(app, port= 5000)
#	except e:
#		print e
