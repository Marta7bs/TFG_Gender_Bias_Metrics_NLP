# Import necessary libraries
from bs4.element import NavigableString
import spacy
import requests
from bs4 import BeautifulSoup
import re
import numpy as np
import pandas as pd
from time import sleep

import warnings
warnings.filterwarnings('ignore')

# Get_article_text function
# -------
# Given an url string and a day string, extract textual information regarding headline, body, kicker and stand-first.
# Returns a dictionary object with all extracted data structured accordingly.
# -------
def get_article_text(url, day_str):
    # Send request to given url string
    try:
      res = requests.get(url, verify=False)
    except:
      print("An error ocurred")
      return None

    # Extract content from the request
    html_page = res.content
    # Use library BeautifulSoup to parse the HTML content
    soup = BeautifulSoup(html_page, 'html.parser')

    # Checking if the page exists by finding the error message in the title
    text = soup.find('title')
    errormessage = 'Página no encontrada o de acceso restringido'
    # If the error message is found we classify the link as not valid and return None
    if errormessage in text:
        return None

    # Finding the link to each article inside the tag for each article
    text = soup.find_all(class_ =  "content-item")
    links = []
    for tag in text[0:-1]:
        t = str(tag)
        # Locate start and end references that define the html string
        start = t.find('<a href=')
        end = t.find('.html')
        # Extract html string
        link = t[start+9:end+5]
        # Append to list of links
        links.append(link)

    output = {'day':[],
            'link':[],
            'kicker':[],
            'headline': [],
            'standfirst':[],
            'body':[]}

    # Extracting text of each article and storing not valid links
    notincluded = []
    for l in links:
        # Safety check
        # If string is not valid, skip to next one
        if len(l) == 0:
            continue
        # Request content to link
        try:
          res = requests.get(l, verify=False)
        except:
          print("An error ocurred")
          return None
        html_page = res.content
        # Extract HTML through parser
        soup = BeautifulSoup(html_page, 'html.parser')

        # HEADLINE EXTRACTTION
        # Create empty string to store text
        x = ''
        # Find headline section through possible tag class names
        text =  soup.find(class_ =  ["ue-c-article__headline js-headline js-headlineb",
                                    'ue-c-article__headline js-headline js-headlineb ue-c-article__headline--opinion',
                                     'entry-hero'])
        # If there is not a match, it is not considered a news article, so we add it to non valid links and move
        # to the next one
        if text is None:
            notincluded.append(l)
            continue
        # If there is a match, append text to empty string and store correspondly
        for tag in text:
            x += str(tag)
        output['headline'] += [x]

        # STANDFIRST EXTRACTION
        # Find standfirst section through class name
        text =  soup.find(class_ =  "ue-c-article__standfirst")
        # Empty string to store text
        x = ''
        # If there exists a stand-first
        if text:
            # Add textual information to empty string
            for tag in text:
                x += str(tag)
            # Add to output dictionary
            output['standfirst'] += [x]
        # If there is no stand-first we label it
        else:
            # Add to output dictionary
            output['standfirst'] += ['no standfirst']

        # BODY EXTRACTION
        # If there exists a body section with the tag below
        if soup.find(class_ =  "ue-c-article__body"):
            # Extract information from section
            text = soup.find(class_ =  "ue-c-article__body")
            # Create empty string
            x = ''
            # For each piece of text check type of data and extract text accordingly
            for tag in text:
                if type(tag) is NavigableString:
                    x += tag
                else:
                    x += tag.get_text()
        # If the above tag does not exist, it corresponds to the other tag name
        else:
            # Extract information from section
            text = soup.find(class_ =  "entry-content")
            # Create empty string
            x = ''
            # For each piece of text extract piece of text from HTML text tags
            for tag in text:
                if '<p>' in str(tag):
                    x += tag.get_text()

        # Add to output dictionary
        output['body'] += [x]

        # KICKER EXTRACTION
        # Create safety check to make sure we always add a value to the output dictionary
        is_kicker = False
        # If not found with first tag, it corresponds to second tag
        if soup.find(class_ =  ['ue-c-article__kicker-seo']) is None:
            # Extract information from section
            text = soup.find(class_ =  ['ue-c-article__kicker'])
            # If there is no text, no kicker
            if text is None:
                output['kicker'] += ['no kicker']
                is_kicker = True
            # If there is a kicker, we extract its text
            else:
                for tag in text:
                    output['kicker'] += [str(tag)]
                    is_kicker = True
        # Find information in first tag
        else:
            # Extract information from section
            text = soup.find(class_ =  ['ue-c-article__kicker-seo'])
            # If there is no text, no kicker
            if text is None:
                output['kicker'] += ['no kicker']
                is_kicker=True
                # If there is a kicker, we extract its text
            else:
                for tag in text:
                    output['kicker'] += [str(tag)]
                    is_kicker=True
        # If not kicker found in both tags, no kicker label
        if not is_kicker:
            output['kicker'] += ['no kicker']

        # Add to output dictionary the link and string of the corresponding day
        output['link'] += [l]
        output['day'] += [day_str]

    # Return output dictionary
    return output


# Create dictionary with all year days

year2022 = {'10':list(np.arange(1,32)),
            '11':list(np.arange(1,31)),
            '12':list(np.arange(1,32))}


NAME_FILE = "output_marca/marca_04.csv"
# Create empty pandas dataframe with corresponding column names for each section
df2023 = pd.DataFrame(columns = ['day','link','kicker','headline','standfirst','body'])

# For each month of the year
for month in year2022.keys():
    # For each day of the month
    for day in year2022[month]:
        # Create day string
        d = str(day)
        # If it is a 1 digit day number we append a 0 before
        if len(d) == 1:
            d = '0' + d
        # For each possible tab of news articles
        for n in range(1,7):
            # For the first tab, the link only ends with 'noticias.html'
            if n == 1:
                url = 'https://www.marca.com/hemeroteca/2022/' + str(month) + '/' + str(d) + '/noticias.html'
            # For the next tabs, the link ends with 'noticias' plus the tab number
            else:
                url = 'https://www.marca.com/hemeroteca/2022/' + str(month) + '/' +str(d) + '/noticias'+ str(n) + '.html'
            # Construct full day string
            day_str = '2022/' + str(month) + '/' + str(d)
            # Call text scraping function
            news = get_article_text(url, day_str)
            # If link is not valid, move to the next one
            if news is None:
                continue
            # If link is valid
            else:
                # Create dataframe from output dictionary and append to total dataframe
                df = pd.DataFrame.from_dict(news)
                df2023 = pd.concat([df2023, df])
                df2023.to_csv(NAME_FILE, index=False)
            sleep(2)
        print(day_str)

