#!/usr/bin/python

import os
import sys, getopt
from lib.TrainLogs import TrainLogs
from lib.CmmtClassify import CmmtClassify


def main(argv):
    Action = ""
    
    try:
        opts, args = getopt.getopt(argv,"hq:",["q="])
    except getopt.GetoptError:
        print ("Run.py -q <question number>")
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print ("Run.py -q <question number>")
            sys.exit()
        elif opt in ("-q", "--question"):
            Action = arg;

    if (not os.path.exists("result")):
        os.makedirs("result")

    if (not os.path.exists("data")):
        print ("data directory does not exist!!!!")
        sys.exit(2)

    if Action == "sample":
        TL = TrainLogs ()
        TL.GetTrainData ()
    if Action == "train":
        CC = CmmtClassify ()
        CC.Fit ("Train.txt", "TrainLabel.txt")
        CC.Validate ("Test.txt", "TestLabel.txt")
        CC.ClassifyLogs ()

   

if __name__ == "__main__":
   main(sys.argv[1:])
