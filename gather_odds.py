import argparse
import sys

from odds_gatherer import OddsChecker


def parse_commandline():
    usage = (
        "Usage: \n"
        "python ./{script} -S|--site <OddsChecker> -G|--genre <nba tennis>"
    ).format(script=sys.argv[0])
    parser = argparse.ArgumentParser(
            usage=usage,
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description="Best Odds collector tool!\n"
    )
    parser.add_argument('-S', "--site",
                        dest='site',
                        choices=["OddsChecker"],
                        help=argparse.SUPPRESS,
                        required=True)
    parser.add_argument('-G', "--genre",
                        dest='genre',
                        nargs="+",
                        choices=["nba", "tennis"],
                        help=argparse.SUPPRESS,
                        required=True)
    args_ret = parser.parse_args()
    return args_ret


if __name__ == "__main__":
    args = parse_commandline()
    for genre in args.genre:
        if args.site == "OddsChecker":
            oc = OddsChecker(sitename=args.site, sportgenre=genre)
            oc.get_odds_from_site()
