import os
import time
import sqlite3
import json
from functools import wraps
from base64 import b64encode, b64decode
from flask import Flask, request, session, g, redirect, url_for, abort, \
        render_template, flash, send_from_directory

app = Flask(__name__)

# Load config.json.
app.config.from_json('config.json')
# If SECRET_KEY not set, generate one and save.
if app.config.get('SECRET_KEY') is None \
        or app.config.get('SECRET_KEY') is "":
    app.logger.info("Generate SECRET_KEY")
    with open('config.json', 'r') as f:
        j = json.load(f)

    j['SECRET_KEY'] = b64encode(os.urandom(64)).decode()
    
    with open('config.json','w') as f:
        json.dump(j, f)
    app.config.from_json('config.json')
app.config['SECRET_KEY'] = b64decode(app.config.get('SECRET_KEY'))

# Set time zone to Asia/Shanghai.
os.environ['TZ'] = 'Asia/Shanghai'

app.logger.debug(app.config)


# Login check decorator.
def loginRequired(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

# Index
@app.route('/')
@loginRequired
def index():
    return render_template('index.html')


# Login function
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
            app.logger.debug(app.config['USERNAME'])
            app.logger.debug(request.form['username'])
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in.')
            return redirect(url_for('index'))
    return render_template('login.html', error=error)


# Logout function.
@app.route('/logout')
@loginRequired
def logout():
    session.pop('logged_in', None)
    flash('You were logged out.')
    return redirect(url_for('show_videos'))


# List video file under the VIDEO_PATH.
@app.route('/video')
@loginRequired
def show_videos():
    video_walk = os.walk(app.config.get('VIDEO_PATH'))
    video_list = []
    for dp, dn, fn in video_walk:
        for f in fn:
            video_list.append(f)
    video_list.sort()
    video_list.reverse()
    return render_template('show_videos.html', video_list=video_list)


# Play video online
@app.route('/video/play/<string:video_name>')
@loginRequired
def playVideo(video_name):
    return render_template('video.html', video_name=video_name)


# Download the specific video.
@app.route('/video/download/<string:video_name>')
@loginRequired
def downloadVideo(video_name):
    return send_from_directory(app.config.get('VIDEO_PATH'), video_name)


# Delete the specific video.
@app.route('/video/remove/<string:video_name>', methods=['GET'])
@loginRequired
def removeVideo(video_name):
    os.remove(app.config.get('VIDEO_PATH')+'/'+video_name)
    flash(video_name+' was removed.')
    return redirect(url_for('show_videos'))


# Remove videos older than the given days.
@app.route('/video/removeVideoByDays', methods=['GET'])
@loginRequired
def removeVideoByDays():
    deleted = 0
    if request.method == 'GET':
        if request.args.get('days'):
            days = int(request.args.get('days'))
            older = time.time() - (days*24*60*60)
            video_walk = os.walk(app.config.get('VIDEO_PATH'))
            for dp, dn, fn in video_walk:
                for f in fn:
                    if os.path.getctime(app.config.get('VIDEO_PATH')+'/'+f) < older:
                        os.remove(app.config.get('VIDEO_PATH')+'/'+f)
                        deleted += 1
            flash("You have remove "+str(deleted)+" videos which older than "+str(days)+" days.")
    return redirect(url_for('show_videos'))


if __name__ == "__main__":
    app.run(threaded=True)

