import csv
import re
from abc import abstractmethod

import requests
import sys
from bs4 import BeautifulSoup


class OddsGatherer(object):
    def __init__(self, **kwargs):
        self.url = kwargs.get("url", "dummy.com")
        self.sitename = kwargs.get("sitename", "dummysite")
        self.sportgenre = kwargs.get("sportgenre", "dummysport")

    @abstractmethod
    def get_odds_from_site(self, **kwargs):
        pass

    def get_prettified_page(self, url_to_scrape):
        page_raw = requests.get(url_to_scrape)
        soup = BeautifulSoup(page_raw.content, 'html.parser')
        return soup.prettify()

    def generate_csv(self, odds_rows):
        filename = self.sitename + "_" + self.sportgenre + "_odds.csv"
        with open(filename, 'w') as myfile:
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
        self.baseurl = "https://www.oddschecker.com/"
        self.subpages = {
            "nba": "basketball/nba",
            "tennis": "tennis/match-coupon"
        }
        self.pattern_dict = {
            "nba": r'basketball\/nba\/\w+-\w+-at-\w+-\w+\/winner',
            "nba_matchup": r'basketball\/nba\/(\w+-\w+-at-\w+-\w+)\/winner',
            "tennis": r'tennis\/.*\/\w+-\w+-v-\w+-\w+\/winner',
            "tennis_matchup": r'tennis\/.*\/(\w+-\w+-v-\w+-\w+)\/winner'
        }
        url = self.baseurl + self.subpages[self.sportgenre]
        self.page_content = self.get_prettified_page(url)

    def get_matchup_urls(self):
        pattern = self.pattern_dict[self.sportgenre]
        urls = [self.baseurl + x for x in self._find_pattern_on_page(pattern)]
        return urls

    def get_odds_from_site(self, **kwargs):
        best_odds = {}
        odds_rows = []
        columns = ["Match-up", "Winner", "Best Odds", "Bookies"]
        pattern = self.pattern_dict[self.sportgenre]
        if pattern:
            odds_rows.append(columns)
            if self.page_content:
                matchups = self.get_matchup_urls()
                for match_url in matchups:
                    pattern = self.pattern_dict[self.sportgenre + "_matchup"]
                    matchup_title = re.findall(pattern, match_url)
                    best_odds[matchup_title[0]] = self._get_best_odds_for_each_team(match_url)
            else:
                sys.exit(1)

            for k, v in best_odds.items():
                for team, odds_info in v.items():
                    odds_row = list()
                    # Add the match-up to the first column of the row
                    odds_row.append(k)
                    odds_row.append(team)
                    odds_row.append(odds_info["best_odds_for_win"])
                    odds_row.append(odds_info["bks"])
                    odds_rows.append(odds_row)
            self.generate_csv(odds_rows)
        else:
            raise Exception("No patterns were specified!")

    def _get_best_odds_for_each_team(self, match_url):
        best_odds_dict = {}
        pattern = r'data-best-bks=["]([a-zA-Z,0-9]*)["][ ]' \
                  r'data-best-dig=["]([0-9.]*)["][ ].*[ ]' \
                  r'data-bname=["]([a-zA-Z]*[ |/][a-zA-Z0-9]*)["]'
        matchup_content = self.get_prettified_page(match_url)
        best_odds_for_each_team = re.findall(pattern, matchup_content)
        if best_odds_for_each_team:
            print(best_odds_for_each_team)
            for odds_info in best_odds_for_each_team:
                best_odds_for_team = dict()
                best_odds_for_team["bks"] = odds_info[0]
                best_odds_for_team["best_odds_for_win"] = odds_info[1]
                best_odds_dict[odds_info[2]] = best_odds_for_team
            return best_odds_dict
        else:
            raise Exception("Could not find match odds at %s!" % match_url)


