from discovery.constants import *
from lib.core import *
from parsers import myparser
import re
import requests
import sys
import time


class SearchGoogleCSE:

    def __init__(self, word, limit, start):
        self.word = word
        self.files = 'pdf'
        self.results = ""
        self.totalresults = ""
        self.server = 'www.googleapis.com'
        self.hostname = 'www.googleapis.com'
        self.userAgent = '(Mozilla/5.0 (Windows; U; Windows NT 6.0;en-US; rv:1.9.2) Gecko/20100115 Firefox/3.6'
        self.quantity = '10'
        self.limit = limit
        self.counter = 1
        self.api_key = Core.google_cse_key()['key']
        if self.api_key is None:
            raise MissingKey(True)
        self.cse_id = Core.google_cse_key()['id']
        if self.cse_id is None:
            raise MissingKey(False)
        self.lowRange = start
        self.highRange = start + 100

    def do_search(self):
        url = 'https://' + self.server + '/customsearch/v1?key=' + self.api_key + '&highrange=' + str(self.highRange) \
              + '&lowrange=' + str(self.lowRange) + '&cx=' + self.cse_id + '&start=' + str(self.counter) + \
              '&q=' + self.word
        headers = {
            'Host': self.server,
            'User-agent': self.userAgent
        }

        h = requests.get(url=url, headers=headers)
        self.results = h.text
        self.totalresults += self.results

    def do_search_files(self, files):
        url = 'https://' + self.server + '/customsearch/v1?key=' + self.api_key + '&highRange=' + str(self.highRange) \
              + '&lowRange=' + str(self.lowRange) + '&cx=' + self.cse_id + '&start=' + str(self.counter) + \
              '&q=filetype:' + files + '%20site:' + self.word
        headers = {
            'Host': self.server,
            'User-agent': self.userAgent
        }
        h = requests.get(url=url, headers=headers)
        self.results = h.text
        self.totalresults += self.results

    def check_next(self):
        renext = re.compile('>  Next  <')
        nextres = renext.findall(self.results)
        if nextres != []:
            nexty = '1'
        else:
            nexty = '0'
        return nexty

    def get_emails(self):
        rawres = myparser.Parser(self.totalresults, self.word)
        return rawres.emails()

    def get_hostnames(self):
        rawres = myparser.Parser(self.totalresults, self.word)
        return rawres.hostnames()

    def get_files(self):
        rawres = myparser.Parser(self.totalresults, self.word)
        return rawres.fileurls(self.files)

    def process(self):
        tracker = self.counter + self.lowRange
        while tracker <= self.limit:
            self.do_search()
            ESC = chr(27)
            sys.stdout.write(ESC + '[2K' + ESC + '[G')
            sys.stdout.write('\r\t' + 'Searching  ' + str(self.counter + self.lowRange) + ' results.')
            sys.stdout.flush()
            if self.counter == 101:
                self.counter = 1
                self.lowRange += 100
                self.highRange += 100
            else:
                self.counter += 10
            tracker = self.counter + self.lowRange

    def store_results(self):
        filename = 'debug_results.txt'
        file = open(filename, 'w')
        file.write(self.totalresults)

    def process_files(self, files):
        while self.counter <= self.limit:
            self.do_search_files(files)
            time.sleep(1)
            self.counter += 100
            print('\tSearching ' + str(self.counter) + ' results.')
