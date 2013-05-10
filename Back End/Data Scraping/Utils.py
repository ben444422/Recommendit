import sys
from pprint import pprint
from cluster import *
from pymongo import MongoClient

#governs whether a subreddit should be added to a cluster or not
threshold = 15

class Cluster:    
    initID = 10
    clusters = []

    def __init__(self):
        initID = 10
        
    #fills the clusters list with the clusters from the database
    def cluster(self):
        client = MongoClient('localhost',27017)
        subreddits = client.RedditData.srDataComplete.find()
        srList = []
        i = 0
        for sr in subreddits:
            if (i > 40000):
                break;
            textList = sr['text'].split();
            textList = textList[:50]
            srList.append((sr['name'], textList)) 
            i = i + 1;
        i = 0
        for e in srList:
            print "processing subreddit " + str(i) + " of " + str(len(srList))
            i += 1
            highestSim = -1
            highestC = None
            for c in self.clusters:
                sim = self.getAvgSim(e, c[0])
                if sim > highestSim:
                    highestSim = sim
                    highestC = c[0]
            if highestSim < threshold:
                self.clusters.append(([e], self.initID))
                self.initID += 1
            else:
                highestC.append(e)
        i = 0
        for c in self.clusters:
            print "cluster ID " + str(c[1]) + ": "
            for sr in c[0]:
                sys.stdout.write(sr[0])
                sys.stdout.write(", ")
            sys.stdout.write("\n")
            i += 1
            
    # get the average similarity between a subreddit and a list of subreddits
    def getAvgSim(self, curSR, subreddits):
        totSim = 0
        for sr in subreddits:
            totSim += self.sim_v2(curSR, sr)
        return totSim/len(subreddits)

    # write the clusters data to the database
    def writeToDatabase(self):
        client = MongoClient('localhost', 27017)
        clusterData = client.RedditData.clusterData
        srAssignments = client.RedditData.srAssignments
        clusterData.remove()
        for c in self.clusters:
            clusterID = c[1]
            srList = c[0]
            for sr in srList:
                srAssDatum = {"name" : sr[0],
                              "id" : clusterID}
                if srAssignments.find_one({"name":sr[0]}) == None:
                    srAssignments.insert(srAssDatum)
                else:
                    srAssignments.update({"name":sr[0]}, srAssDatum)
                
                clusterDatum = {"id" : clusterID,
                                "subreddits" : sr[0]}    
                if clusterData.find_one({"id":clusterID}) == None:
                    clusterData.insert(clusterDatum)
                else:
                    subreddits = clusterData.find_one({"id":clusterID})["subreddits"]
                    subreddits += (" " + sr[0])
                    clusterDatum["subreddits"] = subreddits
                    clusterData.update({"id":clusterID}, clusterDatum)

    #return the similarity based on a simple intersection                
    def sim(self, sr1, sr2):
        wordList1 = sr1[1]
        wordList2 = sr2[1]
        return len(set(wordList1).intersection(set(wordList2)))
    
    # return a similarity based on a weighted scheme
    def sim_v2(self, sr1, sr2):
        wordList1 = sr1[1]
        wordList2 = sr2[1]
        weight = float(len(wordList1))
        score = float(0)
        i = 1.0
        for w in wordList1:
            if w in set(wordList2):
                score += weight/(0.5*(i+wordList2.index(w)+1))
            i += 1.0
        return score


c = Cluster()
c.cluster()
c.writeToDatabase()
