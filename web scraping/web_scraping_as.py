# Import necessary libraries
from bs4.element import NavigableString
import spacy
import requests
from bs4 import BeautifulSoup
import re
import numpy as np
import pandas as pd
import warnings
from IPython.display import display
warnings.filterwarnings('ignore')

##########################################################################################
#                               AUXILIAR FUNCTIONS                                       #
##########################################################################################
'''Auxiliar function that checks if the page exists.
  Input: soup of the web page
  Output: True if page exists, False if page does not exist'''
def page_exists(soup):
    # Checking if the page exists by finding the error message
    error_msg = soup.find_all('header', class_='static-404__hdr')
    # If the error message is found, classify the link as not valid and return False
    if error_msg:
      print("Web page does not exist: invalid link")
      return False
    return True


'''Auxiliar function that gets the article news found in the page.
  Input: soup of the web page
  Output: a list of strings containing the links of the news'''
def get_links(soup):
  links = []
  # Finding the link to each article inside the tag for each article
  list_news = soup.find_all('h2', class_ =  "s__tl")
  for data in list_news:
    links.append(str((data.find('a')['href'])))
  return links

'''Auxiliar function that retrieves article information from a link
    Input: soup of web page, link
    Output: dictionary with the fields -> day, link, kicker, headline, standfirst, body'''
def get_article_data(soup, link, section):
  output = {'day':[],
        'link':[],
        'section':[],
        'kicker':[],
        'headline': [],
        'standfirst':[],
        'body':[]}
  x = ""

  # get whole article
  article = soup.find(class_=['art ct', 'img-tres-col', 'art art--op ct', 'container content'])
  if article is None:
    print("no article "+url)
    return None

  # extract headline
  headline = article.find( class_= ['art__hdl__tl', 'art-headline', 'titular-articulo'])
  if headline is None:
    output['headline'] += ['None']
  else:
    for tag in headline:
      x += str(tag)
      output['headline'] += [x]

  # extract standfirst
  x = ""
  # counter
  c = 0
  standfirst = article.find(class_= ['art__hdl__opn', 'art-opening', 'cont-entradilla-art'])
  if standfirst is None:
    output['standfirst'] += ['None']
  else:
    for tag in standfirst:
      # exit loop if counter > 1, we do this to avoid duplicated standfirsts
      if c > 0:
        break
      c += 1
      if type(tag) is NavigableString:
        x += tag
      else:
          x += tag.get_text()
      output['standfirst'] += [x]

  # extract day
  day = 'None'
  day_raw = article.find('time')
  if day_raw is not None:
    try:
      day = day_raw['datetime']
    except:
      day = 'None'
  output['day'] = [day]

  # extract kicker
  x = ""
  kicker = article.find(class_= ['ki', 'art-kicker', 'subtit-art'])
  if kicker is None:
    output['kicker'] += ['None']
  else:
    for tag in kicker:
      if type(tag) is NavigableString:
          x += tag
      else:
          x += tag.get_text()
    output['kicker'] += [x]

  #extract body
  x = ""
  body = article.find(class_= ['art__bo is-unfolded', 'int-articulo'])
  if body is None:
    output['body'] += ['None']
  else:
    for tag in body:
      if type(tag) is NavigableString:
          x += tag
      else:
          x += tag.get_text()
    output['body'] += [x]

  # link & section are a parameter passed to the function, already extracted
  output['link'] += [link]
  output['section'] += [section]

  return output

'''scraping_as function
Given an url string, extracts all links containing articles from it.
For each link, extracts textual information regarding headline, body, kicker and stand-first.
Returns a dataframe with all extracted data from the articlesstructured accordingly.'''
def scraping_as(url, section):
  # Send request to given url string
  try:
    res = requests.get(url, allow_redirects=True, verify=False)
  except:
    print("Timeout error ocurred")
    return None
  
  # Extract content from the request
  html_page = res.content
  soup = BeautifulSoup(html_page, 'html.parser')

  # If page does not exist, return None
  if not page_exists(soup):
    print("page does not exist: "+url)
    return 0
  
  # Obtain links of the articles that will be extracted
  article_links = get_links(soup)

  # Prepare output structure
  output_dict = {'day':[],
          'link':[],
          'section':[],
          'kicker':[],
          'headline': [],
          'standfirst':[],
          'body':[]}

  # For each article
  for l in article_links:
    # request access to link
    try:
      res = requests.get(l, allow_redirects=True, verify=False)
    except requests.exceptions.Timeout:
      print("Timeout error ocurred")
      return None
    except requests.exceptions.TooManyRedirects:
      print("Exceeded 30 redirects")
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
      print("empty article "+l)
      continue
    # Append all articles in the same dictionary
    for k in article.keys():
      output_dict[k].append(article[k])

  # Return output dataframe
  return pd.DataFrame.from_dict(output_dict)

##########################################################################################
#                                   MAIN PROGRAM                                         #
##########################################################################################

columns = ['day', 'link', 'section', 'kicker', 'headline', 'standfirst', 'body']

'''
possible_sections = ["futbol", "baloncesto", "tenis","motociclismo", "formula-1",
                     "balonmano", "ciclismo", "futbol-sala", "atletismo",
                     "golf", "boxeo", "rugby", "natacion", "vela", "esqui", "padel", "surf",
                     "politica", "economia", "sociedad", "ciencia"]'''


sections=["sociedad", "ciencia"]

for section in sections:
  result = pd.DataFrame(columns=columns)
  url_basic = "https://as.com/noticias/"+section
  name_file = "output_as/"+section+"_as_final_03.csv"
  if section == "sociedad":
    for i in range(400):
      if i == 0:
        url = url_basic
      if i != 0:
        url = url_basic+"/"+str(i)
      data = scraping_as(url, section)
      if isinstance(data, int):
        print("all pages retrieved")
        break
      else:
        result = pd.concat([result, data], axis=0)
        print("retrieved articles from page "+str(i))
        # write data to csv file
        result.to_csv(name_file)
  else:
    for i in range(400):
      if i == 0:
        url = url_basic
      if i != 0:
        url = url_basic+"/"+str(i)
      data = scraping_as(url, section)
      if isinstance(data, int):
        print("all pages retrieved")
        break
      else:
        result = pd.concat([result, data], axis=0)
        print("retrieved articles from page "+str(i))
        # write data to csv file
        result.to_csv(name_file)
    
display(result)