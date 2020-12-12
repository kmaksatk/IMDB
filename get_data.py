#import libraries
from urllib.request import urlopen
from bs4 import BeautifulSoup
import ssl
import numpy as np
import pandas as pd
import re
import time
import urllib.parse
import socket

#ignore ssl certificates
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

#just to measure time, usually it takes about an hour
#so I suggest using the dataset provided
start = time.time()

#intialize variables; my dataset will have 11 variables
movielinks = [np.nan]*1000
movieNames = [np.nan]*1000
movieRating = [np.nan]*1000
movieLang = [np.nan]*1000
movieYear = [np.nan]*1000
movieBudget = [np.nan]*1000
movieGenre = [np.nan]*1000
movieUSBO = [np.nan]*1000
movieBO = [np.nan]*1000
movieCountry = [np.nan]*1000
movieDirector = [np.nan]*1000
movieMetaCriticScore = [np.nan]*1000

#parameters for the request that we send to http://www.suggestmemovie.com
parms = {'mood_change': 1, 'mood_year1': 1900, 'mood_year2': 2020,
	'language_criteria': 'ignore','which_language': 'English','mood_imdb_rating': 0,
	'mood_imdb_users': 0,'type_genre_selection': 'use_or','exclude_genres': 'include'}
url = 'https://www.suggestmemovie.com/'
buttonlink = urllib.parse.urlencode(parms).encode('ascii')

for i in range(0,1000):
	socket.setdefaulttimeout(3) #some pages do not proceed, this allows to skip it
	try:
		#this generates random page with a movie, 
		#randomness purely based on the back-end of the suggestmemovie website
		#I don't know how it works, except movies are indeed random
		data = urlopen(url, buttonlink, context=ctx).read() 
	except socket.timeout:
		print('ERROR: the read operation timed out\n')
		continue
	except urllib.error.URLError:
		print('ERROR: the handshake operation timed out\n')
		continue

	#next segment finds the movie name and IMDB link and then follows that link
	soup = BeautifulSoup(data, 'html.parser')
	mov_link = soup.find('ul', class_ = 'list-group list-group-flush').li.a['href']
	print('Retrieving', mov_link)
	movielinks[i] = mov_link
	name = soup.find('div', class_ = 'col text-center')
	name.h1.span.extract()
	movieNames[i] = re.sub("\n","",name.text)
	try:
		openurl = urlopen(mov_link).read()
	except socket.timeout:
		print('ERROR: the read operation timed out\n')
		continue
	except urllib.error.URLError:
		print('ERROR: the handshake operation timed out\n')
		continue
	print('...')
	#scraping necessary variables from the IMDB page of each movie
	data = BeautifulSoup(openurl, 'html.parser')
	title_year = data.find('div', class_ = 'title_wrapper')
	if title_year.h1.span.a:
		movieYear[i] = int(title_year.h1.span.a.text)
	movieRating[i] = float(data.find('span', itemprop='ratingValue').text)
	
	credits = data.findAll('div', class_ = 'credit_summary_item')
	for credit in credits:
		if credit.h4 and (credit.h4.text == 'Director:' or credit.h4.text == 'Directors:'):
			movieDirector[i] = credit.a.text
			break

	storyline = data.findAll('div', class_ = 'see-more inline canwrap')
	for genre in storyline:
		if genre.h4 and genre.h4.text == 'Genres:':
			movieGenre[i] = genre.a.text
			break

	details = data.findAll('div', class_ = 'txt-block')
	for divs in details:
		if divs.h4 and divs.h4.text == 'Language:':
			movieLang[i] = divs.a.text
		if divs.h4 and divs.h4.text == 'Country:':
			movieCountry[i] = divs.a.text
		if divs.h4 and divs.text and divs.h4.text == 'Cumulative Worldwide Gross:':
			movieBO[i] = int(re.sub(r'[^0-9]','', divs.text))
		if divs.h4 and divs.text and divs.h4.text == 'Gross USA:':
			movieUSBO[i] = int(re.sub(r'[^0-9]','', divs.text))
		if divs.h4 and divs.text and divs.h4.text == 'Budget:':
			movieBudget[i] = int(re.sub(r'[^0-9]','', divs.text))
	MCScore = data.find('div', class_ = "titleReviewBarItem")
	if MCScore.div and MCScore.div.span:
		movieMetaCriticScore[i] = MCScore.div.span.text

	#Uncomment this if you want to see the information about each movie
	#print((movieNames[i],movieYear[i],movieRating[i],movieDirector[i],movieGenre[i],
	#	movieCountry[i],movieLang[i], movieBudget[i], movieUSBO[i], movieBO[i],
	#	movieMetaCriticScore[i]))
	print('Retrieved', mov_link, '\n')

#finally implementing everything into the dataset.csv
table = {'title': movieNames, 'year': movieYear,
'director': movieDirector, 'genre': movieGenre,
'country': movieCountry, 'language': movieLang, 
'budget': movieBudget, 'US_box_office': movieUSBO, 
'box_office': movieBO, 'usr_rating': movieRating, 
'metacritic': movieMetaCriticScore}
df = pd.DataFrame(table)
df.to_csv('dataset.csv')

#time taken
end = time.time()
print('time taken: ', (end - start)/60, 'minutes')



