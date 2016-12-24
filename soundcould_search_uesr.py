# -*- coding: utf-8 -*-
"""
Created on Sun Apr 10 21:35:27 2016

@author: davidhey
"""

from soundcloud_functions import *
import pprint

def searchUser(toSearch, url):
    """
    When url = true just resolve the user page from the url, and dont search
    """
    returnUser = []    
    client = create_client(CLIENTID)
    
    if url == False:
        query = toSearch
        users = client.get('/users', q = query)
        
        for user in users:
            #pprint.pprint(user.__dict__)
            if user.username == toSearch:
                returnUser = user
    else:
        returnUser = client.get('/resolve', url = toSearch)
            
    return returnUser