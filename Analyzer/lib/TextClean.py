#!/usr/bin/python
import nltk
nltk.download('stopwords');nltk.download('brown');nltk.download('punkt');nltk.download('wordnet')
from nltk.corpus import stopwords

from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()

import time
import pandas as pd
import numpy as np
import re


class TextClean():
    def __init__(self):
        pass 

    def CleanText(self, Text):
        Text = str (Text)
        Text = re.sub(r'[+|/]', ' and ', Text)
        Text = re.sub(r'[^\w\d,]', ' ', Text)
        Text = Text.lower()
        words = Text.split()
        words = [re.sub(r'[^a-z]', '', word) for word in words if word.isalnum()]
        Text = ' '.join(words)
        return Text      
        
    def Cleaning(self, Text, min_len=4):
        Text = self.CleanText (Text)       
        words = nltk.word_tokenize(Text)
        words = [lemmatizer.lemmatize(word) for word in words]
        words = [word for word in words if word not in stopwords.words('english') and len(word) > min_len]
        return words
