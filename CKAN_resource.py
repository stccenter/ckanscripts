#!/usr/bin/env python
import urllib2
import urllib
import json
import pprint
import copy
import requests
import os
import shutil

i = 1
sum = 0
flag = 1000
res = []

while(flag == 1000):
        params = (
                ('page_num', str(i)),
                ('concept_id', 'C43677728-LARC'),
                ('page_size', '1000'),
                ('pretty', 'true')
        )
        temp = requests.get('https://cmr.earthdata.nasa.gov/search/granules', params=params)

        datatext = temp.text
        datalist = datatext.split("<id>")

        del datalist[0]
        for str1 in datalist:
                str2 = str1.split("</id>")
                res.append(str2[0])

        flag = len(datalist)
        i = i + 1
        sum = sum + flag

print len(res)
path = "/home/ubuntu/test/"

shutil.rmtree(path)
os.mkdir(path)
for str3 in res:
        test = requests.get('https://cmr.earthdata.nasa.gov/search/concepts/' + str3 + '.json')
        #print str3
        file = open(path + str3 + '.json','w')
        file.write(test.text)
        file.close()

files = os.listdir(path)

for file_1 in files:

        print file_1
        f = open(path + file_1)
        first_dict = json.load(f)

        resource_dict = {}
        # Put the details of the dataset we're going to create into a dict.
        resource_dict['package_id'] = 'C43677728-LARC'.lower()
	
	if first_dict.has_key('links'):
        	resource_dict['url'] = first_dict['links'][0]['href']
		del(first_dict['links'])

        resource_dict['name'] = first_dict['title']
        item_1 = first_dict['boxes']
        first_dict['boxes'] = [item.encode('utf-8') for item in item_1]

        del(first_dict['title'])
        
        for key,value in first_dict.items():
            resource_dict[key] = str(value).encode('utf-8')
            
        data_string = urllib.quote(json.dumps(resource_dict))
#    try:
        request = urllib2.Request(
                'http://127.0.0.1:8080/api/3/action/resource_create')

        request.add_header('Authorization', 'dc4897d8-7770-40d6-9d70-e4655f80b3ea')

        response = urllib2.urlopen(request, data_string)
        assert response.code == 200

        response_dict = json.loads(response.read())
        assert response_dict['success'] is True

        created_package = response_dict['result']

