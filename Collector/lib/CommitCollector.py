#!/usr/bin/python

from lib.System import System
from progressbar import ProgressBar
import abc
import requests
import csv
from time import sleep
import re

class CommitCollector(metaclass=abc.ABCMeta):
    def __init__(self, Task, UserName, Token, RepoList=None):
        self.Task     = Task
        self.UserName = UserName
        self.Token    = Token
        self.RepoList = RepoList
        self.Output   = []
        
        self.StartYear = System.START_YEAR
        self.FilterRule =  re.compile(r'(^\.[a-zA-Z]|\.lock|\.md$|\.png$|\.jpg$|\.txt$)')
        
    def is_filtered (self, FileName):
        return self.FilterRule.match(FileName)
        
    def is_continue (self, errcode):
        codes = [404, 500]
        if (errcode in codes):
            return False
        else:
            return True
    
    def http_get_call (self, url):
        result = requests.get(url,
                              auth=(self.UserName, self.Token),
                              headers={"Accept": "application/vnd.github.mercy-preview+json"})
        if (self.is_continue (result.status_code) == False):
            print("$$$[Task%d]%s: %s, URL: %s" % (self.Task, result.status_code, result.reason, url))
            return None
        
        if (result.status_code != 200 and result.status_code != 422):
            print("[Task%d]%s: %s, URL: %s" % (self.Task, result.status_code, result.reason, url))
            sleep(1200)
            return self.http_get_call(url)     
        return result.json()
    
    def write_csv (self, FileName):
        with open(FileName, 'w', encoding='utf-8') as csv_file:
        
            writer = csv.writer(csv_file)

            header = list(self.Output[0].keys()) 
            writer.writerow(header)
            
            for item in self.Output:
                if item != None:
                    row = list(item.values())
                    writer.writerow(row)
        csv_file.close()
        
    def get_commit_path (self, RepoId):
        CommitDir  = System.setdir_cmmt (str(RepoId))    
        CommitFile = CommitDir + "/" + str(RepoId) + '.csv'
        return CommitFile
        
    def get_content_path (self, RepoId, Index):
        ContentDir = System.setdir_cmmt_content (str(RepoId))
        ContentFile = ContentDir + "/" + str(Index) + ".csv"
        return ContentFile
        
    def get_stats_path (self, RepoId, Index):
        StatsDir = System.setdir_cmmt_stats (str(RepoId))
        StatsFile = StatsDir + "/" + str(Index) + ".csv"
        return StatsFile
        
    def is_exist (self, file):
        return System.is_exist (file)
        
    def is_processed (self, id):
        return System.access_tag (str(id))
    
    @abc.abstractmethod
    def process(self, id, time=None, url=None):
        print("Abstract Method that is implemented by inheriting classes")
        
    def collect_data (self):
        No = 0;
        TotalNum = len (self.RepoList)
        for repo in self.RepoList:
            id = str(repo['id'])
            if (self.is_processed (id)):
                No += 1
                continue
            
            print ("[Task%d-%d/%d]repo -> %s : %s" %(self.Task, No+1, TotalNum, repo['id'], repo['url']))
            self.process(id, repo['created_at'], repo['url'])
            
            System.set_tag (id)
            No += 1


    