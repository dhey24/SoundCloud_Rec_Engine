# -*- coding: utf-8 -*-
"""
Created on Sat Apr  9 18:21:37 2016

@author: davidhey
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Apr  7 19:32:45 2016

@author: davidhey
"""


from soundcloud_secret import *
from soundcloud_functions import create_client
import soundcloud
from soundcould_search_uesr import *
    
def follows_follows(userid, follow_type):
    """
    A userid create their 2nd degree network
    follow type must be "followings" or "followers"
    Followings will provide reccomendations of who a user should follow but doesnt... intended for those consuming music
    Followers will provide similar artists to a given user id... intended for those producing music
    
    Always looks at the followings of the follow type provided to get the 2nd degree network
    """
    #Authenticate general purpose
    client = create_client(CLIENTID)
    
    #get my info
    me = client.get('/users/' + str(userid))
    processed = 0
    followcount = 0
    maxfollows = 0
    secondDegree = {}
    myFollowsList = []
    
    edgeList = []
    nodeRef = {}
    
    followings = me.followings_count
    page_size = 100
    #process the first linked partition
    
    nxt = True
    try:
        myfollows = client.get('/users/' + str(userid) + '/' + follow_type, limit = page_size)
    except:
        print "504 Error...skipping"
        nxt = False
    while nxt: 
        for myfollow in myfollows.collection:
            myFollowsList.append(myfollow.id)
        #print myfollow.username
        #print myfollows.next_href
        if myfollows.next_href == None:
            nxt = False
        else:
            try:
                myfollows = client.get(myfollows.next_href)
            except:
                print "504 Error...skipping"
                nxt = False
    
    print len(myFollowsList), "<--Total follows"
    
    #loop through all followings and get their followings
    nxt = True
    try:
        myfollows = client.get('/users/' + str(userid) + '/' + follow_type, limit = page_size)
    except:
        print "504 Error...skipping"
        nxt = False
    while nxt:
        for myfollow in myfollows.collection:
            if myfollow.id not in nodeRef.keys():
                attr = {}
                attr["followers"] = myfollow.followers_count
                attr["username"] = myfollow.username
                attr["city"] = myfollow.city
                attr["track_count"] = myfollow.track_count
                attr["first_degree_follow"] = True
                attr["permalink_url"] = myfollow.permalink_url
                nodeRef[myfollow.id] = attr
                
            followings = myfollow.followings_count
            getstr = '/users/' + str(myfollow.id) + '/followings'
            
            nxt2 = True
            try:
                myfollows2 = client.get(getstr, filter = "all", limit = page_size)
            except:
                print "504 Error...skipping"
                nxt2 = False
            while nxt2:
                for myfollow2 in myfollows2.collection:
                    #print myfollow.username, myfollow2.username    #for debug
                    #add to the edgeList
                    edgeList.append((myfollow.id, myfollow2.id))
                    #add to nodeRef if it doesnt exist
                    if myfollow2.id not in nodeRef.keys():
                        attr = {}                   
                        attr["followers"] = myfollow2.followers_count
                        attr["username"] = myfollow2.username
                        attr["city"] = myfollow2.city
                        attr["track_count"] = myfollow2.track_count
                        attr["permalink_url"] = myfollow2.permalink_url
                        if myfollow2.id not in myFollowsList:
                            attr["first_degree_follow"] = False
                        else:
                            attr["first_degree_follow"] = True
                        nodeRef[myfollow2.id] = attr
                    processed += 1
                if myfollows2.next_href == None:
                    nxt2 = False
                else:
                    try:
                        myfollows2 = client.get(myfollows2.next_href)
                    except:
                        print "504 Error...skipping"
                        nxt2 = False
            followcount += 1
            print len(edgeList), "second degree follows"
            print followcount, "out of", len(myFollowsList), "complete...", processed, "processed" #for debugging
        if myfollows.next_href == None:
            nxt = False
        else:
            try:        
                myfollows = client.get(myfollows.next_href)
            except:
                print "504 Error...skipping"
                nxt = False
    return (edgeList, nodeRef)

def follows(userid):
    #Authenticate general purpose
    client = create_client(CLIENTID)
    
    #get my info
    me = client.get('/users/' + str(userid))
    myfollows = client.get('/users/' + str(userid) + '/followings', limit = 200)
    
    return myfollows
