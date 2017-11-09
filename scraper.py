from bs4 import BeautifulSoup
import urllib2
import datetime

def seasonUrlString(year):
	return 'http://www.hockey-reference.com/leagues/NHL_{}_games.html'.format(year)

def extractRowData(row, fields):
	data = {}
	fields = row.find_all('th', recursive=False) + row.find_all('td', recursive=False)
	for field in fields:
		fieldName = field.attrs['data-stat']
		data[fieldName] = field.text
		if fieldName == 'date_game':
			link = field.find('a')
			if link is not None:
				data['boxscore_link'] = link.attrs['href']
			else:
				data['boxscore_link'] = None
	return data

def parseGamesTable(table):
	tableHeader = table.find('thead', recursive=False)
	headerRow = tableHeader.find('tr', recursive=False)
	fields = [fieldElement.attrs['data-stat'] for fieldElement in headerRow.findChildren()]
	tableBody = table.find('tbody', recursive=False)
	tableRows = tableBody.find_all('tr', recursive=False)
	games = [extractRowData(row, fields) for row in tableRows]
	return games

def getSeasonGameResults(year):
	url = seasonUrlString(year)
	html = urllib2.urlopen(url)
	soup = BeautifulSoup(html, 'html.parser')
	table = soup.find('table', attrs={'id': 'games'})
	if table is not None:
		regularGames = parseGamesTable(table)
	else:
		regularGames = []

	table = soup.find('table', attrs={'id': 'games_playoffs'})
	if table is not None:
		playoffGames = parseGamesTable(table)
	else:
		playoffGames = []

	return regularGames, playoffGames


if __name__=='__main__':
	import cPickle as pickle
	import time
	import argparse
	parser = argparse.ArgumentParser()
	parser.add_argument('--start', '-a', type=int, default=None, help='Starting season (e.g. for 2015-2016, this should be 2016)')
	parser.add_argument('--end', '-b', type=int, default=None, help='Ending season (e.g. for 2015-2016, this should be 2016), default to the current season')
	parser.add_argument('--output', default='gameData.pickle', help='Output pickle path')
	parser.add_argument('--minTime', type=float, default=1., help='Minimum time between season queries')
	args = parser.parse_args()

	if args.start is None:
		args.start = 1918

	if args.end is None:
		curDate = datetime.date.today()
		if curDate.month < 10:
			args.end = curDate.year
		else:
			args.end = curDate.year + 1

	gameData = {}
	for year in range(args.start, args.end+1):
		startTime = time.time()
		print('Getting game results for the {}-{} season'.format(year-1, year))
		regularGames, playoffGames = getSeasonGameResults(year)
		print('--> {} regular games, {} playoff games found'.format(len(regularGames), len(playoffGames)))
		if (len(regularGames) == 0) or (len(playoffGames) == 0):
			print('--> WARNING - no regular and/or playoff games found!')
		gameData[year] = {}
		gameData[year]['regular'] = regularGames
		gameData[year]['playoff'] = playoffGames

		# Enforce minimum time between calls
		elapsedTime = time.time() - startTime
		print('--> Elapsed time: {:.6f}'.format(elapsedTime))
		if elapsedTime < args.minTime:
			print('--> Enforcing min time between queries...')
			time.sleep(args.minTime - elapsedTime)

	print('\nWriting data to {}...'.format(args.output))
	with open(args.output, 'w') as f:
		pickle.dump(gameData, f)
	print('Done.')
