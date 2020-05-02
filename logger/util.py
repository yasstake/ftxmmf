from datetime import datetime
import os
from binascii import crc32
from tables import *
import numpy as np
import csv
import tables
import subprocess
from tqdm import tqdm

ISO_FORMAT_LEN = len('2020-04-30T11:43:53.734593')
NANO_SEC = 1_000_000.0


def to_nsec(sec):
    return int(sec * NANO_SEC)


def to_sec(nsec):
    return float(nsec) / NANO_SEC


def isotime_to_unix(time: str, ns=False):
    if time.endswith('Z'):
        time = time[:-1]
        time_len = len(time)
        if ISO_FORMAT_LEN < time_len:
            time = time[:ISO_FORMAT_LEN - time_len]
        elif time_len < ISO_FORMAT_LEN:
            time = time + '0' * (ISO_FORMAT_LEN - time_len)
        time += '+00:00'
    dt = datetime.fromisoformat(time)
    time_stamp = dt.timestamp()

    if ns:
        time_stamp = to_nsec(time_stamp)

    return time_stamp


def unixtime_to_iso(time, ns=False):
    if ns:
        time = to_sec(time)

    dt = datetime.utcfromtimestamp(time)
    iso = dt.date().isoformat() + 'T' + dt.time().isoformat() + 'Z'
    return iso


def unix_time_to_date(time, ns=False):
    if ns:
        time = to_sec(time)

    dt = datetime.utcfromtimestamp(time)
    iso = dt.date().isoformat()

    return iso


def unixtime_now(ns=False):
    dt = datetime.utcnow()

    time = dt.timestamp()

    if ns:
        time = to_nsec(time)

    return time


class Action:
    # board
    PARTIAL = 1
    UPDATE_BIT = 2
    UPDATE_ASK = 3

    # trade
    TRADE_LONG = 4
    TRADE_LONG_LIQUID = 5

    TRADE_SHORT = 6
    TRADE_SHORT_LIQUID = 7


class Logger:
    '''logging file utility'''
    def __init__(self, log_file_dir=None, flag_file_name=None, process_name=None):
        self.log_file_root_name = None
        self.log_file_name = None
        self.last_action = None
        self.last_time = None
        self.last_index = None

        if log_file_dir:
            self.log_file_dir = log_file_dir
        else:
            self.log_file_dir = os.sep + "tmp"

        if process_name:
            self.process_name = process_name
        else:
            self.process_name = 'LOG'

        if flag_file_name:
            self.flag_file_name = flag_file_name
        else:
            self.flag_file_name = os.sep + "tmp" + os.sep + self.process_name

        self.terminate_count = 200
        self.pid = str(os.getpid())

        self.rotate_file()

    def close(self):
        self.rotate_file()
        self.remove_terminate_flag()

    def process_id(self):
        return self.pid

    def create_terminate_flag(self):
        self.remove_terminate_flag()
        file_name = self.flag_file_name
        with open(file_name + "tmp", "w") as file:
            file.write(self.process_id())
            file.close()
            os.rename(file_name + "tmp", file_name)

    def check_terminate_flag(self):
        file_name = self.flag_file_name

        if os.path.isfile(file_name):
            with open(file_name, "r") as file:
                id = file.readline()
                if id != self.process_id():
                    self.terminate_count = self.terminate_count - 1
                    print(self.terminate_count)
                    if self.terminate_count < 0:
                        return True
        return False

    def remove_terminate_flag(self):
        file_name = self.flag_file_name
        if os.path.isfile(file_name):
            os.remove(file_name)

    def rotate_file(self):
        if self.log_file_name:
            if os.path.isfile(self.log_file_name):
                os.rename(self.log_file_name, self.log_file_root_name)

        time_string = unixtime_to_iso(unixtime_now()).replace(":", "-").replace('+', '-')

        self.log_file_root_name = self.log_file_dir + os.sep + self.process_name + '-' \
                                 + time_string + ".log"

        self.log_file_name = self.log_file_root_name + ".current"

    def write(self, message):
        with open(self.log_file_name, "a") as file:
            file.write(message)

    def write_check_sum(self, checksum):
        self.write(str(checksum))

    def write_action(self, action, time, price, size, id=None, price_in_100c=True):
        if id:
            self.last_index = id
        elif self.last_action == action and self.last_time == time:
            self.last_index += 1
        else:
            self.last_action = action
            self.last_time = time
            self.last_index = 0

        s = '\n' + str(action) + ',' + str(time) + ',' + str(self.last_index) + ','
        if price is not None:
            if price_in_100c:
                s += str(int(price*10))
            else:
                s += str(price)
        s += ','
        if size is not None:
            s += str(size)
        s += ','

        self.write(s)


class OrderBook:
    def __init__(self):
        self.bids = None
        self.asks = None
        self.clear()

    def clear(self):
        self.bids = {}
        self.asks = {}

    def set_bids(self, price, size):
        if size == 0:
            del self.bids[price]
        else:
            self.bids[price] = size

    def set_asks(self, price, size):
        if size == 0:
            del self.asks[price]
        else:
            self.asks[price] = size

    def to_string(self):
        sorted_bids = sorted(self.bids.keys(), reverse=True)
        sorted_asks = sorted(self.asks.keys())

        num_items = min(len(sorted_asks), len(sorted_bids))

        s = ''
        for i in range(num_items):
            bid = sorted_bids[i]
            ask = sorted_asks[i]

            s += str(bid) + ':' + str(self.bids[bid]) + ':'
            s += str(ask) + ':' + str(self.asks[ask]) + ':'

        if s.endswith(':'):
            s = s[:-1]

        return s

    def crc32(self):
        s = self.to_string()
        return crc32(s.encode())


class BoardCompress:
    def __init__(self):
        self.bids = None
        self.asks = None
        self.clear()

    def clear(self):
        self.bids = {}
        self.asks = {}

    def set_bids(self, price, size):
        self.bids[price] = size

    def set_asks(self, price, size):
        self.asks[price] = size

    def make_string(self, value):
        if int(value) == value:
            return str(int(value))
        return str(value)

    def encode(self, compress=False):
        sorted_bids = sorted(self.bids.keys(), reverse=True)

        s = ''
        if len(sorted_bids):
            s = 'B,' + str(len(sorted_bids)) + ','
            min_bid = sorted_bids[0]
            s += str(min_bid) + ',' + str(self.bids[min_bid]) + ','

            for bid in sorted_bids[1:]:
                if compress:
                    s += self.make_string(min_bid - bid) + ',' + str(self.bids[bid]) + ','
                else:
                    s += str(bid) + ',' + str(self.bids[bid]) + ','

        sorted_asks = sorted(self.asks.keys())

        if len(sorted_asks):
            s += 'A,' + str(len(sorted_asks)) + ','
            min_ask = sorted_asks[0]
            s += str(min_ask) + ',' + str(self.asks[min_ask]) + ','
            for ask in sorted_asks[1:]:
                if compress:
                    s += self.make_string(ask - min_ask) + ',' + str(self.asks[ask]) + ','
                else:
                    s += str(ask) + ',' + str(self.asks[ask]) + ','

        return s[:-1]


class LogRecord(IsDescription):
    action = UInt8Col()  # Action class
    time = Int64Col()    # nano sec
    index = UInt32Col()  # index or id
    price = UInt32Col()  # price in USD(100c) or JPY(1Yen)
    size = Float32Col()  # volume in BTC

class LogLoader:
    def __init__(self):
        self.h5file = None
        self.board_table = None
        self.trade_table = None

        self.board_record = None
        self.trade_record = None

    @staticmethod
    def parse_line(row):
        action = int(row[0])
        time = int(row[1])
        index = int(row[2])
        price = row[3]
        if price == '':
            price = 0
        else:
            price = int(price)

        size = row[4]
        if size == '':
            size = 0
        else:
            size = float(size)

        return action, time, index, price, size

    def open_db(self, file_name):
        FILTERS = tables.Filters(complib='zlib', complevel=9)
        self.h5file = tables.open_file(file_name, mode='a', title='testfile', filters=FILTERS)

        log_group = None

        if '/LOG' in self.h5file:
            log_group = self.h5file.get_node('/LOG')
            self.board_table = log_group.board
            self.trade_table = log_group.trade
        else:
            # create group and tables
            log_group = self.h5file.create_group('/', 'LOG', 'Log directory')
            self.board_table = self.h5file.create_table(log_group, 'board', LogRecord, 'board data')
            self.board_table.cols.time.create_index()
            self.board_table.cols.index.create_index()
            self.trade_table = self.h5file.create_table(log_group, 'trade', LogRecord, 'trade data')
            self.trade_table.cols.time.create_index()
            self.trade_table.cols.index.create_index()

        self.board_record = self.board_table.row
        self.trade_record = self.trade_table.row

    def close_db(self):
        self.board_table.flush()
        self.trade_table.flush()
        self.h5file.close()

    def load(self, log_file):
        command = 'wc -l {}'.format(log_file)
        output = subprocess.check_output(command, shell=True).decode()
        total_lines = int(output.split()[0])
        progress_bar = tqdm(total=total_lines)

        with open(log_file) as f:
            reader = csv.reader(f)
            for row in reader:
                progress_bar.update(1)
                if len(row) == 0:
                    continue

                action, time, index, price, size = LogLoader.parse_line(row)

                record = None
                table = None
                if action == Action.PARTIAL or \
                    action == Action.UPDATE_ASK or \
                    action == Action.UPDATE_BIT:
                    record = self.board_record
                    table = self.board_table
                elif action == Action.TRADE_LONG or \
                    action == Action.TRADE_SHORT or \
                    action == Action.TRADE_LONG_LIQUID or \
                    action == Action.TRADE_SHORT_LIQUID:
                    record = self.trade_record
                    table = self.trade_table
                else:
                    print('unknown actionERROR', action, record)

                '''
                # check if exists
                query = '(time=={}) & (index=={})'.format(time, index)
                # query = '(time=={}) & (action=={})'.format(time, action)
                rows = table.read_where(query)

                if len(rows):
                    continue
                '''

                record['action'] = action
                record['time'] = time
                record['index'] = index
                record['price'] = price
                record['size'] = size
                record.append()



import sys

if __name__ == '__main__':
    argc = len(sys.argv)

    logfile = None
    db_file = './logdb.hd5'
    if argc == 2:
        logfile = sys.argv[1]
    elif argc == 3:
        logfile = sys.argv[1]
        db_file = sys.argv[2]
    else:
        print('[usage] util.py logfile.log [dbfile.hd5]')
        exit(-1)

    loader = LogLoader()
    loader.open_db(db_file)
    loader.load(logfile)
    loader.close_db()

