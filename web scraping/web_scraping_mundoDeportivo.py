# Import necessary libraries
from time import sleep
from bs4.element import NavigableString
import spacy
import requests
from bs4 import BeautifulSoup
import re
import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings('ignore')


##########################################################################################
#                               AUXILIAR FUNCTIONS                                       #
##########################################################################################
'''Auxiliar function that checks if the page exists.
  Input: soup of the web page
  Output: True if page exists, False if page does not exist'''
def page_exists(soup):
    # Checking if the page exists by finding the error message
    error_msg = soup.find_all('div', class_='error-title')
    # If the error message is found, classify the link as not valid and return False
    if error_msg:
        print("Web page does not exist: invalid link")
        return False
    return True


'''Auxiliar function that gets the article news found in the page.
  Input: soup of the web page
  Output: a list of strings containing the links of the news'''
def get_links(soup, url, section):
    links = []
    # Finding the link to each article inside the tag for each article
    if section == "opinion":
        list_news = soup.find_all('li', class_="result-opinion")
    else:
        list_news = soup.find_all('li', class_ =  "result-news")
        
    for data in list_news:
        raw_link = str(data.find('h2', class_ = 'title'))
        start = raw_link.find('label="')
        end = raw_link.find('.html')
        # from the original url we only want the "basic" url (without /futbol)
        link = url[:url.find(section)]+str(raw_link[start+8:end+5])
        links.append(link)
    return links


'''Auxiliar function that retrieves article information from a link
    Input: soup of web page, link
    Output: dictionary with the fields -> day, link, kicker, headline, standfirst, body'''
def get_article_data(soup, link, section):
    output = {'day':[],
        'link':[],
        'section': [],
        'kicker':[],
        'headline': [],
        'standfirst':[],
        'body':[]}
    x = ""

    # get whole article
    article = soup.find_all('div', class_='main-article-container')
    if article == []:
        print("empty article")
        return None
    else:
        article = article[0]

    # extract headline
    headline = article.find_all('h1', class_='title')
    if headline == []:
        print("no headline")
        output['headline'] += ['None']
    else:
        for tag in headline[0]:
            x += str(tag)
            output['headline'] += [x]

    # extract standfirst
    x = ""
    # counter
    c = 0
    standfirst = article.find_all('h2', class_='epigraph')
    if standfirst == []:
        print("no standfirst")
        output['standfirst'] += ['None']
    else:
        for tag in standfirst[0]:
            # exit loop if counter > 1, we do this to avoid duplicated standfirsts
            if c > 0:
                break
            c += 1
            if type(tag) is NavigableString:
                x += tag
            else:
                x += tag.get_text()
            output['standfirst'] += [x]

    #extract body
    x = ""
    body = article.find_all('p', class_='paragraph')
    if body == []:
        print("no body")
        output['body'] += ['None']
    else:
        for tag in body:
            if type(tag) is NavigableString:
                x += tag
            else:
                x += tag.get_text()
        output['body'] += [x]

    # extract day
    x = ""
    day = article.find_all('div', class_='date-time')
    if day == []:
        print("no day")
        output['day'] += ['None']
    else:
        day_raw = str(day[0])
        start = day_raw.find('datetime=')
        day_clean = day_raw[start+10:start+20]
        output['day'] += [day_clean]

    # link is a parameter passed to the function, already extracted
    output['link'] += [link]

    # section is passed to the function
    output['section'] += [section]

    # extract kicker
    kicker = article.find_all('h2', class_="supra-title")
    if kicker == []:
        print("no kicker")
        output['kicker'] += ['None']
    else:
        for tag in kicker[0]:
            x += str(tag)
            output['kicker'] += [x]

    return output

# Get_article_text function
# -------
# Given an url string, extract textual information regarding headline, body, kicker and stand-first.
# Returns a dictionary object with all extracted data structured accordingly.
# -------
def scraping_mundoDeportivo(url, section):
  # Send request to given url string
    try:
        res = requests.get(url, verify=False)
    except requests.exceptions.Timeout:
        print("Timeout error ocurred")
        return None
    except:
        print("error ocurred")
        return None

    # Extract content from the request
    html_page = res.content
    soup = BeautifulSoup(html_page, 'html.parser')

    # If page does not exist, return None
    if not page_exists(soup):
        print("page does not exist")
        return 0

     # Obtain links of the articles that will be extracted
    article_links = get_links(soup, url, section)

     # Prepare output structure
    output_dict = {'day':[],
          'link':[],
          'section':[],
          'kicker':[],
          'headline': [],
          'standfirst':[],
          'body':[]}
    output_df = pd.DataFrame.from_dict(output_dict)

    # For each article
    for l in article_links:
    # request access to link
        try:
            res = requests.get(l, verify=False)
        except requests.exceptions.Timeout:
            print("Timeout error ocurred")
            return None
        except:
            print("error occured")
            return None

        html_page = res.content
        # Extract HTML through parser
        soup = BeautifulSoup(html_page, 'html.parser')

        # Call function to retrieve the article
        article = get_article_data(soup, l, section)
        if article is None:
            print("no article")
            continue
        # Append all articles in the same dictionary
        for k in article.keys():
            output_dict[k].append(article[k])

    # Return output dataframe
    return pd.DataFrame.from_dict(output_dict)

##########################################################################################
#                                   MAIN PROGRAM                                         #
##########################################################################################

# get a section from this list
possible_sections = ["futbol", "baloncesto", "motor", "elotromundo", "vidae",
                    "atletismo", "rugby", "boxeo", "e-sport", "padel",
                    "waterpolo", "deportes-invierno", "ufc", "vela"]

# define section to extract data from
section = "futbol"

# empty dataframe with output structure
columns = ['day', 'link', 'kicker', 'headline', 'standfirst', 'body']

# before launching create empty dataframe
result = pd.DataFrame(columns=columns)

# name of file
NAME_FILE = "output_mundoDeportivo/"+section+"_md_02.csv"

loop = True
i = 0

for i in range(1001):
    url = "https://www.mundodeportivo.com/"+section+"/p"+str(i)
    if i==0:
        url = "https://www.mundodeportivo.com/"+section
    data = scraping_mundoDeportivo(url, section)
    if isinstance(data, int):
        print("all pages retrieved")
        loop = False
        break
    result = pd.concat([result, data], axis=0)
    print("retrieved articles from page "+str(i))
    # Save the DataFrame to a CSV file
    result.to_csv(NAME_FILE, index=False)
    # update counter
    sleep(2)


