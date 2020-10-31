#!/usr/bin/python

from lib.System import System
from lib.RetrvCommits import RetrvCommits
from progressbar import ProgressBar
import threading

class Task(threading.Thread):
    def __init__(self, TaskNo, Account, RepoList):
        threading.Thread.__init__(self)
        self.Account  = Account
        self.RepoList = RepoList
        self.TaskNo   = TaskNo
        
    def run(self):
        print ("[Task%d]Start.." %self.TaskNo)
        CC = RetrvCommits(self.TaskNo, self.Account["Name"], self.Account["Token"], self.RepoList)
        CC.collect_data ()
        print ("[Task%d]Finish collecting commits of %d repositories.." %(self.TaskNo, len(self.RepoList)))
        
        



    