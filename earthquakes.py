from datetime import datetime, timedelta
import os
import urllib

from bs4 import BeautifulSoup
from geopy import Point
from geopy.distance import vincenty
import requests

EARTHQUAKES_FEED = 'http://earthquake.usgs.gov/earthquakes'\
                   '/feed/v1.0/summary/2.5_week.atom'
IMAGEWRITER_URL = os.environ['IMAGEWRITER_URL']
HOME = Point(os.environ['HOME_LAT'], os.environ['HOME_LON'])


def get_feed():
    res = requests.get(EARTHQUAKES_FEED)
    soup = BeautifulSoup(res.content)
    return soup.find_all('entry')


def get_datetime(entry):
    updated = entry.find('updated').text
    return datetime.strptime(updated, '%Y-%m-%dT%H:%M:%S.%fZ')


def check_earthquakes(min_offset=5, distance_cutoff=200):
    earthquakes = get_feed()
    time_offset = datetime.utcnow() - timedelta(minutes=min_offset)

    print 'number of earthquakes: %s' % (len(earthquakes), )
    for quake in reversed(earthquakes):
        then = get_datetime(quake)
        print then
        if then > time_offset:
            point = quake.find('georss:point').text
            lat, lon = [float(_) for _ in point.split(' ')]
            quake_point = Point(lat, lon)

            distance = vincenty(quake_point, HOME).miles

            if distance <= distance_cutoff:
                title = quake.find('title').text
                text = '%s (%s)\n' \
                       '-------------------------------%s' % (
                           title,
                           point,
                           then
                       )

                print text
                requests.get('%s%s' % (
                    IMAGEWRITER_URL,
                    urllib.quote(text)
                ))

if __name__ == '__main__':
    check_earthquakes()
