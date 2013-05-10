import praw
import string
import json
import urllib2
import sys
from pymongo import MongoClient
from pprint import pprint 
from Parser import Parser

#scrapes subreddit data from reddit and fills the database with the data

subreddits = open('subreddits', 'r')
client = MongoClient('localhost', 27017)
redditData = client.RedditData
srData = redditData.srData

r = praw.Reddit('Subreddit data scraper')
i = 0;

for subreddit in subreddits:
    try:
        sr = r.get_subreddit(subreddit.strip())
        if sr is None:
            continue
        submissions = sr.get_top_from_all(limit=1000);
        if submissions is None:
            continue
    
        sys.stderr.write("Processing subreddit # " + str(i) + ": " + subreddit[:-1] + "\n")
        text = "" 
        for submission in submissions:
            data = vars(submission)['title']
            data = data.encode('ascii', 'ignore')
            data = data.strip()
            text = text + data + " "
            
        if text == "":
            continue;

        parser = Parser(text)    
        wordList = parser.getWordList()
        
        text = " ".join(wordList)
        srName = subreddit[:-1]
        srName = srName.lower()
        
        srDatum = { "name" : srName,
                    "text" : text }
        pprint(wordList[:10])
            
        if srData.find_one({"name": srName}) == None:
            srData.insert(srDatum)
        else:
            srData.update({ "name": srName }, srDatum)
    except:
        sys.stderr.write("Error in processing subreddit # " + str(i) + ": " + subreddit[:-1] + "\n")        
    i += 1

