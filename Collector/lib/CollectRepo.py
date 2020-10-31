import csv  
import sys   
import os
import re
from lib.System import System
from datetime import datetime, date
from time import sleep
import requests
from progressbar import ProgressBar

csv.field_size_limit(sys.maxsize)
PAGE_COUNT  = System.PAGE_COUNT
PER_PAGE    = System.PER_PAGE


class CollectRepo():

    Fields = ['id', 'size', 'created_at', 'forks',
              'open_issues', 'subscribers_count',
              'stargazers_count', 'language_dictionary',
              'owner_type', 'url', 'topics', 'description']

    def __init__(self, RepoPath, Username, Token):
        self.list_of_repositories = []
        self.file_name = RepoPath
        self.username = Username
        self.password = Token
        self.stars = []
        self.init_star ()
        
    def init_star(self):
        End = "*"
        Beg = 25000
        while Beg >= 100:
            Star = str (Beg) + ".." + End
            self.stars.append (Star)           
            End = str (Beg-1)
            Beg = Beg - 200
        print (self.stars)

    def collect_repositories(self):
        self.list_of_repositories = self.get_repos()
        original_repo_count = len(self.list_of_repositories)
        print("%d Repositories have been read in from Github" % original_repo_count)

        self.update_repositories()      
        list_of_languages = self.update_languages()
        self.clean_repositories(list_of_languages)
        self.remove_invalid_repositories()
        final_repo_count = len(self.list_of_repositories)
        print("Valid Repositories Remaining %d of %d [%.2f%%]" % (final_repo_count, original_repo_count,
                                                                  (final_repo_count / original_repo_count) * 100))

        self.write_csv()

    def update_repositories(self, field='url', repo_num=65535):
        print("Updating Repository Data[%s]..." %field)
        pbar = ProgressBar()
        index = 0
        for repo in pbar(self.list_of_repositories):
            url = repo[field]
            result = self.http_get_call(url)
            self.list_of_repositories[index] = dict(result)
            index += 1
            if (index >= repo_num):
                break

    def update_languages(self):
        print("Updating Repository Language Data...")
        language_dict = {}
        pbar = ProgressBar()
        for repo in pbar(self.list_of_repositories):
            url = repo['languages_url']
            repo['language'] = self.http_get_call(url)
            language_dict.update(repo['language'])
        return [lang.lower() for lang in language_dict.keys()] 

    def remove_invalid_repositories(self):
        updated_repos = []
        for repo in self.list_of_repositories:
            language_count = len(repo['language_dictionary'])
            character_count = len(str(repo['description']))
            if language_count > 1 and character_count > 20:
                updated_repos.append(repo)
        self.list_of_repositories = updated_repos
        
    def dictsort_key(self, original_dict, reverse=False):
        new_dict = {}
        for key in sorted(original_dict):
            new_dict[key] = original_dict[key]
        return new_dict
        
    def clean_text(self, text):
        text = text.lower()
        text = re.sub(r'[+|/]', ' and ', text)
        text = re.sub(r'[^\w\d,]', ' ', text)
        words = text.split()
        words = [re.sub(r'[^a-z]', '', word) for word in words if word.isalnum()]
        text = ' '.join(words)
        return text

    def clean_repositories(self, langs):
        index = 0
        for repo in self.list_of_repositories:
            topics = [topic.lower() for topic in repo['topics']]
            repo['topics'] = [topic for topic in topics if topic not in langs]
            language_dictionary = {language.lower(): val for language, val in repo['language'].items()}
            repo['language_dictionary'] = self.dictsort_key(language_dictionary)
            description = str(repo['description'])
            repo['description'] = self.clean_text (description)
            repo['owner_type'] = repo['owner']['type']
            self.list_of_repositories[index] = {field: repo[field] for field in CollectRepo.Fields}
            index += 1

    def http_get_call(self, url):
        result = requests.get(url,
                              auth=(self.username, self.password),
                              headers={"Accept": "application/vnd.github.mercy-preview+json"})
        if (result.status_code != 200 and result.status_code != 422):
            print("Status Code %s: %s, URL: %s" % (result.status_code, result.reason, url))
            # Sleeps program for one hour and then makes call again when api is unrestricted
            sleep(300)
            return self.http_get_call(url)
        return result.json()

    def get_page_of_repos(self, page_num, star_count):
        url = 'https://api.github.com/search/repositories?' \
              + 'q=stars:' + star_count + '+is:public+mirror:false'
        
        url += '&sort=stars&per_page=' + str(PER_PAGE) + '&order=desc' + '&page=' + str(page_num)  # 4250
        
        if page_num == 1:
            print(url)
        return self.http_get_call(url)

    def get_repos(self):
        print("---> Obtaining Repositories from Github, PAGE_COUNT[%d]..." %(PAGE_COUNT))
    
        page_count = PAGE_COUNT+1        
        list_of_repositories = []
        for star_count in self.stars:
            for page_num in range(1, page_count, 1):
                json_repos = self.get_page_of_repos(page_num, star_count)
                if 'items' in json_repos:
                    repos = json_repos['items']
                    list_of_repositories += repos
                    if (len(repos) < PER_PAGE):
                        break
                else:
                    break
            print ("star: %s  --->  retrive repositories: %d" %(star_count, len(list_of_repositories)));
        return list_of_repositories

    def write_csv(self):
        file = self.file_name
        print("---> Writing to" + file)       
        with open(file, 'w') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(CollectRepo.Fields)
            for repository in self.list_of_repositories:
                row = []
                for field in CollectRepo.Fields:
                    row.append(repository[field])
                writer.writerow(row)
        csv_file.close()

