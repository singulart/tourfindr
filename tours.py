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
	free_stuff = []

	print colored('Looking for %s tours...' % style, 'green')


def usage():
	print 'tours.py -s <last.fm style tag>'
	sys.exit(2)

if __name__ == "__main__":
	main(sys.argv[1:])