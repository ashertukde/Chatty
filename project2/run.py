from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, send, join_room, leave_room, emit
from flask_session import Session
from profanity_filter import ProfanityFilter
import sys

app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'secretKey'
app.config['SESSION_TYPE'] = 'filesystem'

Session(app)
socketio = SocketIO(app, manage_session=False)

pf = ProfanityFilter()

# TODO
# Add profanity filter for username and room name
# Create members box to display current members in room
# Make sure no two members in the same room have the same name
# Have messages be distinguishable

@app.route('/index', methods=['GET','POST'])
@app.route('/login', methods=['GET','POST'])
@app.route('/', methods=['GET','POST'])
def index():
    return render_template('index.html')

@app.route('/chat', methods=['GET','POST'])
def chat():
    if(request.method=='POST'):
        username = request.form['username']
        room  = request.form['chatroom']
        # Store data in session to use 
        # when user is in chat room
        session['username'] = username
        session['room'] = room
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
    emit('status', {'msg': session.get('username') + ' has entered the room. Say hi!'}, room=room)

@socketio.on('text', namespace='/chat')
def text(message):
    room = session.get('room')
    print('Message: ' + message['msg'])
    # Check if message is appropriate
    if pf.is_clean(message['msg']):
        emit('message', {'msg': session.get('username') + ': ' + message['msg']}, room=room)
    else:
        emit('message', {'msg': 'Detected foul language. Please keep messages clean!'}, broadcast=False, include_self=True)

@socketio.on('left', namespace='/chat')
def left(message):
    room = session.get('room')
    username = session.get('username')
    leave_room(room)
    session.clear()
    emit('status', {'msg': username + ' has left the room.'}, room=room)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        socketio.run(app)
    else:
        socketio.run(app, host=sys.argv[1])