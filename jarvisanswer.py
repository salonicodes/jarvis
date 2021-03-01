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
from nltk.stem import WordNetLemmatizer
warnings.filterwarnings('ignore')

from fake_useragent import UserAgent

remove_punct_dict = dict((ord(punct), None) for punct in string.punctuation)

# For Keyword Matching
GREETING_INPUTS = ("hello", "hi", "greetings", "sup", "what's up","hey",)
GREETING_RESPONSES = ["hi", "hey", "*nods*", "hi there", "hello", "I am glad! You are talking to me"]

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



def tokenise(raw):
    #Tokenisation
    sent_tokens = nltk.sent_tokenize(raw)# converts to list of sentences 
    #print(sent_tokens)
    word_tokens = nltk.word_tokenize(raw)# converts to list of words
    return sent_tokens

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



# for greeting the user
def greeting(query):
    """If user's input is a greeting, return a greeting response"""
    for word in query.split():
        if word.lower() in GREETING_INPUTS:
            return random.choice(GREETING_RESPONSES)
        
# for saying bye and ending the program
def byee():
    return"Bye! take care.."

#for setting flag to true and introduction
def introduce():
    #as we are taking a variable flag (true until user keeps asking questions)
    #print("Hi! My name is Jarvis. I will answer all your queries. If you want to exit, type something like 'Bye' !")
    return True


def finalAns(query):
    #Jarvis introduces itself
    flag=introduce()
    i=0
    #taking user question
    query=query.lower()
    
    if('bye' not in query.split(' ')):
        if(query=='thanks' or query=='thank you' ):
            flag=False
            return "You are welcome.."
        else:
            if(greeting(query)!=None):
                return greeting(query)
            else:
                result=webpageextraction(query)
                raw=''
                while((not raw.strip()) or (('access' in raw.lower()) and ('denied' in raw.lower()))):
                    raw=snippetextraction(result,i)
                    if raw=='error604':
                        break
                    i+=1
                if raw=='error604':
                    return "Sorry I couldn't find an answer."
                if raw:
                    sent_tokens=tokenise(raw)
                else:
                    return "Sorry I couldn't find an answer."
                answer=response(query,sent_tokens)
                if answer=='error502':
                    return "Faced an Error"
                return answer
                
                
                '''#now checking satisfaction
                satisfied=False
                while(not satisfied):
                    print('Are you satisfied by my answer? Enter "yes" or "no".')
                    if (input().lower()=='yes'):
                        break
                    else:
                        i+=1
                        raw=snippetextraction(result,i)
                        while((not raw.strip()) or (('access' in raw.lower()) and ('denied' in raw.lower()))):
                            raw=snippetextraction(result,i)
                            i+=1
                        if raw=='error604':
                            print('Sorry, I am out of answers now.')
                            print("Anything else you would like to ask?")
                            break
                        if raw:
                            sent_tokens=tokenise(raw)
                        else:
                            print("Sorry I couldn't find an answer.")
                        print(response(query,sent_tokens)+'\n'+result[i])
                        
                    
                sent_tokens.remove(query)'''
                
    elif ('bye' in query.split(' ')):
        flag=False
        byee()
