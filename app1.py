from flask import Flask, request, render_template, redirect, session
from functools import wraps
import db

app = Flask(__name__)

staff = open("./templates/staff.txt",'r').read().splitlines()
#a list of all teachers

def authenticate(func):
    @wraps(func)
    def inner():
        if 'username' in session:
            return func()
        else:
            return redirect('/login')
    return inner

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/view_schedule')
@authenticate
def viewSchedule():
    return render_template('view_schedule.html')

@app.route('/edit_schedule', methods=['GET', 'POST'])
@authenticate
def editSchedule():
    if request.method == 'GET':
        return render_template('edit_schedule.html', staff=staff)
    else:
        button = request.form['button']
        if button == 'cancel':
            return redirect('/')
        else:
            #change user stuff in database...
            return redirect('/view_schedule')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    button = request.form['button']
    username = request.form['username']
    password = request.form['password']
    valid_user = valid(username, password)
    if button == 'cancel' or not(valid_user):
        return redirect('/')
    else:
        criteria = {'username': username, 'password': password}
        user = db.find_user(criteria)
        if user:
            session['username'] = username
            #db.touch_user_login_time(criteria)
            return redirect('/')
        else:
            return render_template('login.html',error=True)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    button = request.form['button']
    username = request.form['username']
    password = request.form['password']
    if button == 'cancel':
        return redirect('/')
    else:
        criteria = {'username': username}
        if db.find_user(criteria):
            return render_template('register.html',error=True)
        else:
            user_params = {'username': username, 'password': password}
            db.new_user(user_params)
            session['username'] = username
            return redirect('/')


@app.route('/display')
@authenticate
def display():
    user = db.find_user({'username': session['username']})
    return render_template('display.html', user=user)


@app.route('/logout')
@authenticate
def logout():
    criteria = {'username': session['username']}
    #db.touch_user_logout_time(criteria)
    session.pop('username', None)
    return render_template('logout.html',logged_out=True)


@app.route('/change', methods=['GET', 'POST'])
@authenticate
def change_account():
    if request.method == 'GET':
        return render_template('change_account.html')

    if request.form['button'] == 'cancel':
        return redirect('/')

    criteria = {'username': session['username']}

    username = request.form['username']
    password = request.form['password']
    changeset = {}
    if username:
        changeset['username'] = username
    if password:
        changeset['password'] = password

    if valid_change(username, password)==True:
        db.update_user(criteria, changeset)
        if username:
            session['username'] = username
        return redirect('/display')
    else:
        return render_template('change_account.html', error=valid_change(username, password))

#returns True or an error that can be displayed on the webpage
def valid_change(username, password):
    if username == session['username']:
        #lets the user change his password
        if password == db.find_user({'username':username})['password']:
            return "Your information has not been changed."
    elif db.find_user({'username':username}):
        return "That username has already been taken."
    return True

#is this function needed?
def valid(username, password):
    return True


if __name__ == '__main__':
    app.secret_key = 'Happy Halloween'
    app.debug = True
    app.run()
