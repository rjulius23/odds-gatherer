import csv
from abc import abstractmethod

import requests
from bs4 import BeautifulSoup


class OddsGatherer(object):
    def __init__(self, **kwargs):
        self.url = kwargs.get("url", None)
        self.sitename = kwargs.get("sitename", None)
        self.sportgenre = kwargs.get("sportgenre", None)

    @abstractmethod
    def get_odds_from_site(self, **kwargs):
        pass

    def get_prettified_page(self, url_to_scrape):
        page_raw = requests.get(url_to_scrape)
        soup = BeautifulSoup(page_raw.content, 'html.parser')
        return soup.prettify()

    def generate_csv(self, odds_rows):
        filename = self.sitename + "_" + self.sportgenre + "_odds.csv"
        with open(filename, 'wb') as myfile:
            wr = csv.writer(myfile, delimiter=';', quoting=csv.QUOTE_ALL)
            for rows in odds_rows:
                wr.writerow(rows)


class OddsChecker(OddsGatherer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_odds_from_site(self, **kwargs):
        url_to_scrape = kwargs.get('url', self.url)
        if url_to_scrape:
            page = self.get_prettified_page(url_to_scrape)
        print(page)

