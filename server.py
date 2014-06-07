from flask import Flask, redirect, url_for, session, jsonify, request, g, abort, render_template, send_from_directory
import requests
import os
from torndb import Connection
import datetime
import time
import config
import urllib
import random 

app = Flask(__name__)

def random_str(randomlength=8):
    return ''.join(random.sample('AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789', 8))

@app.before_request
def connect_db():
    g.db = Connection(config.DB_HOST,
                      config.DB_NAME,
                      config.DB_USER,
                      config.DB_PASSWD)

@app.after_request
def close_connection(response):
    g.db.close()
    return response

@app.route('/')
def index():
    if 'userid' in session :
        res = g.db.query("SELECT rid, short, utime, etime, description, visited FROM res WHERE owner=%s ORDER BY rid DESC LIMIT 20", session['userid'])
    else :
        res = None
    return render_template('index.html', res=res, index=True)

@app.route('/u')
def update_session():
    if 'error' in requests.get('http://bbs.sysu.edu.cn/account/sssok',
                               params=dict(m=request.args.get('m'),
                                           u=request.args.get('u'),
                                           t=request.args.get('t'))) :
        return 'Error'
    session['userid'] = request.args.get('u')
    return redirect(url_for('index'))

@app.route('/r/<username>/<short>')
def show_files(username, short):
    ret = g.db.get("SELECT * FROM res WHERE owner=%s AND short=%s",
                 username, short)
    if not ret :
        abort(404)
    files = g.db.query("SELECT pid, savename, filename, utime, etime, fflag, download FROM file WHERE rid=%s ORDER BY pid DESC LIMIT 10",
                     ret['rid'])
    if session.get('lastrid', None) != ret['rid'] :
        g.db.execute("UPDATE res SET visited=visited+1 WHERE rid=%s",
                     ret['rid'])
        session['lastrid'] = ret['rid']
    thisurl = url_for('show_files', username=username, short=short,
                      _external=True)
    return render_template('files.html', ov=ret, fs=files, thisurl=thisurl)

@app.route('/f/<int:ed1>/<tf>')
def download_file(ed1, tf):
    savename = '%s/%s/%s/%s' % (config.UPLOAD_FOLDER,
                             ed1, tf[:2], tf)
    print savename
    if not os.path.exists(savename):
        abort(404)
    ret = g.db.get("SELECT rid, pid, filename FROM file WHERE savename=%s",
                   tf)
    print ret
    if not ret :
        abort(404)
    if not g.db.get("SELECT rid FROM res WHERE rid=%s", ret['rid']):
        abort(404)
    if session.get('lastpid', None) != ret['pid'] :
        g.db.execute('UPDATE file SET download=download+1 WHERE pid=%s',
                     ret['pid'])
        session['lastpid'] = ret['pid']        
    return send_from_directory('%s/%s/%s' % (config.UPLOAD_FOLDER, ed1,
                                             tf[:2]), tf,
                               as_attachment=True,
                               attachment_filename=ret['filename'])

@app.route('/ajax/query')
def ajax_query():
    if not 'userid' in session :
        return jsonify(error='No login user')
    if request.args.get('cursor') :
        res = g.db.query("SELECT rid, short, UNIX_TIMESTAMP(utime) as utime, UNIX_TIMESTAMP(etime) as etime, description, visited FROM res WHERE owner=%s AND rid<=%s ORDER BY rid DESC LIMIT 20", session['userid'], request.args.get('cursor'))
    else :
        res = g.db.query("SELECT rid, short, UNIX_TIMESTAMP(utime) as utime, UNIX_TIMESTAMP(etime) as etime, description, visited FROM res WHERE owner=%s ORDER BY rid DESC LIMIT 20", session['userid'])
    return jsonify(ok=True, res=res)

@app.route('/ajax/upload', methods=['POST'])
def ajax_upload():
    if not 'userid' in session :
        return jsonify(error='No login user')
    short = request.form['short'].replace('..', '_').replace('/', '_').replace(':', '_')
    rid=g.db.get('SELECT rid FROM res WHERE owner=%s AND short=%s LIMIT 1',
                 session['userid'], short)
    if rid :
        return jsonify(error='This short has been used', code=1)
    nw = datetime.datetime.now()
    expd = int(request.form['expi'])
    if expd > config.MAX_EXPIDAY :
        expd = config.MAX_EXPIDAY
    if expd < 1 :
        expd = 1
    expitime = datetime.datetime(nw.year,
                                 nw.month,
                                 nw.day + expd)
    tf = random_str()
    savedir = '%s/%s/%s/' % (config.UPLOAD_FOLDER,
                             expitime.day, tf[:2])
    if not os.path.exists(savedir):
        os.makedirs(savedir)    
    savename = '%s/%s/%s' % (expitime.day, tf[:2], tf)
    f = request.files['file']
    f.save('%s/%s' % (config.UPLOAD_FOLDER, savename))
    rid=g.db.execute("INSERT INTO res (owner, short, utime, etime, lastfilename, description) VALUES (%s, %s, %s, %s, %s, %s)",
                     session['userid'],
                     short,
                     nw, expitime,
                     f.filename,
                     request.form.get('description', f.filename))
    print 'tf> '+tf
    g.db.execute("INSERT INTO file (rid, filename, savename, utime, etime) VALUES (%s, %s, %s, %s, %s)", rid, f.filename, tf, nw, expitime)
    return jsonify(ok=True, rid=rid, savename=savename,
                   location=url_for('show_files', username=session['userid'],
                                    short=short, _anchor="main"))

@app.route('/ajax/update', methods=['POST'])
def ajax_update():
    if not 'userid' in session:
        return jsonify(error='No login user')
    short = request.form['short'].replace('..', '_').replace('/', '_')
    nw = datetime.datetime.now()
    expd = 7
    if expd > config.MAX_EXPIDAY :
        expd = config.MAX_EXPIDAY
    if expd < 1 :
        expd = 1
    expitime = datetime.datetime(nw.year,
                                 nw.month,
                                 nw.day + expd)
    tf = random_str()
    savename = '%s/%s/%s' % (expitime.day, tf[:2], tf)
    savedir = '%s/%s/%s' % (config.UPLOAD_FOLDER, expitime.day, tf[:2])
    if not os.path.exists(savedir) :
        os.makedirs(savedir)
    f = request.files['file']
    f.save('%s/%s' % (config.UPLOAD_FOLDER, savename))
    rid=g.db.get("SELECT rid FROM res WHERE short=%s AND owner=%s",
               short, session['userid'])
    if not rid :
        return jsonify(error="No exists res")
    rid = rid['rid']
    g.db.execute("INSERT INTO file (rid, filename, savename, utime, etime) VALUES(%s, %s, %s, %s, %s)", rid, f.filename, tf, nw, expitime)
    g.db.execute("UPDATE res SET etime=%s, lastfilename=%s WHERE rid=%s", expitime, f.filename, rid)
    return jsonify(ok=True, rid=rid, savename=savename)
        
@app.route('/ajax/del', methods=['POST'])
def ajax_del():
    if not 'userid' in session :
        return jsonify(error='No login user')
    ret = g.db.get("SELECT rid FROM res WHERE owner=%s AND short=%s",
                   session['userid'], request.form['short'])
    if not ret :
        return jsonify(error='No such res')
    g.db.execute("DELETE FROM res WHERE rid=%s", ret['rid'])
    return jsonify(ok=True, location=url_for('index'))

@app.route('/logout', methods=["GET", "POST"])
def logout():
    session.pop('userid', None)
    if request.method == 'POST' :
        return jsonify(success=True)
    else :
        return redirect(request.referrer or url_for('index'))

app.secret_key = config.SESSION_KEY

if __name__ == "__main__":
    app.run(debug=True)

