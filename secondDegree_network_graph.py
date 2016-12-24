# -*- coding: utf-8 -*-
"""
Created on Sun Apr 10 12:39:48 2016

@author: davidhey
"""
from follows_follows_genericUID_reworked import *
from soundcould_search_user import *
import networkx as nx
import pprint
import matplotlib.pyplot as plt

#repull data?
repull = 1
if repull == 1:
    #find a user by username
    new_user = searchUser("https://soundcloud.com/oliver-stahlmann-195515684", True)
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
countLimit = 10   #need to get this dynamically assigned
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
    if d["username"] == new_user.username or (d["first_degree_follow"] == False and G.degree(n) < countLimit):
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
        
print len(boringEdges), "Boring edges", len(interestingEdges), "Interesting edges"
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
        
print len(boringEdges), "Boring edges", len(interestingEdges), "Interesting edges"
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
nx.draw_networkx_nodes(G, pos, alpha = .5, node_color = nodeColor, node_size = 1) #, node_size = nodeSize
#edges
nx.draw_networkx_edges(G, pos, alpha = .15, edgelist = boringEdges)
nx.draw_networkx_edges(G, pos, alpha = .4, edgelist = interestingEdges, edge_color = '#377eb8')
#label
nx.draw_networkx_labels(G, pos, labels = nodeLabels_f, font_weight = "bold", alpha = .6)
nx.draw_networkx_labels(G, pos, labels = nodeLabels_nf[1], font_weight = "bold", font_color = '#bd0026', alpha = .8, font_size = 20)
nx.draw_networkx_labels(G, pos, labels = nodeLabels_nf[2], font_weight = "bold", font_color = '#f03b20', alpha = .8, font_size = 16)
nx.draw_networkx_labels(G, pos, labels = nodeLabels_nf[3], font_weight = "bold", font_color = '#fd8d3c', alpha = .8, font_size = 12)
nx.draw_networkx_labels(G, pos, labels = nodeLabels_nf[4], font_weight = "bold", font_color = '#feb24c', alpha = .8, font_size = 8)
#sequential color scheme
#ffffb2
#fecc5c
#fd8d3c
#e31a1c

#d7191c
#fdae61
#abd9e9
#2c7bb6

#feb24c
#fd8d3c
#f03b20
#bd0026
plt.axis('off')
plt.savefig("secondDegree_"+ new_user.username + "_+" + str(countLimit) +".png")
plt.show
