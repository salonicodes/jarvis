import sys
from flask import Flask, render_template, request, redirect, Response, jsonify
import random, json
from flask_wtf.csrf import CSRFProtect

import os
SECRET_KEY = os.urandom(32)


app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
csrf = CSRFProtect(app)
csrf.init_app(app)

@app.route("/")
def home():
  return render_template("home.html")

#for webpage and snippet extraction
import urllib
import requests
from bs4 import BeautifulSoup
from requests import get
import re
import collections
import pandas as pd
import matplotlib.pyplot as plt
import nltk
#nltk.download('stopwords')
from nltk.corpus import stopwords

#for answer filtering
import io
import random
import string # to process standard python strings
import warnings
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import warnings
warnings.filterwarnings('ignore')
from nltk.stem import WordNetLemmatizer
# nltk.download('popular', quiet=True)
nltk.download('punkt')
nltk.download('wordnet')

from fake_useragent import UserAgent

from flask_wtf.csrf import CsrfProtect

remove_punct_dict = dict((ord(punct), None) for punct in string.punctuation)

import jarvisanswer


# For Keyword Matching
GREETING_INPUTS = ("hello", "hi", "greetings", "sup", "what's up","hey",)
GREETING_RESPONSES = ["hi", "hey", "*nods*", "hi there", "hello", "I am glad! You are talking to me"]

#web page extraction
def webpageextraction(query):
  ua = UserAgent()

  google_url = "https://www.google.com/search?q=" + query #+ "&num=" + str(number_result)
  response = requests.get(google_url, {"User-Agent": ua.random})
  soup = BeautifulSoup(response.text, "html.parser")

  result_div = soup.find_all('div', attrs = {'class': 'ZINbbc'})

  links = []
  titles = []
  descriptions = []
  for r in result_div:
      # Checks if each element is present, else, raise exception
      try:
          link = r.find('a', href = True)
          title = r.find('div', attrs={'class':'vvjwJb'}).get_text()
          description = r.find('div', attrs={'class':'s3v9rd'}).get_text()

          # Check to make sure everything is present before appending
          if link != '' and title != '' and description != '': 
              links.append(link['href'])
              titles.append(title)
              descriptions.append(description)
      # Next loop if one element is not present
      except:
          continue
  to_remove = []
  clean_links = []
  for i, l in enumerate(links):
      clean = re.search('\/url\?q\=(.*)\&sa',l)

      # Anything that doesn't fit the above pattern will be removed
      if clean is None:
          to_remove.append(i)
          continue
      if "youtube.com" not in clean.group(1):
          clean_links.append(clean.group(1))

  # Remove the corresponding titles & descriptions
  for x in to_remove:
      del titles[x]
      del descriptions[x]
  return clean_links


#snippet extraction
def snippetextraction(results,i):
  # Snippet Extraction from the obtained web page urls
  try:
      raw = get(results[i]).text ###this is how we can extract raw html from web pages
  except:
      return 'error604'
  html = requests.get(results[i]).content
  #1 Recoding
  unicode_str = html.decode("utf8")
  encoded_str = unicode_str.encode("ascii",'ignore')
  news_soup = BeautifulSoup(encoded_str, "html.parser")
  a_text = news_soup.find_all('p')
  #2 Removing
  y=[re.sub(r'<.+?>',r'',str(a)) for a in a_text]
  y=[x.replace('\n','') for x in y]
  y=[x.strip() for x in y]
  y=' '.join(y)
  return y

#tokenise
def tokenise(raw):
  #Tokenisation
  sent_tokens = nltk.sent_tokenize(raw)# converts to list of sentences 
  #print(sent_tokens)
  word_tokens = nltk.word_tokenize(raw)# converts to list of words
  return sent_tokens

#preprocessing
def LemTokens(tokens):
  lemmer = WordNetLemmatizer()
  return [lemmer.lemmatize(token) for token in tokens]
remove_punct_dict = dict((ord(punct), None) for punct in string.punctuation)
def LemNormalize(text):
  return LemTokens(nltk.word_tokenize(text.lower().translate(remove_punct_dict)))


def response(query,sent_tokens):
  robo_response=''
  sent_tokens.append(query)
  TfidfVec = TfidfVectorizer(tokenizer=LemNormalize, stop_words='english')
  tfidf = TfidfVec.fit_transform(sent_tokens)
  vals = cosine_similarity(tfidf[-1], tfidf)
  idx=vals.argsort()[0][-2]
  flat = vals.flatten()
  flat.sort()
  req_tfidf = flat[-2]
  if(req_tfidf==0):
      robo_response=robo_response+"I am sorry! I don't understand you"
      print(robo_response)
      return 'error502'
  else:
      robo_response = robo_response+sent_tokens[idx]
      return robo_response



def introduce():
  return True



import json
@app.route('/answer')
def table():
  _result = json.loads(request.args.get('uque'))
  print(_result[0])
  fans=jarvisanswer.finalAns(_result[0])
  #return jsonify(_result)
  print(fans)
  return jsonify([fans])
    

def finalAnswer(query):
  #Jarvis introduces itself
  flag=introduce()
  #User introduces

  while(flag==True):
      i=0
      #taking user question
      query=query.lower()

      result=webpageextraction(query)
      raw=''
      while((not raw.strip()) or (('access' in raw.lower()) and ('denied' in raw.lower()))):
          raw=snippetextraction(result,i)
          if raw=='error604':
              break
          i+=1
      if raw=='error604':
          return "Sorry I couldn't find an answer."
          continue
      if raw:
          sent_tokens=tokenise(raw)
      else:
          return "Sorry I couldn't find an answer."
      answer=response(query,sent_tokens)
      if answer=='error502':
          continue
      return answer








if __name__ == "__main__":
  app.run(host="localhost", port=4000, debug=True)