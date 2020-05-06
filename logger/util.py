from datetime import datetime
import os
from glob import glob
import pathlib
from binascii import crc32
from random import random

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
    def __init__(self, log_file_dir=None, flag_file_dir=None, process_name=None):
        self.log_file_root_name = None
        self.log_file_name = None
        self.last_action = None
        self.last_time = None
        self.last_index = None
        self._enable = False

        if log_file_dir:
            self.log_file_dir = log_file_dir
        else:
            self.log_file_dir = os.sep + "tmp"

        if process_name:
            self.process_name = process_name
        else:
            self.process_name = 'LOG'

        self.pid = str(unixtime_now()) + '-' + str(random()*1000)

        if flag_file_dir:
            self.flag_file_name = flag_file_dir + os.sep + self.process_name + self.process_id() + '.lock'
            self.flag_pattern = flag_file_dir + os.sep + self.process_name + '*' + '.lock'
        else:
            self.flag_file_name = os.sep + "tmp" + os.sep + self.process_name + self.process_id() + '.lock'
            self.flag_pattern = os.sep + "tmp" + os.sep + self.process_name + '*' + '.lock'

        self.rotate_file()


    def close(self):
        self.rotate_file()
        self.remove_terminate_flag()

    def process_id(self):
        return self.pid

    def create_terminate_flag(self):
        self.remove_terminate_flag()
        pathlib.Path(self.flag_file_name).touch()
        print('createflag', self.flag_file_name)

    def check_terminate_flag(self):
        '''
        フラグパターンのファイルが 自分以外が存在　→　終了（削除）
        　　　　　　　　　　　　　１つのみ、かつ自分　→　維持
        :return:
        '''
        terminate = False

        for file in glob(self.flag_pattern):
            if file != self.flag_file_name:
                print('[peer flag ]', file)
                terminate = True
                break

        if terminate:
            self.remove_terminate_flag()

        return terminate

    def set_enable(self):
        self._enable = True

    def remove_terminate_flag(self):
        for file in glob(self.flag_pattern):
            print('[remove flag]', file)
            os.remove(file)

    def rotate_file(self):
        if self.log_file_name:
            if os.path.isfile(self.log_file_name):
                os.rename(self.log_file_name, self.log_file_root_name)

        time_string = unixtime_to_iso(unixtime_now()).replace(":", "-").replace('+', '-')

        self.log_file_root_name = self.log_file_dir + os.sep + self.process_name + '-' \
                                 + time_string + ".log"

        self.log_file_name = self.log_file_root_name + ".current"
        print('[newfile]', self.log_file_name)

    def write(self, message):
        if not self._enable:
            print('[skipping] ', message)
            return

        # todo: 1) recycle file handler, 2) use gzip compress on the fly.
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

from logger.table import LogTable


class LogLoader:
    def __init__(self):
        pass

    def open(self, file):
        pass

    def line_string(self, line: str):
        items = LogTable.parse_line(line.split(','))
        return line(items)

    def line(self, items):
        pass

    def new_tick(self):
        pass

