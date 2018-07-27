#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 12 14:52:52 2018

@author: leonwang

Web Scrapping Script to gather baseball umpire's information from MLB website.


"""

import re
import requests
import pandas as pd

# MLB Umpires' Roster
url='http://mlb.mlb.com/mlb/official_info/umpires/roster.jsp'

# Get the whole HTML script
txt=requests.get(url)
content=txt.text

# Get the Umpire's Name
regex=r'<td><a href="/mlb/official_info/umpires/bio.jsp\?id=(\d*?|\w*?_\w*?)">(\w*? \w*?)</a></td>'
pat=re.compile(regex,re.S)
umpire=pat.findall(content)

# Get when are the umpires born
sub_url='http://mlb.mlb.com/mlb/official_info/umpires/bio.jsp?id='
regex_born=r'Born in (\w*? \d\d\d\d)'
pat_born=re.compile(regex_born)

# Get the residence place of the umpires
regex_resides =r'resides in (\w*?)\.|resides in (\w*?) '
pat_resides=re.compile(regex_resides,re.S)


# Get the hometown address of the umpires
regex_hometown=r'Born in (\w*? \d\d\d\d) in (.*?)\.\.\.'
pat_hometown=re.compile(regex_hometown,re.S)


# Get the service years for the umpires
regex_service=r'<strong>MAJOR LEAGUE SERVICE TIME:</strong>(.*?)</p>'
regex_service2=r'<strong>MAJOR LEAGUE SERVICE TIME</strong>:(.*?)</p>'
pat_service=re.compile(regex_service,re.S)
pat_service2=re.compile(regex_service2,re.S)

# Get the Picture to make the Umpire cards 
regex_picture=r'<img src="(/mlb/images/official_info/umpires/.*?.jpg)" width="275"'
pat_picture=re.compile(regex_picture,re.S)


# Informations are missing for some umpires
born_date=[]
hometown=[]
resides=[]
service_year=[]
bad_name=[]
pictureurl=[]
for i in umpire:
    sub_temp_url=sub_url+i[0]
    sub_content=requests.get(sub_temp_url)
    if pat_born.findall(sub_content.text)==[]:
        bad_name.append(i[1])
        continue
    try:
        pictureurl.append(pat_picture.findall(sub_content.text)[0])
        born_date.append(pat_born.findall(sub_content.text)[0])
    except:
        bad_name.append(i[1])
        continue
    try:
        service_year.append(pat_service.findall(sub_content.text)[0])
    except:
        service_year.append(pat_service2.findall(sub_content.text)[0])
    try:
        place=pat_resides.findall(sub_content.text)[0]
        if place[0]=="":
            resides.append(place[1])
        else:
            resides.append(place[0])
    except:
        place=pat_hometown.findall(sub_content.text)[0]
        resides.append("hometown "+place[1])
        

# Create the DataFrame to Aggregate the Umpire Information
name=[]
for i in umpire:
    if i[1] not in bad_name:
        name.append(i[1])
data=pd.DataFrame(index=name,columns=['Birth','Hometown/Residence','Service Years','Picture Url'])


# Output the result for Latex Name Card Generation
for i in range(len(data)):
    data.iloc[i]['Birth']=born_date[i]
    data.iloc[i]['Hometown/Residence']=resides[i]
    data.iloc[i]['Service Years']=service_year[i]
    data.iloc[i]['Picture Url']='http://mlb.mlb.com/'+pictureurl[i]

data['Name']=data.index
data['count']=list(range(1,len(data)+1))
data.to_csv("Umpire_data.csv",index=False)

# Retrieve the Umpire Picture for Latex Name Card Generation
from urllib.request import urlretrieve
def Get_pic(url_list):
    """
        Function to get the pictures from url and restore the pics locally to umpire_pic/ directory
        :params url_list a list contains all the urls of the pictures
        :return None
    """
    count=0
    for each_url in data['Picture Url']:
        count+=1
        urlretrieve(each_url,"umpire_pic/"+str(count)+".png") 


Get_pic(data['Picture Url'])



