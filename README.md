pychattr
========

Realtime chat engine with hooks in multiple languages. ~~UI-less~~ Has an UI, written in Flask+Python.

####Requirements:

System Requirements:
 - Python 2.7.x
 - Python-Devel (`sudo yum install python-devel` or `sudo apt-get install python-dev`)
 - GCC (GNU C Compiler, `sudo yum install gcc` or `sudo apt-get install gcc`)

Python Package Requirements

 - Flask==0.10.1
 - Flask-KVSession==0.6.1
 - Flask-SocketIO==0.3.8
 - Jinja2==2.7.3
 - MarkupSafe==0.23
 - SQLAlchemy==0.9.7
 - Werkzeug==0.9.6
 - gevent==1.0.1
 - gevent-socketio==0.3.6
 - gevent-websocket==0.9.3
 - greenlet==0.4.3
 - itsdangerous==0.24
 - redis==2.10.3
 - simplekv==0.9.2
 - six==1.7.3
 - wsgiref==0.1.2

 
Other Requirements
 - SocketIO (js client) version 0.9.16
 - jQuery 1.x
 - StringJS
 - App to intergrate PyChattr with
 - pip (not required, but recommended)

####Installation:

#####Server

 - Clone the repo: `git clone https://github.com/Cydrobolt/pychattr.git`
 - `cd` to the app: `cd pychattr`
 - Create a VirtualEnv (highly recommended): `pip install virtualenv && virtualenv env && source env/bin/activate` 
 - Install requirements through `pip`: `pip install -r requirements.txt`
 - Edit `__init__.py` to change the app's `MUTUAL_SECRET`. This is the `pkey` required to generate tokens.
 - Run the PyChattr server: `cd app && python __init__.py`

#####Client

The client, by default, is served by the PyChattr server at `/client`.
However, PyChattr was designed for cross-platform, cross-server, cross-language
chat server purposes. For example, I am planning to use PyChattr as the chat server
for a PHP web application.

Simply copy the `/client` folder from the app root, and place it on the server that
hosts the client. Be warned, however, if the two servers are not on the same domain, 
you will have to use Flask-CORS to allow Cross-Origin Javascript Access.

--
That's it! PyChattr is still under heavy development, and it is very unstable.
If you find any bugs, please file an issue on GitHub. 

####Documentation:

#####Authentication Structure:

**Server-side Token Authentication**

Used for cross-server chat needs. For example, a PHP server based authentication system intergrating with PyChattr, a Python-Flask JSON chat server.

Web Server = S1

PyChattr Server = S2


Person Logs in to S1 -> S1 requests `/gettoken/<user>/nil/<pkey` (refer to `Server` for information on the `pkey`)
 -> S1 stores the returned token in a session variable -> After connecting to PyChattr
 through SocketIO, emit the `auth` event and pass the token as the message -> User is authenticated or denied. 

**Nick Authentication**

Less safety, as users can not be verified against existing authentication databases, however, it is useful if you wish to run a casual chat server for friends or visitors. 

`Potato`*: An IRC NickServ-like service that allows registration of nicks, preventing unauthorized use. Password authencation is used.

`Celery`*: An IRC ChanServ-like service that allows registration of channels, preventing unauthorized access to channels. Depends on Potato accounts.

* Both Potato and Celery require databases. PyChattr, by itself, is completely standalone, and usually depends on existing systems for authentication. However, if you decide to run PyChattr without any external server dependencies, you will have to install MongoDB in order to allow `Potato` and `Celery` to persist data.


##### Commands:

**Stable Commands**
 - `/join #channel` - Joins `#channel`.
 - `/part #channel` - Leaves `#channel`.
 - `/msg user` - Messages `user`.

**Experimental Commands**

`/kick user` - Kicks a user.
`/ban user` - Bans a user. (currently only for token auth, or Potato)
`/nick newnick` - Changes nickname to newnick.

**Services**

######Potato (Nickname Service)

 - `/potato register <nick> <password> <email>` - Registers a nickname
 - `/potato disconnect <nick> <password>` - Disconnect a user that is using your nickname
 - `/potato identify <nick> <password>` - Identify to a nickname through Potato

######Celery (Channel Service)

 - `/celery register #channel` - Registers a channel
 - `/celery op #channel user` - Op user on #channel.
 - `/celery deop #channel user` - Deop user on #channel.

#####Events:

Coming soon.
 
####Todo:

 - Channels - Currently underway
 - Nick change
 - Potato/Celery
 - Ban/kick
 - Oper/voice
 - Hostnames & IP fetching through SocketIO
 - Filter XSS
 - Server Services

####Known Bugs:

Please consult the "Issues" tab.
