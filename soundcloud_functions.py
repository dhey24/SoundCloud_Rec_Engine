# -*- coding: utf-8 -*-
"""
Created on Tue Apr  5 20:57:20 2016

@author: davidhey
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Mar 30 18:55:56 2016

@author: davidhey
"""

from soundcloud_secret import *
import soundcloud
import pprint

def authenticate():
    # create client object with app credentials
    client = soundcloud.Client(client_id=CLIENTID,
                               client_secret=SECRETID,
                               redirect_uri='http://example.com/callback')
    return client

# redirect user to authorize URL
#redirect client.authorize_url()

"""
Refresh tokens if necessary
"""
def refresh_token():
    # create client object with app credentials and refresh token
    client = Soundcloud.new(client_id='YOUR_CLIENT_ID',
                            client_secret='YOUR_CLIENT_SECRET',
                            refresh_token='SOME_REFRESH_TOKEN')
    
    # the client can now be used to make authenticated API calls
    print client.get('/me').username
    return client
    
# create a client object with your app credentials
def create_client(clientid):
    client = soundcloud.Client(client_id=clientid)
    return client
    
def create_dhey_client(clientid, secretid):
    client = soundcloud.Client(client_id = clientid, 
                               client_secret = secretid,
                               username = 'dhey24',
                               password = 'meatspin29')
    return client

#given a user id get their favorites
def get_favs(user_id):
    getstr = '/users/' + str(user_id) + '/favorites'
    favs = client.get(getstr, order = "created_at")
    
    return favs

#given a user id pull back all their track in order of most favorited
def get_tracks(user_id, clientid):
    client = create_client(clientid) 
    getstr = '/users/' + str(user_id) + '/tracks'
    tracks = client.get(getstr, order = 'favoritings_count')
    
    return tracks

#Authenticate general purpose
#client = create_client(CLIENTID)

#authenticate as me
client = create_dhey_client(CLIENTID, SECRETID)

def get_myfollows():
    #get my favorite artists and their tracks
    myfollows = client.get('/me/followings', limit = 100)
    
    return myfollows
        