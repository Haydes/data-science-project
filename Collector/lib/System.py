
import os


class System():
    PAGE_COUNT   = 10
    PER_PAGE     = 100

    BaseDir      = "./Data"
    CmmtSet      = BaseDir + "/CmmtSet"
    TagSet       = BaseDir + "/TagSet"
    
    @staticmethod
    def get_repopath():
        Dir = System.setdir (System.BaseDir)
        return (Dir + "/Repository.csv")

    @staticmethod
    def mkdir(path):
        path=path.strip()
        path=path.rstrip("\\")
        isExists=os.path.exists(path)
        if not isExists:
            os.makedirs(path)
    @staticmethod        
    def setdir(dir):
        isExists=os.path.exists(dir)
        if not isExists:
            os.makedirs(dir)
        return dir
        
    @staticmethod
    def setdir_cmmt(dir):
        NewDir = System.CmmtSet + "/" + dir
        return System.setdir (NewDir)
        
    @staticmethod
    def setdir_cmmt_content(dir):
        NewDir = System.CmmtSet + "/" + dir + "/Content"
        return System.setdir (NewDir)
    
    @staticmethod
    def setdir_cmmt_stats(dir):
        NewDir = System.CmmtSet + "/" + dir + "/Stats"
        return System.setdir (NewDir)
        
    @staticmethod
    def is_exist(file):
        return os.path.exists(file)
        
    @staticmethod
    def set_tag(tag):
        NewDir = System.TagSet
        System.setdir (NewDir)
        file = open(NewDir + "/" + tag,'w')
        file.close()
        
    @staticmethod
    def access_tag(tag):
        tagPath = System.TagSet + "/" + tag
        isExists = os.path.exists(tagPath)
        if not isExists:
            return False
        return True

