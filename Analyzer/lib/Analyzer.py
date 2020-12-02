#!/usr/bin/python
import os
import time
import csv 
import pandas as pd
from patsy import dmatrices
import numpy as np
from datetime import datetime, timedelta

COMMIT_NUM = 200000
TopLang = ["c","c++","ruby","java","shell","php","c#","python","javascript","typescript"]


class RepoInfo ():
    def __init__(self, RepoId, LangNum, AuthorNum, Age, CmmtNum, Vulb1Num, Vulb2Num, Vulb3Num, Vulb4Num):
        self.RepoId    = RepoId
        self.LangNum   = LangNum
        self.AuthorNum = AuthorNum
        self.Age       = Age
        self.CmmtNum   = int(CmmtNum/Age)
        self.Vulb1Num  = Vulb1Num
        self.Vulb2Num  = Vulb2Num
        self.Vulb3Num  = Vulb3Num
        self.Vulb4Num  = Vulb4Num

    def AddLangVariable (self, C, CPP, RUBY, JAVA, SHELL, PHP, CSHP, PYTHON, JAVASCRIPT, TYPESCRIPT):
        self.C = C
        self.CPP = CPP
        self.RUBY = RUBY
        self.JAVA = JAVA
        self.SHELL = SHELL
        self.PHP = PHP
        self.CSHP = CSHP
        self.PYTHON = PYTHON
        self.JAVASCRIPT = JAVASCRIPT
        self.TYPESCRIPT = TYPESCRIPT

class Analyzer():
    def __init__(self):
        self.RepoStat = {}

    def IsExist(self, file):
        isExists = os.path.exists(file)
        if (not isExists):
            return False
        
        fsize = os.path.getsize(file)/1024
        if (fsize == 0):
            return False
        return True

    def GetCmmtInfo (self, CmmtOrigFile):
        Authors  = {}
        MaxDate  = "1999-01-01T13:44:12Z"
        MinDate  = "2020-12-31T13:44:12Z"
        CmmtNum  = 0
        CDF = pd.read_csv(CmmtOrigFile)
        for CIndex, CRow in CDF.iterrows():     
            Authors[CRow['author']] = 1
            date = CRow['date']
            if (date > MaxDate):
                MaxDate = date
            if (date < MinDate):
                MinDate = date
            CmmtNum += 1
            if CmmtNum >= COMMIT_NUM:
                break
        
        AuthorNum = len (Authors)
        MaxTime = datetime.strptime(MaxDate, '%Y-%m-%dT%H:%M:%SZ')
        MinTime = datetime.strptime(MinDate, '%Y-%m-%dT%H:%M:%SZ')
        Age = int((MaxTime - MinTime).days/30)
        return AuthorNum, Age, CmmtNum

    def GetVulbyNum (self, CmmtStatFile):
        VulbNum = {}
        VulbNum[1] = 0
        VulbNum[2] = 0
        VulbNum[3] = 0
        VulbNum[4] = 0
        CDF = pd.read_csv(CmmtStatFile)
        for CIndex, CRow in CDF.iterrows():     
            Type = CRow['Clf']
            if Type >= 5:
                continue            
            VulbNum[Type] += CRow['Number']
        return VulbNum

    def SaveRepoStat (self, File="result/RepoStat.csv"):      
        with open(File, 'w') as CsvFile:
            Writer = csv.writer(CsvFile)
            Headers = list(list(self.RepoStat.values())[0].__dict__.keys())
            Headers = [header.replace(" ", "_") for header in Headers]
            Writer.writerow(Headers)
            for key, value in self.RepoStat.items():
                row = list(value.__dict__.values())
                Writer.writerow(row)
        CsvFile.close()

    def WriteVulbStats (self, VulbData, ResultFile="result/VulbState.csv"):
        with open(ResultFile, 'w', encoding='utf-8') as File:
            Writer = csv.writer(File)
            #print (Vulnerabilities)
            Header = list(("Clf", "Number"))
            Writer.writerow(Header)  
            for item in VulbData.items ():
                if item != None:
                    row = list(item)
                    Writer.writerow(row)
        File.close()

    def GetLangInfo (self, LangStr):
        LangInfo = {}
        for Lang in TopLang:
            LangInfo[Lang] = 0
    
        LangDict = eval (LangStr)
        for Lang, Size in LangDict.items ():
            if LangInfo.get (Lang) == None:
                continue
            LangInfo[Lang] = 1
        return LangInfo
            

    def Process (self, RepoFile="Repository_List.csv"):
        CmmtOrigDir = "data/CmmtSet"
        CmmtStatDir = "result/CmmtSet"

        VulbData = {}

        PDF = pd.read_csv("data/" + RepoFile)       
        for PIndex, PRow in PDF .iterrows():

            RepoId = PRow ['id']
            CmmtOrigFile = CmmtOrigDir + "/" + str (RepoId) + ".csv"
            CmmtStatFile = CmmtStatDir + "/" + str (RepoId) + ".csv"

            now = datetime.now().time()
            print (now, "[", PIndex, "/", len(PDF), "]", ":classify ", CmmtOrigFile, " -> ", end=" ")

            if self.IsExist (CmmtOrigFile) == False or self.IsExist (CmmtStatFile) == False:
                print (" ")
                continue

            AuthorNum, Age, CmmtNum = self.GetCmmtInfo (CmmtOrigFile)
            if Age == 0 or AuthorNum == 0 or CmmtNum == 0:
                continue
            VulbNum = self.GetVulbyNum (CmmtStatFile)
            LangNum = PRow ['language_dictionary'].count(":")
            print ("Getinfo: ", LangNum, AuthorNum, Age, VulbNum, CmmtNum)

            RI = RepoInfo (RepoId, LangNum, AuthorNum, Age, CmmtNum, VulbNum[1], VulbNum[2], VulbNum[3], VulbNum[4])
            LangInfo = self.GetLangInfo (PRow ['language_dictionary'])
            RI.AddLangVariable (LangInfo[TopLang[0]], LangInfo[TopLang[1]], LangInfo[TopLang[2]], LangInfo[TopLang[3]], LangInfo[TopLang[4]],
                                LangInfo[TopLang[5]], LangInfo[TopLang[6]], LangInfo[TopLang[7]], LangInfo[TopLang[8]], LangInfo[TopLang[9]])
            
            self.RepoStat [RepoId] = RI

        self.SaveRepoStat ()
        self.WriteVulbStats (VulbData)
    
