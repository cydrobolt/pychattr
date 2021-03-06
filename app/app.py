from flask import Flask, render_template, session, request
from flask.ext.socketio import SocketIO, join_room, leave_room, emit, send, disconnect
from uuid import uuid4
import os, redis
import json as jsondecode
from flask_kvsession import KVSessionExtension
from simplekv.memory.redisstore import RedisStore
import config

store = RedisStore(redis.StrictRedis())
'''
# PyChattr Server
# [c] Copyright 2014 Chaoyi Zha
# Authors: Chaoyi Zha <summermontreal@gmail.com>
# Licensed under GPLv2, or later. Read LICENSE for more info.
'''

# --------- Config --------- #

use_tokens = config.use_tokens
host = config.web['host']
port = config.web['port']
secret_key_cookie = config.cookie_key
mutual_secret_token = config.token_key

# --------- /Config --------- #



app = Flask(__name__)

KVSessionExtension(store, app)

app.config['SECRET_KEY'] = secret_key_cookie
app.config['MUTUAL_SECRET'] = mutual_secret_token
socketio = SocketIO(app)

tokens = dict() # dict of tokens
users = dict() # dict of users' online status
notices = dict() # list of notifications to send
rtokens = dict()
invited = dict()
chanulist = dict()

def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""

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
			rtokens[str(user)] = token
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
	if use_tokens == True:
		emit('auth', "Please authenticate with your token.")
	else:
		emit('auth', "Please choose a nickname. ")
	send("User has joined socket", room = "notify")

@socketio.on('auth', namespace='/pychattr')
def handle_auth(message):
	# Authenticate a user
	tok = message
	try:
		something = session["username"] # is authed already?
		emit("error", "Already authenticated as "+something)
		return
	except:
		pass
	if use_tokens == True:
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
			emit('skick', "Invalid Token") # tell the client to disconnect
			disconnect()
	else:
		tok = str(tok).translate(None, "!@#$%&*()/\<>~+;'") # filter symbols
		# no token nonsense
		try:
			if users[str(tok)] != "Offline":
				# If online, deny
				emit('skick', "Username in use.")
				disconnect();
				return
			else:
				# Offline, allow use
				token = str(uuid4()) # generate a random token
				tokens[token] = str(tok)
				rtokens[str(tok)] = token
				users[str(tok)] = "Online"
				session["username"] = tok
				send("You are now known as "+tok)
				return

		except:
			token = str(uuid4()) # generate a random token
			tokens[token] = str(tok)
			rtokens[str(tok)] = token
			users[str(tok)] = "Online"
			session["username"] = tok
			send("You are now known as "+tok)
			return



@socketio.on('sendmsg', namespace='/pychattr')
def handle_json(json):
	json = jsondecode.loads(json)
	channel = json['room']
	text = str(json['text'])

	if text[0] == "/":
		handle_command(text)
		return # it's a command!


	text = text.translate(None, '}{<>') #antiXSS
	text = text.replace("'", "\'")
	text = text.replace('"', '\"')
	user = session["username"]
	tjson = '{"room": "'+channel+'", "text": "'+text+'", "from": "'+user+'"}'
	send(tjson, room=channel) # send it :)

@socketio.on('pmuser', namespace='/pychattr')
def handle_pmuser(message):
	# person to PM
	try:
		user = session["username"]
		try:
			status = users[str(message)]
			if status == "Online":
				pass
			else:
				emit('error', "User specified is not online.")
				return
		except:
			emit('error', "User specified not found.")
			return

		room = "PM:"+str(user)+"+"+str(message)
		invited[room] = [message] # message = user being PMed
		# ^ Invite them to the room, so that they can join
		join_room(room)
		# notify other client, through notify channel
		send('{"tojoin": "'+message+'", "joined": "'+user+'"}', room = "notify") # send a push event

	except:
		emit('error', "You are not logged in!")




@socketio.on('disconnect', namespace='/pychattr')
def handle_disconnect():
	user = session["username"]
	users[str(user)] = "Offline"
	send(user+" has disconnected.", room = "notify")

@socketio.on('jroom', namespace='/pychattr')
def handle_jroom(message):
	tjroom = str(message)
	channel = tjroom
	user = session["username"]
	if tjroom.startswith("#") and "+" not in tjroom:
		# if channel
		emit('joinroom', tjroom) # emit a message to make them join
		# tell the room
		text = user+" has joined "+tjroom
		tjson = '{"room": "'+tjroom+'", "text": "'+text+'", "from": "'+"<strong style='color:red'>System</strong>"+'"}'
		send(tjson, room=channel) # send it :)

		join_room(tjroom)
	elif user in invited[tjroom]:
		# was invited, i.e, PM or otherwise
		join_room(tjroom)

@socketio.on('qroom', namespace='/pychattr')
def handle_qroom(message):
	tqroom = str(message)
	try:
		user = session['username']
	except:
		emit('error', "You are not authenticated.")
		return
	if tqroom != "notify":
		# don't allow quitting of notify room
		try:
			leave_room(tqroom)
			return
		except:
			emit('error', "You are not in that room")
			return
	else:
		emit('error', "You cannot leave the global notification channel.")
		return

@socketio.on('command', namespace='/pychattr')
def handle_command(message):
	command = str(message)
	if "/" not in command:
		emit('error', "Invalid command syntax. Please include slash")
		return
	actual_command = find_between(command, "/", " ")
	command = command.translate(None, '/{}"\'')
	argscount = command.count(' ')
	args = []
	cmdlen = int(len(actual_command)+1)
	command = " "+command[cmdlen:]+" "
	for i in xrange(0,argscount):

		arg = find_between(command, " ", " ")
		args.append(arg)
		arglen = len(arg)+1
		command = command[arglen:]

	if actual_command == "join":
		if argscount == 2:
			key = args[1]
			channel = args[0]
		else:
			channel = args[0]
		handle_jroom(channel)
	elif actual_command == "ban":
		pass
	elif actual_command == "kick":
		pass
	elif actual_command == "part" or actual_command == "leave":
		handle_qroom(args[0])
	elif actual_command == "msg" or actual_command == "pm":
		handle_pmuser(args[0])
	else:
		emit('error', "Invalid command given")
@socketio.on('status', namespace='/pychattr')
def handle_statuschange(message):
	try:
		new_status = message
		user = session["username"]
		users[str(user)] = message
	except:
		emit('error', "User not found?")

app.secret_key = os.urandom(24)

if __name__ == '__main__':
    print "PyChattr server listening at "+host+":"+str(port)
    socketio.run(app, port = port, host = host)
