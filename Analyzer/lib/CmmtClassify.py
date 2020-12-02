#!/usr/bin/python
import nltk
nltk.download('stopwords');nltk.download('brown');nltk.download('punkt');nltk.download('wordnet')
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()
import time
import pandas as pd
import os
import csv
from datetime import datetime
from sklearn.naive_bayes import GaussianNB
from lib.TextClean import TextClean
TC = TextClean () 

COMMIT_NUM = 200000

class CmmtClassify():
    def __init__(self):
        self.Vocabulary = self.GetVocabulary ("keywords.txt")

    def ReadText (self, Text):
        Df = pd.read_table("data/" + Text, header=None)
        Data = Df.values
        return Data

    def Serialize (self, Docment):
        SerDoc = []
        for Doc in Docment:
            for Word in Doc:
                SerDoc.append (Word)     
        return SerDoc

    def Preprocessing (self, Text, IsClean=False):
        # read text data
        OriginalData = self.ReadText (Text)

        if IsClean:
            return OriginalData

        # remove stropword from Data
        Data = []
        for Doc in OriginalData:
            NewDoc = TC.Cleaning (Doc[0])
            Data.append (NewDoc)
        return Data

    def GetVocabulary (self, KeywordFile):
        Df = pd.read_table("data/" + KeywordFile)
        Df.columns = ['key']
        return Df['key']

    def GetFeatureVector (self, TrainDoc, Vocabulary):
        FeatureVec = []
        for Doc in TrainDoc:
            DocVec = []
            for Word in Vocabulary:
                if Word in Doc:
                    DocVec.append (1)
                else:
                    DocVec.append (0)
            FeatureVec.append (DocVec)
        return FeatureVec

    def Fit (self, Text, Label):
        TrainDoc = self.Preprocessing (Text, True)       
        print ("Vocabulary Length = %d" %len(self.Vocabulary))

        FeatureVec = self.GetFeatureVector (TrainDoc, self.Vocabulary)
        TrainLabel = self.Serialize (self.ReadText (Label))
        TrainLabel = TrainLabel[1:len(TrainDoc)+1]
        self.ClsNum = len (set (TrainLabel))
        print ("TrainDoc length = %d, ClsNum = %d" %(len(TrainDoc), self.ClsNum))

        gnb = GaussianNB()
        self.FitGnb = gnb.fit(FeatureVec, TrainLabel)
        print ("Finish train...")

    def Predict (self, Message):
        Message = TC.Cleaning (Message)
        if (len (Message) == 0):
            return 5
        FeatureVec = self.GetFeatureVector (Message, self.Vocabulary)
        Pred = self.FitGnb.predict(FeatureVec)

        Result = {}
        for p in Pred:
            Res = Result.get (p)
            if Res == None:
                Result[p] = 1
            else:
                Result[p] += 1
        Max = 0
        Clf = 5
        for K, V in Result.items ():
            if V > Max:
                Max = V
                Clf = K
        return Clf
            

    def IsExist(self, file):
        isExists = os.path.exists(file)
        if (not isExists):
            return False
        
        fsize = os.path.getsize(file)/1024
        if (fsize == 0):
            return False
        return True      

    def Validate (self, Text, Label):
        TestDoc = self.Preprocessing (Text)
        print (len(TestDoc))
        TestFeatureVec = self.GetFeatureVector (TestDoc, self.Vocabulary)
        TestLabel = self.Serialize (self.ReadText (Label))
        TestLabel = TestLabel[1:len(TestDoc)+1]

        Pred = self.FitGnb.predict(TestFeatureVec)
        print (len(Pred))
        Mistakes = (TestLabel != Pred).sum()
        print("GaussianNB accuracy: %f" % (1 - Mistakes/len(TestFeatureVec)))

    def WriteResults (self, ResultFile, Vulnerabilities):
        with open(ResultFile, 'w', encoding='utf-8') as File:
            Writer = csv.writer(File)
            #print (Vulnerabilities)
            Header = list(("Clf", "Number"))
            Writer.writerow(Header)  
            for item in Vulnerabilities.items ():
                if item != None:
                    row = list(item)
                    Writer.writerow(row)
        File.close()


    def ClassifyLogs (self, RepoFile="Repository_List.csv"):
        CmmtDir = "data/CmmtSet"
        TragetDir = "result/CmmtSet"

        PDF = pd.read_csv("data/" + RepoFile)       
        for PIndex, PRow in PDF .iterrows():

            RepoId = PRow ['id']
            CommitFile = CmmtDir + "/" + str (RepoId) + ".csv"
            ResultFile = TragetDir + "/" + str (RepoId) + ".csv"

            now = datetime.now().time()
            print (now, "[", PIndex, "/", len(PDF), "]", ":classify ", CommitFile, " -> ", end=" ")
            
            if os.path.exists(ResultFile):
                print (" ")
                continue;
             
            if self.IsExist (CommitFile) == False:
                print (" ")
                continue
    
            Vulnerabilities = {}
            CDF = pd.read_csv(CommitFile)
            print (" [", len(CDF), "]")
            for CIndex, CRow in CDF.iterrows():
                Clf = self.Predict (CRow['message'])
                Num = Vulnerabilities.get (Clf)
                if Num == None:
                    Vulnerabilities [Clf] = 1
                else:
                    Vulnerabilities [Clf] += 1
                if CIndex >= COMMIT_NUM:
                    break;

            
            self.WriteResults (ResultFile, Vulnerabilities)  

