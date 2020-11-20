#!/usr/bin/python

from progressbar import ProgressBar
import pandas as pd
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import time
import re
import ast
import os


from lib.TextClean import TextClean
TC = TextClean ()

class SecurityType ():
    def __init__ (self, Label, Keywords):
        self.Label    = Label
        self.Keywords = Keywords
        self.Messages = []

    def LabelMatch (self, Message):
        for Word in Message:
            if Word in self.Keywords:
                return self.Label
            else:
                result = process.extractOne(Word, self.Keywords, scorer=fuzz.ratio)
                if (result != None and result[1] >= 99):
                    return self.Label
        return None 

    def AddMsg (self, Message):
        self.Messages.append (Message)

    def GetMsgNum (self):
        return len (self.Messages)

class TrainLogs():

    def __init__(self, FileName="Repository_List.csv", KeywordFile = "keywords.txt", Number=10000):
        self.FileName = FileName
        self.Keywords = self.LoadKeywords (KeywordFile)     
        self.InitSecurityTypes ()
        self.exception = re.compile(r'^current$|^ctrl$|^design$|^designer$|^description$|^described$|^descriptive$|^desc$|^list$|^sure$|^flow$|^brace$|^able$|^action$|^back$|^open$|^read$|^the$|^char$|^site$|^tweak$|^print$|^printf$')
        self.Number      = Number
        
    def InitSecurityTypes (self):
        self.SecurityTypes = {}
        self.SecurityTypes[1] = SecurityType ("Risky_resource_management", 
                                              ['restricted directory', 'dangerous function', 'format string', 'buffer', 'wraparound', 'integrity', 'integer', 'overflow', 'Sensitive', 'Sprintf', 'underflow', 'signedness', 'length', 'overrun'])
        self.SecurityTypes[2] = SecurityType ("Insecure_interaction_between_components", 
                                              ['injection', 'blacklist', 'CSRF', 'Cross-Site', 'forger', 'Forgery', 'SQLI', 'exploit', 'XSRF', 'backdoor', 'insecure', 'threat', 'specialchar', 'penetration'])
        self.SecurityTypes[3] = SecurityType ("Porous_defenses", 
                                              ['leak', 'permission', 'OpenSSL', 'crypto', 'encryption', 'cipher', 'bcrypt', 'entropy', 'unauthenticated', 'weak', 'Exposure', 'expose', 'ciphers', 'wireguard', 'breakable'])
        self.SecurityTypes[4] = SecurityType ("Other", [])
        self.SecurityTypes[5] = SecurityType ("None", [])
        self.ClfNum = 5

    def LoadKeywords(self, KeywordFile):
        Df = pd.read_table("data/" + KeywordFile)
        Df.columns = ['key']
        return Df['key']
    
    def IsFiltered (self, Word):
        return self.exception.match(Word)

    def IsFin (self):
        TargetNum = self.Number/self.ClfNum
        for Label, ST in self.SecurityTypes.items ():
            MsgNum = ST.GetMsgNum ()
            print ("Label[%d]: %d" %(Label, MsgNum))
            if MsgNum < TargetNum:
                return False
        return True
        
        
    def IsVulnerable(self, Message, Threshhold):  
        FzResults = {}
        
        for Word in Message:
            if self.IsFiltered(Word):
                continue
            
            if Word in self.Keywords:
                return True
            else:
                result = process.extractOne(Word, self.Keywords, scorer=fuzz.ratio)
                if (result[1] >= Threshhold):
                    return True

        return False

    def FormalizeMsg (self, Message):
        Message = str (Message)
        if (Message == ""):
            return None
        
        CleanText = TC.Cleaning (Message)
        if (CleanText == ""):
            return None

        return CleanText

    def IsProcessed (self, TrainFile):
        TrainFile = TrainFile + ".csv"
        return os.path.exists (TrainFile)

    def GetLabel (self, Message):
        for Label, ST in self.SecurityTypes.items ():
            if ST.LabelMatch (Message):
                return Label
        return 4

    def IsExist(self, file):
        isExists = os.path.exists(file)
        if (not isExists):
            return False
        
        fsize = os.path.getsize(file)/1024
        if (fsize == 0):
            return False
        return True      

    def GetTrainData (self, Ratio = 0.8):
        CmmtDir = "data/CmmtSet"
        TargetNum = self.Number/self.ClfNum
        
        PDF = pd.read_csv("data/" + self.FileName)       
        for PIndex, PRow in PDF .iterrows():

            RepoId = PRow ['id']
            CommitFile = CmmtDir + "/" + str (RepoId) + ".csv"
            if self.IsExist (CommitFile) == False:
                continue
            print ("process %s" %CommitFile, end="\r")
            
            CDF = pd.read_csv(CommitFile)         
            for CIndex, CRow in CDF.iterrows():
                Message = self.FormalizeMsg (CRow['message'])
                if (Message == None and len (Message < 10)):
                    continue
                            
                IsVulb = self.IsVulnerable (Message, 100)
                print (Message, " ---> ", IsVulb)
                if IsVulb:
                    Label = self.GetLabel (Message)
                    if self.SecurityTypes[Label].GetMsgNum () < TargetNum:
                        self.SecurityTypes[Label].AddMsg (Message) 
                else:
                    Label = 5
                    if self.SecurityTypes[Label].GetMsgNum () < TargetNum:
                        self.SecurityTypes[Label].AddMsg (Message)

                if CIndex >= 20000:
                    break;
            
            self.DumpTrainData (Ratio)
            if self.IsFin ():
                break
        

    
    def DumpTrainData (self, Ratio):
        TrainNum = int (self.Number * Ratio/self.ClfNum)
        print ("TrainNum = %d" %TrainNum)
        
        DFile = open('data/Train.txt', 'w')
        LFile = open('data/TrainLabel.txt', 'w')

        TDFile = open('data/Test.txt', 'w')
        TLFile = open('data/TestLabel.txt', 'w')

        LbFile = open('data/LabelInstruction.txt', 'w')

        for Label, ST in self.SecurityTypes.items ():
            LbFile.write(str(Label) + ", " + ST.Label + "\n")
            
            Num = 0
            for Msg in ST.Messages:
                if Num < TrainNum:
                    DFile.write(" ".join(Msg) + "\n")
                    LFile.write (str (Label) + "\n")
                else:
                    TDFile.write(" ".join(Msg) + "\n")
                    TLFile.write (str (Label) + "\n")
                Num += 1
        
        DFile.close ()
        LFile.close ()
        TDFile.close ()
        TLFile.close ()
        LbFile.close ()


