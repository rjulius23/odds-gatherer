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
        self.page_content = ""

    @abstractmethod
    def get_odds_from_site(self, **kwargs):
        pass

    @staticmethod
    def get_prettified_page(url_to_scrape):
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
        # TODO: Bookies should not be hardcoded, but stored in a dict or list!!
        columns = ["Match-up", "Winner", "bet365", "WilliamHill"]
        pattern = self.pattern_dict[self.sportgenre]
        if pattern:
            odds_rows.append(columns)
            if self.page_content:
                matchups = self.get_matchup_urls()
                for match_url in matchups:
                    pattern = self.pattern_dict[self.sportgenre + "_matchup"]
                    matchup_title = re.findall(pattern, match_url)
                    odds_for_match = self._get_best_odds_for_each_team(match_url)
                    if odds_for_match is not None:
                        best_odds[matchup_title[0]] = odds_for_match
            else:
                sys.exit(1)

            for k, v in best_odds.items():
                for team, odds_info in v.items():
                    odds_row = list()
                    # Add the match-up to the first column of the row
                    odds_row.append(k)
                    odds_row.append(team)
                    odds_row.append(odds_info["bet365"])
                    odds_row.append(odds_info["WilliamHill"])
                    odds_rows.append(odds_row)
            self.generate_csv(odds_rows)
        else:
            raise Exception("No patterns were specified!")

    def _get_best_odds_for_each_team(self, match_url):
        best_odds_dict = {}
        matchup_content = self.get_prettified_page(match_url)
        bookies_dict = self._get_bookies_dict(matchup_content)
        try:
            matchup_info = self._get_matchup_info(matchup_content)
        except Exception as e:
            print(match_url)
            raise e
        for winner in matchup_info:
            winner_odds = self._get_odds_for_winner(winner, matchup_content)
            try:
               bet_365_odds = winner_odds[bookies_dict['B3']]
               wh_odds = winner_odds[bookies_dict['WH']]
               if "0" not in bet_365_odds and "0" not in wh_odds:
                  best_odds_dict[winner] = {
                           "bet365": bet_365_odds,
                           "WilliamHill": wh_odds
                  }
            except IndexError as e:
                print(winner)
                print(winner_odds)
                print(bookies_dict)
                raise e
        return best_odds_dict

    @staticmethod
    def _get_matchup_info(content):
        pattern = r'data-name="([A-Z][A-Za-z0-9-]*[/| ][A-Z][A-Za-z0-9-]*)"'
        matchup_parties = re.findall(pattern, content, re.S | re.M)
        if matchup_parties:
            return set(matchup_parties)
        else:
            raise Exception("Could not find matchup opponents!")

    @staticmethod
    def _get_bookies_dict(content):
        pattern = r'<td class="bookie-area no-grad bg([A-Z0-9]{2})'
        bookies = re.findall(pattern, content, re.S | re.M)
        if bookies:
            bookies_dict = {bookie: bookies.index(bookie) for bookie in bookies}
            return bookies_dict
        else:
            raise Exception("No bookies were found!")

    @staticmethod
    def _get_odds_for_winner(winner, content):
        pattern = (
               r'<tr class="diff-row evTabRow bc".*?data-bname="' + winner + r'"'
               '.*?'
               '</tr>'
               )
    
        filtered = re.findall(pattern, content, re.S | re.M)
        if filtered:
            filtered_content = filtered[0]
            pattern = r'<td class=".*?data-odig="([0-9]+\.*[0-9]*)".*?</td>'
            odds = re.findall(pattern, filtered_content, re.S | re.M)
            if odds:
                return odds
