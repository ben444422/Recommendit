import praw
import sys
import json
import urllib2
import operator
from pymongo import MongoClient
from pprint import pprint
from Parser import Parser

# user object that holds parsed and clean user data
class User:    
    allWords = []
    srList = []
    userSubreddits = {}
    punc = ['[',']','{','}','(',')','<','>']
    isValid = True
    def __init__(self, uName):
        self.getInfo(uName)
    def isUserValid(self):
        return self.isValid
    # get all user information
    def getInfo(self, uName):
        r = praw.Reddit('Reddit User Data Scraper')
        try:
            user = r.get_redditor(uName)
        except:
            self.isValid = False
            return
         
        comments = user.get_comments(limit = None)
        totStr = ""
        
        for c in comments:
            data = vars(c)['body']
            data = data.encode('ascii','ignore')
            data = data.strip()
            totStr = totStr + data + " "

            #get and save the subreddit
            srName = vars(vars(c)['subreddit'])['display_name']
            srName = srName.lower()
            if srName not in self.userSubreddits:
                self.userSubreddits[srName] = 0
            else:
                self.userSubreddits[srName] = self.userSubreddits[srName] + 1

        submissions = user.get_submitted(limit = None)
    
        for s in submissions:
            data = vars(s)['title']
            data = data.encode('ascii', 'ignore')
            data = data.strip()
            totStr = totStr + data + " " 

            #get and save the subreddit
            srName = vars(vars(s)['subreddit'])['display_name']
            srName = srName.lower()
            if srName not in self.userSubreddits:
                self.userSubreddits[srName] = 0
            else:
                self.userSubreddits[srName] = self.userSubreddits[srName] + 1
        
        srListTemp = sorted(self.userSubreddits.iteritems(), key=operator.itemgetter(1))
        for sr in srListTemp:
            self.srList.insert(0, sr[0])

        parser = Parser(totStr)        
        self.allWords = parser.getWordList()
        tempWords = []
        for word in self.allWords:
            if len(word) == 0:
                continue
            if word[0] in self.punc:
                word = word[1:]
            if word[-1:] in self.punc:
                word = word[:-1]
            tempWords.append(word)
        self.allWords = tempWords
 
# generate a recommendation based on a username
class Recommender:    
    user = None
    POOL_SIZE = 40

    def __init__(self, uName):
        self.user = User(uName)

    def isUserValid(self):
        return self.user.isUserValid()
    # create a ranking list based on clusters
    def getRankingList_v2(self):
        subreddits = self.user.srList
        srPool = []
        rankingList = {}
        client = MongoClient('localhost', 27017)
        userWordList = self.user.allWords
        for srName in subreddits:
            idDatum = client.RedditData.srAssignments.find_one({"name":srName})
            if idDatum == None:
                continue
            srID = idDatum["id"]
            srStrDatum = client.RedditData.clusterData.find_one({"id":srID})
            if srStrDatum == None:
                continue
            for sr in srStrDatum["subreddits"].split():
                srPool.append(sr)

        for srName in srPool:
            srDatum = client.RedditData.srDataComplete.find_one({"name":srName})
            if srDatum == None:
                continue
            wordList = srDatum["text"].split()
            out = self.getScore(wordList[:self.POOL_SIZE], userWordList[:200])
            score = out[0]
            rankingList[srName] = score
        sortedSr = sorted(rankingList.iteritems(), key=operator.itemgetter(1))
        return sortedSr
    # create a ranking list based on all subreddits
    def getRankingList(self):
        rankingList = {}
        client = MongoClient('localhost', 27017)
        subreddits = client.RedditData.srDataComplete.find()
        userWordList = self.user.allWords
        srWords = {}

        for sr in subreddits:
            words = []
            srName = sr['name']
            wordList = sr['text'].split()
            out = self.getScore(wordList[:self.POOL_SIZE], userWordList[:200])
            score = out[0]
            words = out[1]
            rankingList[srName] = score
            srWords[srName] = words
        
        sortedSR = sorted(rankingList.iteritems(), key=operator.itemgetter(1))
        return sortedSR

    # returns the similarity score betweena a subreddit word list and the user word list
    def getScore(self, list1, userList2):
        w = len(list1)*2
        i = 1
        score = 0
        words = []
        for word in list1:
            if word in userList2:
                score = score + (w/i)
                words.append(word)
            i = i + 1
        return (score, words)

