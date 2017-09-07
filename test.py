#!bin/python_interpreter

# HOW TO USE:
# run the command:
# ./test.py simple planning && ./test.py simple run
# or
# ./test.py esco planning && ./test.py esco run

import os
import os.path
import os.path
import datetime
import json
import sys
import argparse
import contextlib
import tempfile
from dateutil.tz import tzlocal
from subprocess import check_output

PWD = os.path.dirname(os.path.realpath(__file__))
CWD = os.getcwd()
TENDER = os.path.join(PWD,
                      'src/openprocurement.auction/openprocurement/auction/tests/functional/data/tender_simple.json')

TENDER = {'simple': os.path.join(PWD, 'src/openprocurement.auction/openprocurement/auction/tests/functional/data/tender_simple.json'),
          'esco': 'src/openprocurement.auction.esco/openprocurement/auction/esco/tests/functional/data/tender_esco.json'}

WORKER = {'simple': 'auction_worker', 'esco': 'auction_esco'}


@contextlib.contextmanager
def update_auctionPeriod(path, auction_type):
    with open(path) as file:
        data = json.loads(file.read())
    new_start_time = (datetime.datetime.now(tzlocal()) + datetime.timedelta(
        seconds=20)).isoformat()
    data['data']['auctionPeriod']['startDate'] = new_start_time
    with tempfile.NamedTemporaryFile(delete=False) as auction_file:
        json.dump(data, auction_file)
        auction_file.seek(0)
    yield auction_file.name
    auction_file.close()


def planning(tender_file_path, worker, auction_id):
    with update_auctionPeriod(tender_file_path,
                              auction_type='simple') as auction_file:
        os.system('{0}/bin/{1} planning {2}'
                  ' {0}/etc/auction_worker_defaults.yaml --planning_procerude partial_db --auction_info {3}'.format(
            CWD, worker, auction_id, auction_file))
    os.system('sleep 3')


def run(tender_file_path, worker, auction_id):
    with update_auctionPeriod(tender_file_path,
                              auction_type='simple') as auction_file:
        check_output('{0}/bin/{1} run {2}'
                     ' {0}/etc/auction_worker_defaults.yaml --planning_procerude partial_db --auction_info {3}'.format(
            CWD, worker, auction_id, auction_file).split())
    os.system('sleep 3')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('auction_type', type=str)
    parser.add_argument('action_type', type=str)

    args = parser.parse_args()

    actions = globals()
    if args.action_type in actions:
        actions.get(args.action_type)(TENDER[args.auction_type], WORKER[args.auction_type], "11111111111111111111111111111111")
