import string 
import operator
from pymongo import MongoClient
from pprint import pprint

"""
This script cleans the data associated with the subreddits in the database
"""

totSR = 0
RATIO = 0.3
wordFreq = {}
client  = MongoClient('localhost', 27017)
subreddits = client.RedditData.srDataComplete.find()

# find the frequency of the terms in all subreddits
for sr in subreddits:
    totSR = totSR + 1
    wordList = sr['text'].split()
    print "processing: " + sr['name'] 
    for word in wordList:
        if word in wordFreq:
            wordFreq[word] = wordFreq[word] + 1
        else:
            wordFreq[word] = 1
    

rankedFreq = sorted(wordFreq.iteritems(), key=operator.itemgetter(1))
thresh = totSR*RATIO

# get the common words shared across many subreddits
commonWords = []
for w in reversed(rankedFreq):
    freq = w[1]
    word = w[0]
    print freq
    if freq > thresh:
        commonWords.append(word)
    else:
        break

pprint(commonWords)

def isNum(num):
    try:
        float(num)
        return True
    except ValueError:
        return False

commonWords.append('-')
punc = ['[',']','{','}','(',')','<','>', '\"','\'', ',','.','?','!','*','~','-','_']
client = MongoClient('localhost', 27017)
subreddits = client.RedditData.srDataComplete.find()
srDataComplete = client.RedditData.srDataComplete

# clean each subreddit
for sr in subreddits:
    srName = sr['name']
    wordList = sr['text'].split()
    tempList = []
    
    if (len(wordList) < 50):
        srDataComplete.remove({"name":srName})
        continue

    for word in wordList:
        if len(word) == 0:
            continue
        
        if word in commonWords:
            print "removing common"
            continue
        
        if word[0] in punc:
            word = word[1:]
        if word[-1:] in punc:
            word = word[:-1]
        
        #don't add words that are only punctuation
        isValid = True
        for c in string.punctuation:
            s = word.replace(c,"")
            if (len(s) == 0):
                isValid = False
                break
        if (not isValid):
            continue
        
        if (isNum(word)):
            continue

        tempList.append(word)    
    
    print "Cleaning subreddit: " + srName
    datum = { "name": srName,
              "text": " ".join(tempList) }
    srDataComplete.update({"name":srName}, datum)
    
            
