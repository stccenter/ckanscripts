import urllib2
import urllib
import json
import pprint
import copy
import os

path = "/home/ubuntu/res/"
files = os.listdir(path)
total = 0

request = urllib2.Request(
        'http://127.0.0.1:8080/api/3/action/package_list')

request.add_header('Authorization', 'dc4897d8-7770-40d6-9d70-e4655f80b3ea')

response = urllib2.urlopen(request)
assert response.code == 200

resdict = json.loads(response.read())
strings = resdict['result']
print strings

for item in strings:
    request = urllib2.Request(
        'http://127.0.0.1:8080/api/3/action/package_delete')

    request.add_header('Authorization', 'dc4897d8-7770-40d6-9d70-e4655f80b3ea')
    sdict = {}
    sdict['id'] = item
    data_string = urllib.quote(json.dumps(sdict))
    response = urllib2.urlopen(request, data_string)
    assert response.code == 200

for file_1 in files:

    f = open(path + file_1)

    try:
        	first_dict = json.load(f)
    except ValueError:
		total = total + 1
		continue
    try:
        dataset_dict = {}
        dataset_dict['name'] = file_1.lower()[:-5]

        dataset_dict['owner_org'] = 'nasa-cmr'
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
	
            if entry['key'] == 'boxes':
                box_temp = entry['value'].strip('[]').split(', ')

                coor_list = []
                for box_str in box_temp:
                    box_list = box_str.strip('\'').split()
                    box_list2 = []
                    for str2 in box_list:
                        box_list2.append(float(str2))

                    geo_dict = {}
                    geo_dict['type'] = 'Polygon'
                    point_list = []
                    point_list.append([box_list2[1],box_list2[0]])
                    point_list.append([box_list2[3],box_list2[0]])
                    point_list.append([box_list2[3],box_list2[2]])
                    point_list.append([box_list2[1],box_list2[2]])
                    point_list.append([box_list2[1],box_list2[0]])

                coor_list.append(point_list)
                geo_dict['coordinates'] = coor_list

                new_extra = {}
                new_extra['key'] = 'spatial'
                new_extra['value'] = json.dumps(geo_dict)

                extra_dict.append(new_extra)
	
        dataset_dict['extras'] = extra_dict
    
        data_string = urllib.quote(json.dumps(dataset_dict))
        total = total + 1
#    try:
        request = urllib2.Request(
                'http://127.0.0.1:8080/api/3/action/package_create')

        request.add_header('Authorization', 'dc4897d8-7770-40d6-9d70-e4655f80b3ea')

        response = urllib2.urlopen(request, data_string)
        assert response.code == 200

        response_dict = json.loads(response.read())
        assert response_dict['success'] is True

        created_package = response_dict['result']
        print file_1
    except Exception as e:
        continue
