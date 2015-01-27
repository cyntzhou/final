import datetime

from pymongo import MongoClient

client = MongoClient()
db = client['account_manager']
users = db['users']
clubs = db['clubs']
essays = db['essays']
teachers = db['teachers']

def new_user(user_params):
#    user_params['last_login_at'] = None
#    user_params['last_logout_at'] = None
    user_id = users.insert(user_params)
    return user_id

def find_user(criteria):
    user = users.find_one(criteria)
    return user

def find_things(criteria):
    things = users.find(criteria)
    return things

def find_classmates(criteria, attribute): #item is what you're searching for, e.g. username, password, etc.
    things = users.find(criteria)
    l = []
    for t in things:
        l.append(t[attribute])
    return l #doesn't return the users; returns a list of the attributes of each user

def find_attribute(criteria, attribute): #item is what you're searching for, e.g. username, password, etc.
    user = find_user(criteria)
    return user[attribute] #doesn't return the users; returns a list of the attributes of each user

#gotta use $set or else update would repace the entry
def update_user(criteria, changeset):
    db.users.update(criteria, {'$set':changeset}, upsert=False)

def update_schedule(user,changeset): #changeset is new schedule list with items 0-9 being teachers and 10-19 being the respective Course IDs
    old_schedule = user['schedule']
    for i in range(0,10):
        old_teacher_name = old_schedule[i].replace(".", "") #keys can't have periods
        period = str(i+1)
        if old_teacher_name != "N/A": #if the old schedule had a valid teacher
            old_teacher = teachers.find_one({'name':old_teacher_name})
            if old_teacher: #if old_teacher exists in teachers collection
                if old_teacher.has_key(period):
                    if user['username'] in old_teacher[period]:
                        old_teacher[period].remove(user["username"])
                        teachers.update({'name':old_teacher_name}, {"$set":{period:old_teacher[period]}})
        new_teacher_name = changeset[i].replace(".", "")
        if new_teacher_name != "N/A":
            new_teacher = teachers.find_one({'name':new_teacher_name})
            students = []
            if new_teacher:
                if new_teacher.has_key(period):
                    new_teacher[period].append(user["username"]) 
                else:
                    new_teacher[period] = [user["username"]]
                students = new_teacher[period]
            else:
                students = [user["username"]]
            teachers.update({'name':new_teacher_name}, {"$set":{period:students}}, upsert=True)
    db.users.update(user,{'$set':{"schedule":changeset}})

def create_club(user,user_params):
    user_params['admin']=user
    user_id=db.clubs.insert(user_params)
    return user_id

def update_club(clubname,status,description):
    clubs.update({'clubname':clubname},{"$set":{"status":status,"description":description}})
    
    return clubs
def view_clubs():
    clubList = []
    for club in clubs.find():
        clubList.append([club['clubname'],club['status'],club['description'],club['admin']])
    return clubList

def list_clubs(user):
    clubList=[]
    for club in clubs.find({"admin":user}):
        clubList.append([club['clubname'],club['status'],club['description']])
    return clubList

def post_essay(user,user_params):
    user_params['user'] = user
    user_id=db.essays.insert(user_params)
    return user_id

def view_essays():
    essayList = []
    for essay in essays.find():
        essayList.append([essay['title'],essay['topic'],essay['essay'],essay['author'],essay['essay_id'],essay['user'],essay['time']])
    return essayList

#used to find one essay using its unique essay_id
def find_essay(criteria):
    essay = essays.find_one(criteria)
    return essay
    
#used to find your essays using {'user': ____}
def find_essays(criteria):
    essayList = essays.find(criteria)
    return essayList

def update_essay(essay_id, title, topic, essay):
    essays.update({'essay_id':essay_id},{"$set":{"title":title,"topic":topic,"essay":essay}})

def delete_essay(essay_id):
    essay = essays.remove({'essay_id':essay_id})
    return essay
    
def add_essay_comment(essay_id, paragraph_id, comment, user, time):
    essay = essays.find_one({'essay_id':essay_id})
    l = [user, time, comment]
    if essay.has_key('comments'):
        comment_dict = essay['comments']
        if comment_dict.has_key(paragraph_id):
            comments = comment_dict[paragraph_id]
            comments.append(l)
        else:  
            comments = [l]
        comment_dict[paragraph_id] = comments
        essays.update({'essay_id':essay_id},{"$set":{"comments":comment_dict}})      
    else:
        essays.update({'essay_id':essay_id},
                      {"$set":
                       {"comments":
                        {paragraph_id:[l]}}})
            
#used to find one teacher using its unique name
def find_teacher(criteria):
    teacher = teachers.find_one(criteria)
    return teacher
    
#used to find one teacher using its unique name
def find_teachers():
    teacherList = teachers.find({})
    return teacherList
    
def search(query):
    queries = query.split(" ") #query.lower()?
    results = {'users':[], 'teachers':[], 'clubs':[], 'essays':[]}
    for q in queries:
        addToResultList({'username':q}, 'username', results, users, 'users')
        addToResultList({'first':q}, 'username', results, users, 'users')
        addToResultList({'last':q}, 'username', results, users, 'users')
        addToResultList({'name':q}, 'name', results, teachers, 'teachers')
        addToResultList({'clubname':q}, 'clubname', results, clubs, 'clubs')
        addToResultList({'title':q}, 'title', results, essays, 'essays')
        addToResultList({'topic':q}, 'title', results, essays, 'essays')
    return results

def addToResultList(queryDict, collection_key, results, collection, results_key):
    if collection.find(queryDict):
        for i in collection.find(queryDict):
            if i[collection_key] not in results[results_key]:
                results[results_key].append(i[collection_key])

