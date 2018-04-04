import csv
import re
from abc import abstractmethod

import requests
import sys
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

    def _find_pattern_on_page(self, pattern):
        matches = re.findall(pattern, self.page_content)
        if matches:
            return matches
        else:
            raise Exception("Could not find any matchups in the page! Wrong URL maybe?")


class OddsChecker(OddsGatherer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.page_content = self.get_prettified_page(self.url)
        self.baseurl = "https://www.oddschecker.com/"

    def get_matchup_urls(self, content):
        pattern = r'basketball\/nba\/\w+-\w+-at-\w+-\w+\/winner'
        urls = [self.baseurl + x for x in self._find_pattern_on_page(pattern)]
        return urls

    def get_odds_from_site(self, **kwargs):
        best_odds = {}
        if self.page_content:
            matchups = self.get_matchup_urls(self.page_content)
            for match_url in matchups:
                pattern = r'basketball\/nba\/(\w+-\w+-at-\w+-\w+)\/winner'
                matchup_title = re.findall(pattern, match_url)
                best_odds[matchup_title[0]] = self._get_best_odds_for_each_team(match_url)
        else:
            sys.exit(1)
        print(best_odds)
        for k, v in best_odds.items():
            print(k)
            for team, odds_info in v.items():
                print("Team: %s" % team)
                print("---> best odds for win: %s" % odds_info["best_odds_for_win"])
                print("---> bookies with best odds: %s" % odds_info["bks"])

    def _get_best_odds_for_each_team(self, match_url):
        best_odds_dict = {}
        pattern = r'data-best-bks=["]([a-zA-Z,0-9]*)["][ ]' \
                  r'data-best-dig=["]([0-9.]*)["][ ].*[ ]' \
                  r'data-bname=["]([a-zA-Z]*[ ][a-zA-Z0-9]*)["]'
        matchup_content = self.get_prettified_page(match_url)
        best_odds_for_each_team = re.findall(pattern, matchup_content)
        if best_odds_for_each_team:
            print(best_odds_for_each_team)
            for odds_info in best_odds_for_each_team:
                best_odds_for_team = {}
                best_odds_for_team["bks"] = odds_info[0]
                best_odds_for_team["best_odds_for_win"] = odds_info[1]
                best_odds_dict[odds_info[2]] = best_odds_for_team
            return best_odds_dict
        else:
            raise Exception("Could not find match odds at %s!" % match_url)


