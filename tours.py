import sys, getopt
import getpass
import requests
import time
import lxml.html
from lxml.cssselect import CSSSelector
from collections import OrderedDict
from termcolor import colored

try:
	from html import escape  # python 3.x
except ImportError:
	from cgi import escape  # python 2.x

# Next navigation page
has_next = CSSSelector('.next')

# On Tour Label
on_tour = CSSSelector('.label')

# Band link
bands = CSSSelector('.grid-items-item-main-text > .link-block-target')

def main(argv):
	print colored('TourFinder v0.1.0 (c) singulart@i.ua', 'yellow')
	print colored('Simple utility for looking up tours of your favourite musicians', 'yellow')

	style = ''
	try:
		opts, args = getopt.getopt(argv,"hs:",["style="])
	except getopt.GetoptError:
		usage()
	for opt, arg in opts:
		if opt == '-h':
			print 'tours.py -s <last.fm style tag>'
			sys.exit()
		elif opt in ("-s", "--style"):
			style = arg

	if style == '':
		usage()

	page = 1
	proceed = True
	band_links = []
	now_on_tour = []

	print colored('Looking for %s tours...' % style, 'green')
	print colored('1. Collecting band links...', 'green')
	while proceed:
		r = requests.get('http://www.last.fm/tag/%s/artists?page=%d' % (style, page))

		# build the DOM Tree
		tree = lxml.html.fromstring(r.text)

		# Apply selectors to the DOM tree.
		band_results = bands(tree)

		band_links.extend([result.get('href') for result in band_results])
		print band_links[len(band_links) - 1]
		nextel = has_next(tree)
		if nextel:
			page += 1
		else:
			proceed = False

	print colored('2. Checking tours...', 'green')
	for href in band_links:
		r = requests.get('http://www.last.fm%s' % href)
		tree = lxml.html.fromstring(r.text)
		is_on_tour = on_tour(tree)
		if is_on_tour:
			print colored('%s is on tour' %href, 'red')
			now_on_tour.extend(href)




def usage():
	print 'tours.py -s <last.fm style tag>'
	sys.exit(2)

if __name__ == "__main__":
	main(sys.argv[1:])