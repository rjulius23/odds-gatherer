import argparse
import sys

from odds_gatherer import OddsChecker


def parse_commandline():
    usage = (
        "Usage: \n"
        "python ./{script} -U|--url <url> -S|--site <sitename>"
    ).format(script=sys.argv[0])
    parser = argparse.ArgumentParser(
            usage=usage,
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description="CLI Tool to Create and Query Jenkins CQ runs\n"
    )
    parser.add_argument('-U', "--url", dest='url',
                        help=argparse.SUPPRESS, required=True)
    parser.add_argument('-S', "--site", dest='site',
                        help=argparse.SUPPRESS, required=True)
    args_ret = parser.parse_args()
    return args_ret


if __name__ == "__main__":
    args = parse_commandline()
    oc = OddsChecker(url=args.url, site=args.site)
    oc.get_odds_from_site()