import csv
from abc import abstractmethod


class OddsGatherer(object):
    def __init__(self, **kwargs):
        self.sitename = kwargs.get("site_name", None)
        self.sportgenre = kwargs.get("sport_genre", None)

    @abstractmethod
    def get_odds_from_site(self, **kwargs):
        pass

    def generate_csv(self, odds_rows):
        filename = self.sitename + "_" + self.sportgenre + "_odds.csv"
        with open(filename, 'wb') as myfile:
            wr = csv.writer(myfile, delimiter=';', quoting=csv.QUOTE_ALL)
            for rows in odds_rows:
                wr.writerow(rows)
