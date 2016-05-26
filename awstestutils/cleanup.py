import logging
import argparse
import awstestutils

logging.basicConfig(level=logging.INFO)


def parse_args():
    parser = argparse.ArgumentParser(description='Delete test topics and queues that might have been left behind.')
    parser.add_argument('-r', '--region-name', default=None, help='region name to work on (default is system configuration)')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    if args.region_name is not None:
        logging.getLogger('cleanup').info('using region "{}"'.format(args.region_name))
    awstestutils.cleanup(region_name=args.region_name)
