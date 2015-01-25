from flask import Flask, request, render_template, redirect, session
from functools import wraps
import db
import time

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

def searchBar(func): #doesnt work if function takes in an argument?
    @wraps(func)
    def inner():
        if request.method == 'POST':
            button = request.form['button']
            if button == 'Search':        
                print '/search/'+request.form['query']
                return redirect('/search/'+request.form['query'])
            else:
                return func()
        else:
            return func()
    return inner
            
@app.route('/', methods=['GET', 'POST'])
@searchBar
def home():
    if request.method == 'GET':
        return render_template('home.html')
    button = request.form['button']
    if button == 'Clubs':
        return redirect('/clubs')
    if button == 'Essays':
        return redirect('/essays')
    if button == 'Calendar':
        return redirect('/calendar')

@app.route('/search/<tag>', methods=['GET','POST'])
def search(tag):
    if request.method == 'GET':
        resultDict = db.search(tag)
        return render_template('search.html', resultDict = resultDict, tag=tag)
    else:
        button = request.form['button']
        if button == 'Search':        
            return redirect('/search/'+request.form['query'])
        
    
@app.route('/view_profile/<username>',methods=['GET','POST'])
def viewProfile(username):
    viewer=session['username']
    criteria= {"username":username}
    user=db.find_user(criteria)
    clubs=[] 
    clubList= db.list_clubs(username)
    for club in clubList:
        clubs.append(club[0])
        
    info=[username,user['first'],user['last'],user['schedule'],user['essays'],clubs]
    if request.method== 'GET':
        
        return render_template('profile.html',viewer=viewer,info=info,counter=False)   
    else:
        button = request.form['button']
        if button == 'Search':        
            return redirect('/search/'+request.form['query'])
        localtime = time.strftime("%B %d, %Y, %I:%M %p")
        
        userMessage= user['Message']
        
        message = request.form['User_Message']
        message = {"Message":message,"Sender":session['username'],"Time":localtime}
        
        if userMessage== None:
            userMessage=[]
        userMessage.append(message)
        db.update_user(criteria,{"Message":userMessage})
        
        
        return render_template('profile.html',info=info,viewer=viewer,counter=True)
        
                       
@app.route('/view_message',methods=['GET','POST'])
@searchBar
@authenticate
def viewMessage():
    if request.method=='GET':
        user= db.find_user({'username':session['username']})
        print user
        Message=user["Message"]
        return render_template('view_message.html',Message=Message)
    else:        
        button = request.form['button']
        if button == 'Search':        
            return redirect('/search/'+request.form['query'])

@app.route('/view_schedule', methods=['GET', 'POST'])
@searchBar  
@authenticate
def viewSchedule():
    if request.method == 'POST':
        button = request.form['button']
        if button == 'Change Schedule':
            return redirect('/edit_schedule')
        elif button == 'View Classmates':
            return redirect('/classmates')
    user = db.find_user({'username': session['username']})
    
    return render_template('view_schedule.html',user=user)


@app.route('/classmates')
@searchBar  
@authenticate
def classmates():
    user = db.find_user({'username': session['username']})
    periods = [1,2,3,4,5,6,7,8,9,10]
    classmates = {} #a dictionary with indices with the format... period:[classmates]
    for p in periods:
        course = user['schedule'][p-1]
        if course != 'N/A':
            l = getClassmates(p) #a list of classmates
            classmates[p] = l
    return render_template('classmates.html',user=user,classmates=classmates)


@app.route('/edit_schedule', methods=['GET', 'POST'])
@searchBar  
@authenticate
def editSchedule():
    user = db.find_user({'username': session['username']})
    if request.method == 'GET':
        return render_template('edit_schedule.html', staff=staff, user=user)
    else:
        button = request.form['button']
        if button == 'cancel':
            return redirect('/')
        else:
            user = db.find_user({'username': session['username']})
            sL=[]
            xd = 1
            
            while xd !=11:
              sL.append( request.form['teacher'+str(xd)])
              xd+= 1
            while xd !=21:
              sL.append(request.form['course'+str(xd-10)])
              xd+=1
            
            db.update_schedule(user,sL)
            return redirect('/view_schedule')

        
@app.route('/post_essay', methods=['GET', 'POST'])
@searchBar  
@authenticate
def post_essay():
    user = db.find_user({'username': session['username']})
    if request.method == 'GET':
        return render_template('post_essay.html')
    else:
        button = request.form['button']
        if button == 'Cancel':
            return redirect('/')
        elif button == 'Post':
            title = request.form['title']
            topic = request.form['topic']
            essay = request.form['essay']
            anon = request.form['anon']
            if not title or not essay:
                return render_template('post_essay.html',error='Please complete all required fields.')
            if not topic:
                topic = "None"
            newEssay={}
            newEssay['title'] = title
            newEssay['topic'] = topic
            newEssay['essay'] = essay
            if anon == "yes":
                newEssay['author'] = "Anonymous"
            else:
                newEssay['author'] = session['username']
            #adds essay id to essays list in user
            previous_essays = db.find_attribute({'username': session['username']}, "essays")
            essay_id = session['username'] + str(len(previous_essays))
            previous_essays.append(essay_id)
            change_user_info('essays', previous_essays)
            newEssay['essay_id'] = essay_id
            localtime = time.strftime("%B %d, %Y, %I:%M %p") 
            #Time in formate of Full month name, day, full year, hour:minute AM/PM  https://docs.python.org/3.0/library/time.html
            newEssay['time'] = localtime
            db.post_essay(session['username'], newEssay)
            return redirect('/essays')

@app.route('/essays', methods=['GET', 'POST'])
@searchBar
@authenticate
def essays():
    if request.method== 'GET':
        return render_template('essays.html')
    else:
        button=request.form['button']
        if button=='View All Essays':
            return redirect('/view_essays')
        if button == 'Your Essays':
            return redirect('/your_essays')
        if button == 'Post an Essay':
            return redirect('/post_essay')


@app.route('/your_essays', methods=['GET', 'POST'])
@searchBar  
@authenticate
def your_essays():
    if request.method== 'GET':
        essays = db.find_essays({'user':session['username']})
        return render_template('your_essays.html', essays=essays)
    else:
        button=request.form['button']
        if button == 'Post Your Own Essay':
            return redirect('/post_essay')


@app.route('/view_essays', methods=['GET', 'POST'])
@searchBar  
def view_essays():
    if request.method == 'GET':
        essayList= db.view_essays()
        return render_template('view_essays.html', essayList=essayList)
    else:
        button = request.form['button']
        if button == 'Post Your Own Essay':
            return redirect('/post_essay')

@app.route('/view_essay', methods=['GET', 'POST'])
@app.route('/view_essay/<tag>', methods=['GET', 'POST'])
def view_essay(tag='None'):
    if tag=='None':
        return redirect('/essays')
    essay_id = tag
    essay = db.find_essay({'essay_id':essay_id})
    if request.method == 'GET':
        if essay['user'] == session['username']: #if it's your essay
            return redirect('/view_your_essay/'+essay_id)
        else: #if it's someone else's essay
            return render_template('view_essay.html', essay=essay)
    else:
        button = request.form['button']
        if button == 'Comment On Essay':   
            return redirect('/comment_on_essay/'+essay_id)
        if button == 'Search':        
            return redirect('/search/'+request.form['query'])
    
@app.route('/view_your_essay', methods=['GET', 'POST'])
@app.route('/view_your_essay/<tag>', methods=['GET', 'POST'])
def view_your_essay(tag='None'):
    if tag=='None':
        return redirect('/essays')
    essay_id = tag
    essay = db.find_essay({'essay_id':essay_id})
    if request.method == 'GET':
        if essay['user'] == session['username']: #if it's your essay
            return render_template('view_your_essay.html', essay=essay)
        else: #if it's someone else's essay
            return redirect('/view_essay/'+essay_id)
    else:
        button = request.form['button']
        if button == 'Go Back To Your Essays':
            return redirect('/your_essays')
        elif button == 'Delete This Essay':
            db.delete_essay(essay_id)
            return redirect('/your_essays')
        elif button == 'Search':        
            return redirect('/search/'+request.form['query'])

@app.route('/comment_on_essay', methods=['GET', 'POST'])
@app.route('/comment_on_essay/<tag>', methods=['GET', 'POST'])
def comment_on_essay(tag='None'):
    if tag=='None':
        return redirect('/essays')
    essay_id = tag
    essay = db.find_essay({'essay_id':essay_id})
    if request.method == 'GET':
        if essay['user'] == session['username']: #if it's your essay
            return redirect('/view_your_essay/'+essay_id)
        else: #if it's someone else's essay
            return render_template('comment_on_essay.html', essay=essay)
    else:
        button = request.form['button']
        if button == 'Submit Comment':  
            paragraph_id = request.form['id']
            comment = request.form['comment']
            localtime = time.strftime("%B %d, %Y, %I:%M %p") 
            if comment:
                db.add_essay_comment(essay_id, paragraph_id, comment, session['username'], localtime)
                return redirect('/comment_on_essay/'+essay_id)
        elif button == 'Cancel':            
            return redirect('/comment_on_essay/'+essay_id)
        elif button == 'Search':        
            return redirect('/search/'+request.form['query'])

@app.route('/comment_on_essay.js')
def js():
    return render_template("comment_on_essay.js")


@app.route('/clubs',methods=['GET','POST'])
@searchBar
def clubs():
    if request.method== 'GET':
        return render_template('clubs.html')
    button=request.form['button']
    if button=='View Clubs':
        return redirect('/view_clubs')
    if button == 'Add a club/Create a club startup':
        return redirect('/add_clubs')
    if button == 'Edit Your Club':
        return redirect('/edit_club')

@app.route('/view_clubs', methods=['GET','POST'])
@searchBar
def view_club():
    clubList= db.view_clubs()
    return render_template('view_clubs.html',clubList=clubList)

@app.route('/add_clubs', methods=['GET', 'POST'])
@searchBar
@authenticate
def add_club():
    if request.method=='GET':
        return render_template('create_club.html')
    else:
        if not request.form['Club_Name']:
            return render_template('create_club.html',error="incomplete")
        if db.clubs.find_one({"clubname":request.form['Club_Name']}):
            return render_template('create_club.html',error='club taken')
        newClub={}
        newClub['clubname']=request.form['Club_Name']
        newClub['status']=request.form['Club_Status']
        newClub['description']=request.form['Club_Description']
        db.create_club(session['username'],newClub)
        return redirect('/clubs')

@app.route('/edit_club', methods=['GET', 'POST'])
@searchBar
@authenticate
def edit_clubs():
    clublist= db.list_clubs(session['username'])
    if request.method=='GET':
        
        return render_template('edit_club.html',clublist=clublist)
    if request.method=='POST':
        for club in clublist:
            status=request.form[str(club[0])+"Club_Status"]
            description=request.form[str(club[0])+"Club_Description"]
            db.update_club(club[0],status,description)
        return redirect('/view_clubs')


@app.route('/view_teachers', methods=['GET','POST'])
@searchBar
def view_teachers():
    teachers = db.find_teachers()
    return render_template('view_teachers.html', teachers=teachers)

@app.route('/view_teacher', methods=['GET', 'POST'])
@app.route('/view_teacher/<tag>', methods=['GET', 'POST'])
###############################################################
def view_teacher(tag='None'):
    if tag=='None':
        return redirect('/teachers')
    name = tag
    teacher = db.find_teacher({'name':name})
    if request.method == 'GET':
        return render_template('view_teacher.html', teacher=teacher)
    else:
        button = request.form['button']
        if button == 'View All Teachers':   
            return redirect('/view_teachers')

    
@app.route('/calendar', methods=['GET','POST'])
@searchBar
def calendar():
    return render_template('calendar.html')
    
@app.route('/login', methods=['GET', 'POST'])
@searchBar
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
@searchBar
def register():
    if request.method == 'GET':
        return render_template('register.html')
    button = request.form['button']
    username = request.form['username']
    password = request.form['password']
    first = request.form['first']
    last = request.form['last']
    if button == 'cancel':
        return redirect('/')
    else:
        if not password or not first or not last:
            return render_template('register.html',error='incomplete')
        criteria = {'username': username}
        if db.find_user(criteria):
            return render_template('register.html',error='username taken')
        else:
            initial_Schedule= ["N/A","N/A","N/A","N/A","N/A","N/A","N/A","N/A","N/A","N/A","","","","","","","","","",""]
            user_params = {'username': username, 'password': password, 'first': first, 'last': last, 'schedule':initial_Schedule, 'essays':[],'Message':[]}
            db.new_user(user_params)
            session['username'] = username
            return redirect('/')


@app.route('/display', methods=['GET', 'POST'])
@searchBar
@authenticate
def display():
    if request.method == 'POST':
        button = request.form['button']
        if button == 'Change Settings':
            return redirect('/change')
    user = db.find_user({'username': session['username']})
    return render_template('display.html', user=user)


@app.route('/logout', methods=['GET','POST'])
@searchBar
@authenticate
def logout():
    criteria = {'username': session['username']}
    #db.touch_user_logout_time(criteria)
    session.pop('username', None)
    return render_template('logout.html',logged_out=True)


@app.route('/change', methods=['GET', 'POST'])
@searchBar
@authenticate
def change_account():
    if request.method == 'GET':
        return render_template('change_account.html')

    if request.form['button'] == 'cancel':
        return redirect('/')

    criteria = {'username': session['username']}

    password = request.form['password']
    password2 = request.form['password2']
    first = request.form['first']
    last = request.form['last']
    changeset = {}
    if password:
        if password == password2:
            changeset['password'] = password            
            change_user_info('password',password)
        else:
            return render_template('change_account.html', error="Passwords must match.")
    if first:
        changeset['first'] = first
        change_user_info('first',first)
    if last:
        changeset['last'] = last
        change_user_info('last',last)
    return redirect('/display')

    #if valid_change(username, password)==True:
    #    db.update_user(criteria, changeset)
    #    if username:
    #        session['username'] = usernam
    #    return redirect('/display')
    #else:
    #    return render_template('change_account.html', error=valid_change(username, password))

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

def getClassmates(period):
    index = period - 1
    user = db.find_user({'username': session['username']})    
    course = user['schedule'][index]
    classmates = db.find_classmates({ 'schedule.' + str(index) : course },'username')
    return classmates

def change_user_info(key, value):
    criteria = {'username': session['username']}
    changeset = {}
    changeset[key] = value #a dictionary with the item you want to change
    db.update_user(criteria, changeset)
                    
if __name__ == '__main__':
    app.secret_key = 'Happy Halloween'
    app.debug = True
    app.run()
