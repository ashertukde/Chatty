from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_socketio import SocketIO, send, join_room, leave_room, emit
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_required
from profanity_filter import ProfanityFilter
import sys
import random

app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'secretKey'
app.config['SESSION_TYPE'] = 'filesystem'

Session(app)
socketio = SocketIO(app, manage_session=False)
memberlist = {}
numOfMessages = {}
#pf = ProfanityFilter()
# TODO
# Add profanity filter for username and room name
# Create members box to display current members in room
# Make sure no two members in the same room have the same name
# Have messages be distinguishable

@app.route('/index', methods=['GET','POST'])
@app.route('/', methods=['GET','POST'])
def index():
    return render_template('index.html')

@app.route('/signup', methods=['POST'])
def signup():
    username = request.form['username']
    password = request.form['password']

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']


@app.route('/chat', methods=['GET','POST'])
@login_required
def chat():
    if(request.method=='POST'):
        room  = request.form['room']
        # Store data in session to use 
        # when user is in chat room
        session['username'] = username
        session['room'] = room
        # Generate a random color user will get for chat distinguishing purposes
        rand = lambda: random.randint(0,255)
        session['color'] = "#%02X%02X%02X" % (rand(), rand(), rand())
        
        if room in memberlist:
            if username in memberlist[room]:
                flash("Username has already been taken in this room. Please choose another!", 'danger')
                return redirect(url_for('index'))
            memberlist[room].append(username)
        else:
            memberlist[room] = [username]
        return render_template('chat.html', session=session, title=room)
    else:
        if session.get('username') is not None:
            print(session.get('username'))
            return render_template('chat.html', session=session, title=room)
        else:
            return redirect(url_for('index'))
    
# Namespace is the file we want to execute the function on
@socketio.on('join', namespace='/chat')
def join(message):
    room = session.get('room')
    join_room(room)
    #members list won't keep track of someone logging in without cookies
    if session.get('username'):
        emit('status', {'msg': session.get('username') + ' has entered the room. Say hi!'}, room=room)
        emit('memberlist', {'msg': memberlist[room]}, room=room)
    else:
        emit('status', {'msg': 'Guest has entered the room. Say hi!'}, room=room)
    

@socketio.on('text', namespace='/chat')
def text(message):
    room = session.get('room')
    print('Message: ' + message['msg'])
    # Check if message is appropriate
    # if pf.is_clean(message['msg']):
    #     if session.get('username'):
    #         emit('message', {'msg': session.get('username') + ': ' + message['msg']}, room=room)
    #     else:
    #         emit('message',{'msg': 'Guest: ' + message['msg']}, room=room)
    # else:
    #     emit('message', {'msg': 'Detected foul language. Please keep messages clean!'}, broadcast=False, include_self=True)
    emit('message', {'color': session.get('color'), 'username': session.get('username'), 'msg': message['msg']}, room=room)

    

@socketio.on('left', namespace='/chat')
def left(message):
    room = session.get('room')
    username = session.get('username')
    memberlist[room].remove(username)
    leave_room(room)
    session.clear()
    emit('status', {'msg': username + ' has left the room.'}, room=room)
    emit('memberlist', {'msg': memberlist[room]}, room=room)

@socketio.on('disconnect', namespace='/chat')
def test_disconnect():
    room = session.get('room')
    username = session.get('username')
    memberlist[room].remove(username)
    leave_room(room)
    session.clear()
    emit('status', {'msg': username + ' has left the room.'}, room=room)
    emit('memberlist', {'msg': memberlist[room]}, room=room)
    


if __name__ == '__main__':
    #app.run()
    socketio.run(app, debug=True)