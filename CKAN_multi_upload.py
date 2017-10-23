#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 23 13:45:16 2017

@author: yjiang
"""

#!/usr/bin/env python
# things that maybe need to change: path, organizaor, key, host url&port
import urllib2
import urllib
import json
import copy
import os

path = "/home/ubuntu/cmrdata/res/"
files = os.listdir(path)
total = 0

for file_1 in files:
        total = total + 1
        if total < 5340 :
           continue

        try:
            f = open(path + file_1)
            first_dict = json.load(f)
            dataset_dict = {}
            # Put the details of the dataset we're going to create into a dict.
            dataset_dict['name'] = file_1.lower()[:-5]
            print(total)
            dataset_dict['owner_org'] = 'nasa-cmr' #lower case
            if first_dict.has_key('summary'):
                    dataset_dict['notes'] = first_dict['summary']
            dataset_dict['title'] = first_dict['title']
            dataset_dict['id'] = file_1

            temp = copy.deepcopy(first_dict)
            
            del temp['summary']
            del temp['title']
            del temp['id']
            
            if temp.has_key('links'):
                    del temp['links']
            
            if temp.has_key('boxes'):
                    item_1 = temp['boxes']
                    temp['boxes'] = [item.encode('utf-8') for item in item_1]
            if temp.has_key('organizations'):
                    item_2 = temp['organizations']
                    temp['organizations'] = [item.encode('utf-8') for item in item_2]
            if temp.has_key('dif_ids'):
                    item_3 = temp['dif_ids']
                    temp['dif_ids'] = [item.encode('utf-8') for item in item_3]

            extra_dict = []
            for key in temp:
                    entry = {}
                    entry['key'] = str(key)
                    entry['value'] = str(temp[key])
                    extra_dict.append(entry)

            dataset_dict['extras'] = extra_dict
            #print dataset_dict

            # Use the json module to dump the dictionary to a string for posting.
            data_string = urllib.quote(json.dumps(dataset_dict))

            # We'll use the package_create function to create a new dataset.
            request = urllib2.Request(
            'http://127.0.0.1:8080/api/3/action/package_create')

            # Creating a dataset requires an authorization header.
            # Replace *** with your API key, from your user account on the CKAN site
            # that you're creating the dataset on.
            request.add_header('Authorization', '1bddfc4c-bb03-4aa4-a3e7-b2e66017d94f')

            # Make the HTTP request.
            response = urllib2.urlopen(request, data_string)
            assert response.code == 200

            # Use the json module to load CKAN's response into a dictionary.
            response_dict = json.loads(response.read())
            assert response_dict['success'] is True

            # package_create returns the created package as its result.
            created_package = response_dict['result']
            #pprint.pprint(created_package)
        except Exception as e:
                continue        
