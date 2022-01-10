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


@app.route("/home",methods=['GET','POST'])
def home_page():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM COUNTRY ORDER BY countryID ASC')
    countries = cursor.fetchall()
    return render_template("index.html",countries = countries)



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
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM COUNTRY ORDER BY countryID ASC')
        countries = cursor.fetchall()
        if account:
            session['loggedin'] = True
            session['username'] = account['username']
            session['id'] = account['id']
            session['admin'] = 0
            error = 'Logged in successfully !'
            if account['is_admin']:
                session['admin'] = 1
                return render_template('index.html',error = error,countries = countries)
            else:
                return render_template('index.html',error = error, countries = countries)

        else:
            error = '!!!!Incorrect username or password!!!!!!!'
            
    return render_template('login.html',error =error)

@app.route("/admin",methods=['GET','POST'])
def admin_page ():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM accounts WHERE username = % s AND is_admin = 1',(session['username'],))
    acc = cursor.fetchone()
    cursor.execute('select * from COUNTRY order by countryID asc')
    countries = cursor.fetchall()
    if acc:
        return render_template("admin.html",countries = countries)
    else:
        return render_template("401.html"),401

@app.route('/new_country')
def new_country():
    if session['admin'] == 1:
        return render_template('new_country.html',error = error)
    else:
        return render_template("401.html"),401

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    session.pop('admin', None)
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

@app.route("/country/<int:id>")
def country_info(id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM COUNTRY where countryID=%s',(id,))
    country = cursor.fetchone()
    cursor.execute('SELECT * FROM COUNTRY ORDER BY countryID ASC')
    countries = cursor.fetchall()
    return render_template("country.html",country = country, countries = countries)

@app.route("/stats/<int:id>",methods=['GET','POST'])
def stats_info(id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM COUNTRY order by countryId asc')
    countries = cursor.fetchall()
    cursor.execute('SELECT * FROM YEAR_QUARTER where countryID=%s order by year_quarter',(id,))
    country = cursor.fetchall()
    cursor.execute('SELECT * FROM LABOUR_STATUS where countryID=%s order by year_quarter',(id,))
    labour_stat = cursor.fetchall()
    cursor.execute('SELECT * FROM EDUCATION_LEVEL_EMPLOYED where countryID=%s order by year_quarter,level_number',(id,))
    educated_employed = cursor.fetchall()
    cursor.execute('SELECT * FROM PROFESSION_STATUS where countryID=%s order by year_quarter,type',(id,))
    profession = cursor.fetchall()
    cursor.execute('SELECT * FROM PROFESSION_TYPE')
    profession_type = cursor.fetchall()
    cursor.execute('SELECT * FROM EMPLOYMENT_PART_FULL where countryID=%s order by year_quarter,work_type',(id,))
    employment = cursor.fetchall()
    cursor.execute('SELECT * FROM EMPLOYMENT_TYPE')
    employment_type = cursor.fetchall()
    cursor.execute('SELECT * FROM NACE_EMPLOYMENT where countryID=%s order by year_quarter,job_area',(id,))
    nace_emp = cursor.fetchall()
    cursor.execute('SELECT * FROM NACE_JOBS')
    nace_title = cursor.fetchall()
    cursor.execute('SELECT * FROM EDUCATION_TRAINING where countryID=%s order by year_quarter',(id,))
    edu_tra = cursor.fetchall()
    return render_template("stats.html",countries = countries, country = country, labour_stat = labour_stat, educated_employed =educated_employed,profession=profession,profession_type=profession_type,employment_type=employment_type,employment=employment,nace_emp=nace_emp,nace_title=nace_title,edu_tra=edu_tra)

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