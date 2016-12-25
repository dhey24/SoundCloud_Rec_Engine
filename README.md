# SoundCloud_Rec_Engine
SoundCloud Recommendation Engine

##Motivation
Frustrated with the quality of the recommendations I was getting from SoundCloud natively, I struck out on my own in an attempt to do better.

##Approach
The idea is to create a second degree network of who all the artists/subscribers I follow are following. Using this network, it is easy to see who others are most commonly following that I am not already following (higher node degree). In addition, who is following whom can also provide information about what kind of music that artist makes, and when visualized in a force directed network graph you can interpolate genre even if you do not know who the artist based upon who they are nearest to.
I have also written a script to export the network and metadata to CSV to visualize in Tableau.

##Technologies
Python (NetworkX, soundcloud, matplotlib.pyplot) 
SoundCloud API
