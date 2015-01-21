import datetime

from pymongo import MongoClient

client = MongoClient()
db = client['account_manager']
users = db['users']
clubs= db['clubs']
essays= db['essays']

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
    print things
    l = []
    for t in things:
        l.append(t[attribute])
    return l #doesn't return the users; returns a list of the attributes of each user

def find_attribute(criteria, attribute): #item is what you're searching for, e.g. username, password, etc.
    user = find_user(criteria)
    print user[attribute]
    return user[attribute] #doesn't return the users; returns a list of the attributes of each user

#gotta use $set or else update would repace the entry
def update_user(criteria, changeset):
    
    db.users.update(criteria, {'$set':changeset}, upsert=False)

def update_schedule(user,changeset):
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
    
