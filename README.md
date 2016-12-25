#SoundCloud Recommendation Engine

##Motivation
Frustrated by the quality of recommendations for new artists to follow on SoundCloud, I struck out to create my own.

##How it is Done
Since the track information is often removed on the SoundCloud API, I primarlily depended on the social networks various artists and subscribers had to figure out who people I was following were following that I was not already following. This FOMO (Fear of Missing Out) model, reveals which artists have the highest node degree, and how popular they already are.

##Technologies Used
1. Python (NetworkX, Matplotlib, Soundcloud)
2. SoundCloud API