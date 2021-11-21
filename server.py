from logging import error
from flask import Flask, render_template
from flask import redirect, url_for, request, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import os
import re

from werkzeug.utils import redirect

app = Flask(__name__, static_folder=os.path.abspath('templates/static'))

app.secret_key= 'root'

app.config['MYSQL_HOST'] ='153.92.220.151'
app.config['MYSQL_USER'] ='u413789411_seyfkutluk'
app.config['MYSQL_PASSWORD'] ='47.Antartika'
app.config['MYSQL_DB'] ='u413789411_blg'

mysql=MySQL(app)


@app.route("/home")
def home_page():
    return render_template("index.html")


@app.route('/login')
@app.route('/',methods=['GET','POST'])
def login_page():
    error=''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = % s AND password = % s',(username,password,))
        account = cursor.fetchone()

        if account:
            session['loggedin'] = True
            session['username'] = account['username']
            session['id'] = account['id']
            error = 'Logged in successfully !'
            return render_template('index.html',error = error)

        else:
            error = '!!!!Incorrect username or password!!!!!!!'
            
    return render_template('login.html',error =error)

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login_page'))

@app.route('/register', methods =['GET', 'POST'])
def register():
    message = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username=request.form['username']
        email = request.form['email']
        password=request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = % s', (username, ))
        account = cursor.fetchone()

        if account:
            message = 'Account already exists !'

        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            message = 'Invalid email address !'

        elif not re.match(r'[A-Za-z0-9]+', username):
            message = 'Username must contain only characters and numbers !'

        elif not username or not password or not email:
            message = 'Please fill out the form !'

        else:
            cursor.execute('INSERT INTO accounts VALUES (NULL, % s, % s, % s)', (username, password, email, ))
            mysql.connection.commit()
            message ='You have successfully registered'


    elif request.method == 'POST':
        message = 'Please fill out the form !'

    return render_template('register.html', message = message)


@app.route("/password")
def forgot_password():
    return render_template("password.html")


@app.errorhandler(404)
def not_found_page(e):
    return render_template("404.html"),404


@app.errorhandler(401)
def unauth_page(e):
    return render_template("401.html"),401


@app.errorhandler(500)
def internal_error_page(e):
    return render_template("500.html"),500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)