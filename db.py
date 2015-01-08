import datetime

from pymongo import MongoClient

client = MongoClient()
db = client['account_manager']
users = db['users']

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
        l.append(str(t[attribute]))
    return l #doesn't return the users; returns a list of the attributes of each user

#gotta use $set or else update would repace the entry
def update_user(criteria, changeset):
    
    db.users.update(criteria, {'$set':changeset}, upsert=False)

def update_schedule(user,changeset):
    db.users.update(user,{'$set':{"schedule":changeset}})
    
                  
                    
