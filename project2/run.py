from flask import Flask, render_template, request, redirect, url_for, session, flash

from flask_socketio import SocketIO, send, join_room, leave_room, emit
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import login_required

from profanity_filter import ProfanityFilter
import sys
import random
import sqlite3
import database

app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'secretKey'
app.config['SESSION_TYPE'] = 'filesystem'

connection = database.connect()
database.create_tables(connection)

bcrypt = Bcrypt(app)

Session(app)
socketio = SocketIO(app, manage_session=False)

memberlist = {'Yosemite': [], 'Sequoia':[], 'Redwood':[], 'Kings Canyon':[],'Mojave':[],'Joshua Tree':[]}
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
    if(request.method=='POST'):
        connection = database.connect()
        database.create_tables(connection)
        fName = request.form['fName']
        lName = request.form['lName']
        username = request.form['username']
        password = request.form['password']
        unique = database.add_user(connection, fName, lName, username, password)
        if unique:
            return render_template('index.html', unique=unique)
        else:
            notunique = True
            return render_template('index.html', notunique=notunique)
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    if(request.method=='POST'):
        connection = database.connect()
        username = request.form['username']
        password = request.form['password']
        verified = database.verify_user(connection, username, password)
        if verified:
            session['username'] = username

            return redirect(url_for('rooms'))
        else:
            notverified = True
            return render_template('index.html', notverified=notverified)
    return render_template('index.html')

@app.route('/logout', methods=['POST'])
def logout():
    return redirect(url_for('index'))

@app.route('/rooms', methods=['GET','POST'])
def rooms():
    if(request.method=='POST'):
        
        print(request.form)
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE uname=? ",(session['username'],))
        user_id = c.fetchone()
        if 'friend' in request.form:
            #print("friend")
            value,user_name = request.form['friend'].split(" ", 1) 
            
            if value == "accepted":
                c.execute("SELECT * FROM users WHERE uname=? ",(user_name,))
                temp_id = c.fetchone()
                c.execute("DELETE FROM friends_request WHERE user_id=? and requester_id=?",(int(user_id[0]),int(temp_id[0])))
                c.execute("SELECT * FROM friends WHERE user_id=? and friend_id=?",(int(user_id[0]),int(temp_id[0])))
                checker = c.fetchone()
                
                if(checker == None):
                    c.execute("INSERT INTO friends VALUES(?,?)",(int(user_id[0]),int(temp_id[0])))
                    conn.commit()
                    c.execute("INSERT INTO friends VALUES(?,?)",(int(temp_id[0]),int(user_id[0])))
                    conn.commit()

            else:
                c.execute("SELECT * FROM users WHERE uname=? ",(user_name,))
                temp_id = c.fetchone()
                c.execute("DELETE FROM friends_request WHERE user_id=? and requester_id=?",(int(user_id[0]),int(temp_id[0])))
                conn.commit()
            
           
                
        if 'deleting' in request.form:
            #print("deleting")
            c.execute("SELECT * FROM friends WHERE user_id=? ",(user_id[0],))
            temp_id = c.fetchone()
            #print(temp_id)
            value,user_name = request.form['deleting'].split(" ", 1)
            c.execute("SELECT * FROM users WHERE uname=? ",(user_name,))
            temp_id = c.fetchone() 
            c.execute("DELETE FROM friends WHERE user_id=? and friend_id=?",(int(user_id[0]),int(temp_id[0])))
            conn.commit()
            c.execute("DELETE FROM friends WHERE user_id=? and friend_id=?",(int(temp_id[0]),int(user_id[0])))
            conn.commit()
            c.execute("SELECT * FROM friends WHERE user_id=? ",(user_id[0],))
            temp_id = c.fetchone()
            #print(temp_id)
            
        if 'add' in request.form:
            c.execute("SELECT * FROM users WHERE uname=? ",(request.form['add'],))
            temp_id = c.fetchone()
            if temp_id != None:
                
                c.execute("SELECT * FROM friends_request WHERE user_id=? and requester_id=?",(int(temp_id[0]),int(user_id[0])))
                checker = c.fetchone()
                c.execute("SELECT * FROM friends_request WHERE user_id=? and requester_id=?",(int(user_id[0]),int(temp_id[0])))
                checker2 = c.fetchone()
                c.execute("SELECT * FROM friends WHERE user_id=? and friend_id=?",(int(user_id[0]),int(temp_id[0])))
                checker3 = c.fetchone()
                if(checker == None) and (checker2 == None) and (checker3 == None) and (user_id[0] != temp_id[0]):
                    #print("hi")
                    c.execute("INSERT INTO friends_request VALUES(?,?)",(int(temp_id[0]),int(user_id[0])))
                    conn.commit()
                c.execute("SELECT * FROM friends_request")
                temp = c.fetchall()
                #print(temp)
    return render_template('rooms.html') 

@app.route('/friendslist', methods=['GET' , 'POST'])
def friendslist():            
        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE uname=? ",(session['username'],))
        user_id = c.fetchone()           
        c.execute("SELECT * FROM friends_request WHERE user_id=?",(int(user_id[0]),))
        friends = c.fetchall()
        friends_array = []
        for friend in friends:            
            friends_array.append(friend[1])
        friends_request = []
        for ids in friends_array:
            c.execute("SELECT * FROM users WHERE id=?",(ids,))
            temp = c.fetchone()
            friends_request.append(temp[3])
        c.execute("SELECT * FROM friends WHERE user_id=?",(int(user_id[0]),))
        friends = c.fetchall()
        friends_array = []
        friends_accepted = []
        for friend in friends:            
            friends_array.append(friend[1])
        for ids in friends_array:
            c.execute("SELECT * FROM users WHERE id=?",(ids,))
            temp = c.fetchone()
            print(temp[3])
            friends_accepted.append(temp[3])
        conn.close()
        return render_template('friendslist.html', friends_request=friends_request, friends_accepted=friends_accepted)    

@app.route('/chat', methods=['GET','POST'])
def chat():
    if(request.method=='POST'):
        room  = request.form['room']
        # Store data in session to use 
        # when user is in chat room
        username = session.get('username')
        print(f"{username} {room}")
        session['room'] = room
        # Generate a random color user will get for chat distinguishing purposes
        rand = lambda: random.randint(0,255)
        session['color'] = "#%02X%02X%02X" % (rand(), rand(), rand())

        memberlist[room].append(username)
        
        return render_template('chat.html', session=session, title=room)
    else:
        if session.get('username') is not None:
            print(session.get('username'))
            return render_template('chat.html', session=session, title=room)
        else:
            return redirect(url_for('index'))

@app.errorhandler(503)
@app.errorhandler(500)
def error_500(error):
    return render_template('500.html')

# Namespace is the file we want to execute the function on
@socketio.on('join', namespace='/chat')
def join(message):
    room = session.get('room')
    join_room(room)
    #members list won't keep track of someone logging in without cookies
    if session.get('username'):
        #emit('status', {'msg': session.get('username') + ' has entered the room. Say hi!'}, room=room)
        emit('memberlist', {'msg': memberlist[room]}, room=room)
    else:
        flash('Server error. Please login again.', 'danger')
        return redirect(url_for('index'))    

@socketio.on('text', namespace='/chat')
def text(message):
    room = session.get('room')
    print('Message: ' + message['msg'])
    emit('message', {'color': session.get('color'), 'username': session.get('username'), 'msg': message['msg']}, room=room)


@socketio.on('left', namespace='/chat')
def left(message):
    room = session.get('room')
    username = session.get('username')
    memberlist[room].remove(username)

    leave_room(room)
    emit('status', {'msg': username + ' has left the room.'}, room=room)
    emit('memberlist', {'msg': memberlist[room]}, room=room)

@socketio.on('disconnect', namespace='/chat')
def test_disconnect():
    room = session.get('room')
    username = session.get('username')
    memberlist[room].remove(username)
    leave_room(room)
    emit('status', {'msg': username + ' has left the room.'}, room=room)
    emit('memberlist', {'msg': memberlist[room]}, room=room)
    
    
if __name__ == '__main__':
    #app.run()
    socketio.run(app, debug=False)