import requests
import json

i = 1
sum = 0
flag = 1000
res = []

while(flag == 1000):
    
    params = (
            ('page_num', str(i)),
            ('page_size', '1000'),
            ('pretty', 'true'),
    )
    temp = requests.get('https://cmr.earthdata.nasa.gov/search/collections',params = params)

    datatext = temp.text

    datalist = datatext.split("<id>")
    del datalist[0]
    
    for str1 in datalist:
        str2 = str1.split("</id>")
        res.append(str2[0])

    flag = len(datalist)
    i = i + 1
    sum = sum + flag
    print flag
    
path = "/Users/kevin/Desktop/NASA_Metadata/res/"

sum = 0
for str3 in res:      
    #print str
    test = requests.get('https://cmr.earthdata.nasa.gov/search/concepts/' + str3 + '.json')
    file = open(path + str3 + '.json','w')
    #print test.text
    try:
        file.write(test.text)
    except UnicodeEncodeError:
        continue
    
    file.close()  
    sum = sum + 1
    
    if sum%1000==1:
        print sum

