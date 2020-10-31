#!/usr/bin/python

import sys, getopt
from progressbar import ProgressBar
from lib.System import System
from lib.CollectRepo import CollectRepo

def CollectRepository():
    print(">>>>>>>>>>>> CollectRepo fom github...")
    # Retrieves repo data from Github by page
    CR = CollectRepo(System.get_repopath(), "username", "token")
    CR.collect_repositories()

def main(argv):
    step = 'all'
   
    #########################################################
    # get step
    #########################################################
    try:
        opts, args = getopt.getopt(argv,"hs:",["step="])
    except getopt.GetoptError:
        print ("run.py -s <step_name>")
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print ("arca.py -s all      ---  do all steps");
            print ("arca.py -s repo     ---  collect repositories from github");
            sys.exit()
        elif opt in ("-s", "--step"):
            step = arg;

    #########################################################
    # collect and analysis
    #########################################################
    if (step == "all"):
        CollectRepository ()
            
    elif (step == "repo"):
        CollectRepository ()
      
    else:
        print ("arca.py -s <all/repo>")  
   

if __name__ == "__main__":
   main(sys.argv[1:])
