import os
import sqlite3
import json
from functools import wraps
from base64 import b64encode, b64decode
from flask import Flask, request, session, g, redirect, url_for, abort, \
        render_template, flash, send_from_directory

app = Flask(__name__)
app.config.from_json('config.json')
if app.config.get('SECRET_KEY') is None:
    app.logger.info("Generate SECRET_KEY")
    with open('config.json', 'r') as f:
        j = json.load(f)

    j['SECRET_KEY'] = b64encode(os.urandom(64)).decode()
    
    with open('config.json','w') as f:
        json.dump(j, f)
    app.config.from_json('config.json')
app.config['SECRET_KEY'] = b64decode(app.config.get('SECRET_KEY'))
app.logger.debug(app.config)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
@login_required
def index():
    return 'It works!'

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
            app.logger.info(app.config['USERNAME'])
            app.logger.info(request.form['username'])
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in.')
            return redirect(url_for('show_videos'))
    return render_template('login.html', error=error)

@app.route('/logout')
@login_required
def logout():
    session.pop('logged_in', None)
    flash('You were logged out.')
    return redirect(url_for('show_videos'))

@app.route('/video')
@login_required
def show_videos():
    video_walk = os.walk(app.config.get('VIDEO_PATH'))
    video_list = []
    for dp, dn, fn in video_walk:
        for f in fn:
            video_list.append(f)
    return render_template('video.html', video_list=video_list)

@app.route('/video/<string:video_name>')
@login_required
def video(video_name):
    return send_from_directory(app.config.get('VIDEO_PATH'), video_name)


if __name__ == "__main__":
    app.run()
