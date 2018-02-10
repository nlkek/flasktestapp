import sqlite3
import os
from flask import Flask, request, g, redirect, url_for, \
     render_template, flash, jsonify

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'test.db'),
    DEBUG=True,
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default',
))


def connect_db():
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/users_list')
def users_list():
    temp = ['user_name', 'uid', 'password']
    db = get_db()
    cur = db.execute('select user_name, id, password from users')
    users = cur.fetchall()
    d1 = [dict(zip(temp, record)) for record in users]
    return jsonify(d1)


@app.route('/create_user', methods=['GET', 'POST'])
def create_user():
    if request.method == 'POST':
        db = get_db()
        db.execute('insert into users (user_name, password) values (?, ?)', [request.form['name'], request.form['password']])
        db.commit()
        cur = db.execute('SELECT last_insert_rowid()')
        flash('User\'s uid: %s' % str(cur.fetchone()['last_insert_rowid()']))
        return redirect(url_for('create_user'))
    if request.args.get('name') and request.args.get('password'):
        db = get_db()
        db.execute('insert into users (user_name, password) values (:name, :password)', request.args)
        db.commit()
        cur = db.execute('SELECT last_insert_rowid()')
        return 'New user was added, id: %s' % str(cur.fetchone()['last_insert_rowid()'])
    return render_template('create_user.html')


@app.route('/delete_user', methods=['GET', 'POST'])
def delete_user():
    if request.method == 'POST':
        db = get_db()
        try:
            cur = db.execute('select user_name from users where id = ?', [request.form['id']])
            db.execute('delete from users where id = ?', [request.form['id']])
            db.commit()
            flash('User was deleted, name: %s' % str(cur.fetchone()['user_name']))
        except:
            return 'No users with this id. Try another.'
        return redirect(url_for('delete_user'))
    if request.args.get('uid'):
        db = get_db()
        try:
            cur = db.execute('select user_name from users where id =:uid', request.args)
            db.execute('delete from users where id =:uid', request.args)
            db.commit()
            return 'User was deleted, name: %s' % str(cur.fetchone()['user_name'])
        except:
            return 'No users with this id. Try another.'
    return render_template('delete_user.html')


if __name__ == '__main__':
    os.chdir(app.root_path)
    if not os.path.exists('test.db'):
        init_db()
    app.run()
