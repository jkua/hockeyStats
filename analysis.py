import cPickle as pickle
import numpy as np
import datetime
import matplotlib.pyplot as plt
import matplotlib.ticker as plticker
from matplotlib.colors import LogNorm


def analyzeScores(games):
	gameDates = []
	winningScores = []
	losingScores = []
	tieScores = []
	tieGames = []
	largestGoalDiff = 0
	largestGoalDiffGames = []
	firstOccuranceOfScore = {}
	lastOccuranceOfScore = {}

	for game in games:
		gameDates.append(game['date_game'])
		gameDate = datetime.datetime.strptime(game['date_game'], '%Y-%m-%d')
		try:
			homeScore = int(game['home_goals'])
			visitorScore = int(game['visitor_goals'])
		except ValueError:
			# print('Missing score for {} - home: {}, visitor: {}'.format(game['date_game'], game['home_goals'], game['visitor_goals']))
			continue
		winningScore = max(homeScore, visitorScore)
		losingScore = min(homeScore, visitorScore)
		score = winningScore, losingScore
		if (score not in lastOccuranceOfScore) or (gameDate > lastOccuranceOfScore[score]):
			lastOccuranceOfScore[score] = gameDate
		if (score not in firstOccuranceOfScore) or (gameDate < firstOccuranceOfScore[score]):
			firstOccuranceOfScore[score] = gameDate

		if winningScore > losingScore:
			winningScores.append(max(homeScore, visitorScore))
			losingScores.append(min(homeScore, visitorScore))
		else:
			tieScores.append(winningScore)
			tieGames.append(game)
		scoreDiff = winningScore - losingScore
		if scoreDiff > largestGoalDiff:
			largestGoalDiff = scoreDiff
			largestGoalDiffGames = [game]
		elif scoreDiff == largestGoalDiff:
			largestGoalDiffGames.append(game)

	scoreDifferential = np.array(winningScores + tieScores) - np.array(losingScores + tieScores)

	print('# games with winner: {}, # tie games: {}'.format(len(winningScores), len(tieGames)))
	print('Winning score - mean: {:.3f}, min: {}, max: {}'.format(np.mean(winningScores), np.min(winningScores), np.max(winningScores)))
	print('Losing score -  mean: {:.3f}, min: {}, max: {}'.format(np.mean(losingScores), np.min(losingScores), np.max(losingScores)))
	if len(tieScores) > 0:
		print('Tie score -     mean: {:.3f}, min: {}, max: {}'.format(np.mean(tieScores), np.min(tieScores), np.max(tieScores)))
	else:
		print('Tie score -     mean: ---, min: ---, max: ---')
	print('Goal Diff -     mean: {:.3f}, min: {}, max: {}'.format(np.mean(scoreDifferential), np.min(scoreDifferential), np.max(scoreDifferential)))
	print(' ')
	print('Largest Goal Diff Games: {}'.format(len(largestGoalDiffGames)))
	for i, game in enumerate(largestGoalDiffGames, 1):
		print('{})'.format(i))
		for key, value in game.iteritems():
			print('  {}: {}'.format(key, value))

	winningScores.extend(tieScores)
	losingScores.extend(tieScores)
	numGames = len(winningScores)

	allScores = zip(winningScores, losingScores)
	uniqueScores, scoreCounts = np.unique(allScores, return_counts=True, axis=0)
	sortIdx = np.argsort(scoreCounts)[::-1]
	uniqueScores = uniqueScores[sortIdx]
	scoreCounts = scoreCounts[sortIdx]

	print('\nOccurances of each unique score out of {} games played'.format(numGames))
	print('---------------------------------')
	for i, (score, count) in enumerate(zip(uniqueScores, scoreCounts), 1):
		percentage = float(count)/numGames*100
		score = score[0], score[1]
		firstOccuranceStr = firstOccuranceOfScore[score].strftime('%Y-%m-%d')
		lastOccuranceStr = lastOccuranceOfScore[score].strftime('%Y-%m-%d')
		lastOccuranceDaysAgo = (datetime.date.today() - lastOccuranceOfScore[score].date()).days
		# print('{:2}) {:2}-{:2}, {:4}/{} games ({:6.3f} %) - first occurance: {}, last occurance: {} ({} days ago)'.format(i, score[0], score[1], count, numGames, percentage, firstOccuranceStr, lastOccuranceStr, lastOccuranceDaysAgo))
		print('{:2}) {:2}-{:2}, {:4} games ({:6.3f} %) - last: {} ({} days ago)'.format(i, score[0], score[1], count, percentage, lastOccuranceStr, lastOccuranceDaysAgo))

	uniqueScoreDiff, scoreDiffCounts = np.unique(scoreDifferential, return_counts=True)

	print('\nOccurances of each score differential out of {} games played, sorted by differential'.format(numGames))
	print('---------------------------------')
	for i, (scoreDiff, count) in enumerate(zip(uniqueScoreDiff, scoreDiffCounts), 1):
		percentage = float(count)/numGames*100
		print('{:2}) {:2}, {:5} games ({:6.3f} %)'.format(i, scoreDiff, count, percentage))

	sortIdx = np.argsort(scoreDiffCounts)[::-1]
	uniqueScoreDiff = uniqueScoreDiff[sortIdx]
	scoreDiffCounts = scoreDiffCounts[sortIdx]

	print('\nOccurances of each score differential out of {} games played, sorted by number of occurances'.format(numGames))
	print('---------------------------------')
	for i, (scoreDiff, count) in enumerate(zip(uniqueScoreDiff, scoreDiffCounts), 1):
		percentage = float(count)/numGames*100
		print('{:2}) {:2}, {:5} games ({:6.3f} %)'.format(i, scoreDiff, count, percentage))

	return winningScores, losingScores

def formatTickLabel(value, pos):
	if value % 1 == 0:
		return ''
	return '{:d}'.format(int(np.floor(value)))

def setAxisTickLabels(ax):
	def setSubaxis(subaxis, halign=None):
		loc = plticker.MultipleLocator(base=1)
		loc2 = plticker.MultipleLocator(base=0.5)
		fmt = plticker.NullFormatter()
		fmt2 = plticker.FuncFormatter(formatTickLabel)
		subaxis.set_major_locator(loc)
		subaxis.set_minor_locator(loc2)
		subaxis.set_major_formatter(fmt)
		subaxis.set_minor_formatter(fmt2)
		for tick in subaxis.get_minor_ticks():
		    tick.tick1line.set_markersize(0)
		    tick.tick2line.set_markersize(0)
		    if halign is not None:
		    	tick.label1.set_horizontalalignment(halign)

	setSubaxis(ax.xaxis)
	setSubaxis(ax.yaxis)

def plotScoreDistribution(winningScores, losingScores, plotTitle, plotFileName, vmin=1, vmax=None, norm=None, normed=None):
	fig, ax = plt.subplots(1, figsize=(6.5,8.5))
	cmap = plt.cm.get_cmap('magma')
	cmap.set_under('w', 1)
	counts, xedges, yedges, image = ax.hist2d(losingScores, winningScores, bins=[np.arange(11), np.arange(18)], cmap=cmap, vmin=vmin, vmax=vmax, normed=normed, norm=norm)
	ax.set_title(plotTitle)
	ax.set_xlabel('Losing score')
	ax.set_ylabel('Winning score')
	ax.set_aspect('equal')
	setAxisTickLabels(ax)
	ax.grid(True)
	fig.colorbar(image)
	plt.tight_layout()
	fig.savefig(plotFileName)


if __name__=='__main__':

	f = open('gameData.pickle')
	data = pickle.load(f)	

	games = []
	for year in sorted(data.keys()):
		gameDict = data[year]
		for curGames in gameDict.itervalues():
			games.extend(curGames)

	winningScores, losingScores = analyzeScores(games)

	plotScoreDistribution(winningScores, losingScores, 'NHL Score Distribution Through 2017-11-03', 'nhlScoreDist.png')

	plotScoreDistribution(winningScores, losingScores, 'NHL Score Distribution Through 2017-11-03 (Log scale)', 'nhlScoreDist-log.png', norm=LogNorm())

	plt.close('all')

	years = []
	meanWinningScore = []
	meanLosingScore = []
	meanTotalScore = []
	meanScoreDiff = []
	gamesPlayed = []

	for year in sorted(data.keys()):
		print('\n------- {}'.format(year))
		games = []
		gameDict = data[year]
		for curGames in gameDict.itervalues():
			games.extend(curGames)

		if int(year) == 2018:
			continue

		years.append(year)

		if len(games) == 0:
			meanWinningScore.append(float('nan'))
			meanLosingScore.append(float('nan'))
			meanTotalScore.append(float('nan'))
			meanScoreDiff.append(float('nan'))
			gamesPlayed.append(0)
			continue

		winningScores, losingScores = analyzeScores(games)

		winningScores = np.array(winningScores)
		losingScores = np.array(losingScores)

		meanWinningScore.append(np.mean(winningScores))
		meanLosingScore.append(np.mean(losingScores))
		meanTotalScore.append(np.mean(winningScores + losingScores))
		meanScoreDiff.append(np.mean(winningScores - losingScores))
		gamesPlayed.append(len(winningScores))

		plotScoreDistribution(winningScores, losingScores, 'NHL Score Distribution For {}'.format(year), 'nhlScoreDist_{}.png'.format(year), vmin=1e-10, vmax=0.2, normed=True)

		plotScoreDistribution(winningScores, losingScores, 'NHL Score Distribution For {} (Log scale)'.format(year), 'nhlScoreDist-log_{}.png'.format(year), vmin=1e-3, vmax=0.2, normed=True, norm=LogNorm())

		plt.close('all')

	fig, ax = plt.subplots(4, figsize=(7, 8.5))
	ax[0].plot(years, meanWinningScore, label='Winner')
	ax[0].plot(years, meanLosingScore, label='Loser')
	ax[0].legend(loc='upper right', fancybox=True, framealpha=0.5)
	ax[0].set_title('Mean scores')
	ax[0].grid(True)

	ax[1].plot(years, meanTotalScore)
	ax[1].set_title('Mean combined score')
	ax[1].grid(True)
	
	ax[2].plot(years, meanScoreDiff)
	ax[2].set_title('Mean score differential')
	ax[2].grid(True)

	ax[3].plot(years, gamesPlayed)
	ax[3].set_title('Games played')
	ax[3].grid(True)

	fig.suptitle('NHL Scoring Trends (1918-2017)', fontsize=16)
	fig.tight_layout()
	fig.subplots_adjust(top=0.92)

	fig.savefig('plot.png')
