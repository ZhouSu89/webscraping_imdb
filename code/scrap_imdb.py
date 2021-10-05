###  Webscrapping imdb top chart

from bs4 import BeautifulSoup
import requests
import re
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
import pygsheets
import imdb

# Parameters
gsheet_name = 'imdb_250'
cred_json = './input/cred/imdb-327518-343d6948717a.json'
# Downloading imdb top 250 movie's data
url = 'http://www.imdb.com/chart/top'
imdb_url ='https://www.imdb.com'

response = requests.get(url)
soup = BeautifulSoup(response.content, "html.parser")
ia = imdb.IMDb()

# # Write static htlm to a txt file
# with open("./output/imdb_source.txt", "w") as text_file:
#     text_file.write(response.content)

movies = soup.select('td.titleColumn')
links = [a.attrs.get('href') for a in soup.select('td.titleColumn a')]
crew = [a.attrs.get('title') for a in soup.select('td.titleColumn a')]

ratings = [b.attrs.get('data-value')
		for b in soup.select('td.posterColumn span[name=ir]')]

rankings = [b.attrs.get('data-value')
		for b in soup.select('td.posterColumn span[name=rk]')]

votes = [b.attrs.get('title')
		for b in soup.select('td.ratingColumn strong')]

# create a empty list for storing
# movie information
list = []

# Iterating over movies to extract
# each movie's details
for index in range(len(movies)):
	
	# Separating movie into: 'rank',
	# 'title', 'year'
	movie_string = movies[index].get_text()
	movie = (' '.join(movie_string.split()).replace('.', ''))
	movie_title = movie[len(str(index))+1:-7]
	year = re.search('\((.*?)\)', movie_string).group(1)
	# Use imdb package to get genres of each movie
	genres = ia.get_movie(ia.search_movie(movie_title)[0].movieID)['genres']
	genres = ','.join(genres)
	data = pd.DataFrame({"movie_title": movie_title,
			"year": year,
			"rank": rankings[index],
			"star_cast": crew[index],
			"rating": ratings[index],
			"vote": int(votes[index].split(' ')[3].replace(',','')),
			"link": imdb_url+links[index],
			'genres':genres}, index=[0])
	list.append(data)
	print(f"Finish processing rank {rankings[index]} movie")
df = pd.concat(list, axis=0)

# save to output
df.to_csv('./output/imdb_250.csv',header=True, index=None)

# Write to google sheet
# Following the instruction https://pygsheets.readthedocs.io/en/stable/authorization.html to authorize pygsheets
gc = pygsheets.authorize(service_file=cred_json)
sh = gc.open(gsheet_name)
wks =sh.sheet1
wks.set_dataframe(df,(1,1))