#!c:\Python27\python.exe

import sys
sys.path.append('C:\cgi')
from test import *
import json
import cgi

import string
import operator
import praw
from time import sleep
from Recommender import Recommender


sys.stdout.write("Content-Type: application/json")
#sys.stdout.write("Access-Control-Allow-Origin: *")
#sys.stdout.write("Access-Control-Allow-Methods: GET, POST, PUT, DELTE")
fs = cgi.FieldStorage()

sys.stdout.write("\n")
sys.stdout.write("\n")

result = {}
result['Access-Control-Allow-Origin'] = '*'
result['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE'
result['keys'] = ",".join(fs.keys())
user = fs['username'].value

r = Recommender(user)
if (not r.isUserValid()):
	result['success'] = False
	result['message'] = "nothing"
else:
	sr = r.getRankingList()
	srStr = ""
	limit = 24
	for s in reversed(sr):
		if limit == 0:
			break
		limit -= 1
		srStr += s[0] + " "
	result['success'] = True
	result['message'] = srStr

sys.stdout.write(json.dumps(result,indent=1))
sys.stdout.write("\n")
sys.stdout.close()
