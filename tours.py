import sys, getopt
import requests
import lxml.html
import json
from urllib import unquote
from datetime import date
from datetime import datetime
from dateutil.relativedelta import relativedelta
from lxml.cssselect import CSSSelector
from termcolor import colored
from math import cos, asin, sqrt

# On Tour Label
on_tour = CSSSelector('.label')

# Band link
bands = CSSSelector('.grid-items-item-main-text > .link-block-target')

# Concert City
cities_css = CSSSelector('.events-list-item-venue--city')

# Concert Country
countries_css = CSSSelector('.events-list-item-venue--country')

# Concert Dates xpath. Only select dates which have a specific city set
date_xpath = """//*[@class='events-list']/tbody/
tr[td[@class='events-list-item-venue']/div]
/td[@class = 'events-list-item-art']/time"""

# Next navigation page
has_next = CSSSelector('.next')

api_key = ''
my_lat = 50.4501
my_lng = 30.5234
radius_km = 2000
months_advance = 3


def main(argv):
	print colored('TourFinder v0.1.0 (c) singulart@i.ua', 'yellow')
	print colored('Simple utility for looking up tours of your favourite musicians', 'yellow')

	style = ''
	try:
		opts, args = getopt.getopt(argv, "hs:", ["style="])
	except getopt.GetoptError:
		usage()

	try:
		with open(".google-api-key", "r") as myfile:
			api_key = myfile.read()
			print api_key
	except:
		print colored('Unable to load Google API Key', 'red')

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
			print colored('%s is on tour' % unquote(href.replace('/music/', '')), 'green')
			now_on_tour.extend(href)
			r = requests.get('http://www.last.fm%s/+events' % href)
			tree = lxml.html.fromstring(r.text)
			cities_results = cities_css(tree)
			countries_results = countries_css(tree)
			dates_results = tree.xpath(date_xpath)
			if cities_css and countries_css:
				for d in range(0, len(dates_results)):
					advance_period = date.today() + relativedelta(months =+ months_advance)
					concert_date = datetime.strptime(dates_results[d].attrib['datetime'], '%Y-%m-%dT00:00:00').date()
					if concert_date > advance_period:
						# Access to Google API to get the coordinates of the city
						city_coords = json.loads(requests.get(
							"https://maps.googleapis.com/maps/api/geocode/json?address=%s,%s&key=%s" % (
							cities_results[d].text, countries_results[d].text, api_key)).text)
						city_lat = city_coords['results'][0]['geometry']['location']['lat']
						city_lng = city_coords['results'][0]['geometry']['location']['lng']

						# Filter by desired radius (in kilometres)
						if distance(my_lat, my_lng, city_lat, city_lng) < radius_km:
							print ' %s in %s, %s (%s, %s)' % (
							dates_results[d].attrib['datetime'], cities_results[d].text, countries_results[d].text,
							city_lat, city_lng)


def distance(lat1, lon1, lat2, lon2):
	p = 0.017453292519943295
	a = 0.5 - cos((lat2 - lat1) * p) / 2 + cos(lat1 * p) * cos(lat2 * p) * (1 - cos((lon2 - lon1) * p)) / 2
	return 12742 * asin(sqrt(a))


def usage():
	print 'python tours.py -s <last.fm style tag>'
	sys.exit(2)


if __name__ == "__main__":
	main(sys.argv[1:])
