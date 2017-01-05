# -*- coding: utf-8 -*-
"""
Created on Sun Apr 10 12:39:48 2016

@author: davidhey
"""
from soundcould_search_user import *
from soundcloud_secret import *
from soundcloud_functions import create_client
import networkx as nx
import pprint
import matplotlib.pyplot as plt
import soundcloud
    
def follows_follows(userid, follow_type):
    """
    A userid create their 2nd degree network
    follow type must be "followings" or "followers"
    Followings will provide reccomendations of who a user should follow but 
    doesnt... intended for those consuming music
    Followers will provide similar artists to a given user id... intended for 
    those producing music
    
    Always looks at the followings of the follow type provided to get the 2nd 
    degree network
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
        myfollows = client.get('/users/' + str(userid) + '/' + follow_type, 
                               limit = page_size)
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
        myfollows = client.get('/users/' + str(userid) + '/' + follow_type, 
                               limit = page_size)
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
                myfollows2 = client.get(getstr, filter = "all", 
                                        limit = page_size)
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
            print followcount, "out of", len(myFollowsList), "complete...", 
                  processed, "processed" #for debugging
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


def reccomendationNetwork(user_id, repull_data):
    """
    Create 2nd degree network of who is following who for a given user
    Will create a png of the network

    user_id = user id to get recommendations for (string)
    repull_data = 1 to reputt the follower data, 0 if it already has been done 
    (saves time)
    """
    #repull data?
    repull = repull_data
    if repull == 1:
        #find a user by username
        new_user = searchUser("https://soundcloud.com/" + str(user_id), True)
        #create their second degree dict
        outtuple = follows_follows(new_user.id, "followings")
        newEdgeList = outtuple[0]
        newNodeRef = outtuple[1]
    maxfollows = 0
    maxDegree = 0
    df1_follows= []
    nodeList = []
    edgeList = []
    nodeLabels = {}
    nodeSize = []
    countLimit = 10
    G = nx.Graph()

    for key, val in newNodeRef.iteritems():
        nodeList.append(key)
        val["recEdges"] = 0
        G.add_node(key, attr_dict = val)
        nodeSize.append(val["followers"])
        nodeLabels[key] = val["username"] 
        if val["first_degree_follow"] == True:
            df1_follows.append(key) 
            
            
    for e in newEdgeList:
        edgeList.append(e)
        G.add_edge(*e)
            #print key
            #pprint.pprint(val)

    print len(nodeList), "nodes"
    print len(edgeList), "edges"

    #count node degrees of second degree follows
    nodeDegList = []
    for n, d in G.nodes_iter(data = True):
        if d["first_degree_follow"] == False and d["username"] <> new_user.username:
            nodeDegList.append(G.degree(n))
            #get max degree for dynamically resizing recs   
            if G.degree(n) > maxDegree:
                maxDegree = G.degree(n)
    nodeDegList.sort(reverse = True)
    #Dynamically set the count limit as the degree that gives at least 100 recs
    countLimit = nodeDegList[min(100,len(nodeDegList))]
    totalRecs = 0
    for deg in nodeDegList:
        if deg >= countLimit:
            totalRecs += 1
    totalRecs = min(100, totalRecs)
    #create 4 buckets of nodelabels ()
    recCutoffs = []
    for i in range(1,5):
        recCutoffs.append(nodeDegList[(i)*totalRecs/4])
    print countLimit
    print recCutoffs

    toRemove = []
    for n, d in G.nodes_iter(data = True):
        if d["username"] == new_user.username or  \
          (d["first_degree_follow"] == False and G.degree(n) < countLimit):
            toRemove.append(n)
    G.remove_nodes_from(toRemove)

    #remove nodes with no connections
    outdeg = G.degree()
    toRemove = [n for n in outdeg if outdeg[n] < 1]
    G.remove_nodes_from(toRemove)

    #remove edges where both nodes are already followed
    boringEdges = []
    interestingEdges = []
    for e in G.edges_iter(data = False):
        if e[0] in df1_follows and e[1] in df1_follows:
            boringEdges.append(e)
        else:
            interestingEdges.append(e)
            G.node[e[0]]["recEdges"] += 1
            G.node[e[1]]["recEdges"] += 1
            
    print len(boringEdges), "Boring edges", 
          len(interestingEdges), "Interesting edges"
    #G.remove_edges_from(edges2remove)

    #remove nodes with no rec edges (cuts down massive networks)
    toRemove = []
    for n, d in G.nodes_iter(data = True):
        if d["recEdges"] == 0:
            toRemove.append(n)
        if val["followers"] > maxfollows and d["first_degree_follow"]:
            maxfollows = val["followers"]
            
    G.remove_nodes_from(toRemove)
    print len(toRemove), "nodes removed in last stage of cleaning"

    #scale label size to have min 8 max 16
    #redo the edges
    boringEdges = []
    interestingEdges = []
    for e in G.edges_iter(data = False):
        if e[0] in df1_follows and e[1] in df1_follows:
            boringEdges.append(e)
        else:
            interestingEdges.append(e)
            G.node[e[0]]["recEdges"] += 1
            G.node[e[1]]["recEdges"] += 1
            
    print len(boringEdges), "Boring edges", 
          len(interestingEdges), "Interesting edges"
    nodesize = []
    nodeColor = []
    nodeLabels_f = {}
    nodeLabels_nf = {1 : {}, 2 : {}, 3 : {}, 4 : {}}
    notFound = []

    for n, d in G.nodes_iter(data = True):
        #print n 
        #pprint.pprint(d)
        #try:
        #nodeSize.append(max(d["followers"]/500, 1))
        if d["first_degree_follow"] == True:
            nodeColor.append('r')
            nodeLabels_f[n] = d["username"] 
            nodeSize.append(1)
        else:
            nodeColor.append('g')
            nodeSize.append(max(50, d["followers"]*300/maxfollows))
            nbin = 1        
            for cutoff in recCutoffs:
                if G.degree(n) >= cutoff:
                    nodeLabels_nf[nbin][n] = d["username"] + " [" + str(G.degree(n)) + "]"
                    break
                else:
                    nbin += 1
    #    except KeyError:
    #        #print n        
    #        #pprint.pprint(d)
    #        nodeSize.append(1)
    #        nodeColor.append('w')
    #        notFound.append(n)

    #draw the graph
    plt.figure(1,figsize=(60,60))
    pos = nx.spring_layout(G, iterations = 100)


    #nodes
    nx.draw_networkx_nodes(G, pos, alpha = .5, 
                           node_color = nodeColor, 
                           node_size = 1)
    #edges
    nx.draw_networkx_edges(G, pos, alpha = .15, edgelist = boringEdges)
    nx.draw_networkx_edges(G, pos, alpha = .4, edgelist = interestingEdges, 
                           edge_color = '#377eb8')
    #label
    nx.draw_networkx_labels(G, pos, 
                            labels = nodeLabels_f, 
                            font_weight = "bold", 
                            alpha = .6)
    nx.draw_networkx_labels(G, pos, 
                            labels = nodeLabels_nf[1], 
                            font_weight = "bold", 
                            font_color = '#bd0026', 
                            alpha = .8, 
                            font_size = 20)
    nx.draw_networkx_labels(G, pos, 
                            labels = nodeLabels_nf[2], 
                            font_weight = "bold", 
                            font_color = '#f03b20', 
                            alpha = .8, 
                            font_size = 16)
    nx.draw_networkx_labels(G, pos, 
                            labels = nodeLabels_nf[3], 
                            font_weight = "bold", 
                            font_color = '#fd8d3c', 
                            alpha = .8, 
                            font_size = 12)
    nx.draw_networkx_labels(G, pos, 
                            labels = nodeLabels_nf[4], 
                            font_weight = "bold", 
                            font_color = '#feb24c', 
                            alpha = .8, 
                            font_size = 8)
    plt.axis('off')
    plt.savefig("secondDegree_"+ new_user.username + "_+" + str(countLimit) +".png")
    plt.show


if __name__ == "__main__":
    reccomendationNetwork("oliver-stahlmann-195515684", 1)
