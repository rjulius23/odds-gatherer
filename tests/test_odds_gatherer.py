from unittest import TestCase

from odds_gatherer import OddsGatherer


class TestOddsGatherer(TestCase):

    def test_collecting_odds_from_website(self):
        og = OddsGatherer(site_name="dummy",
                          sport_genre="tennis")

        collected_odds = og.get_odds_from_site()

        self.AssertIsNotNone(collected_odds)
