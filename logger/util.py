from datetime import datetime
import os
from binascii import crc32

ISO_FORMAT_LEN = len('2020-04-30T11:43:53.734593')

def isotime_to_unix(time: str):
    if time.endswith('Z'):
        time = time[:-1]
        time_len = len(time)
        if ISO_FORMAT_LEN < time_len:
            time = time[:ISO_FORMAT_LEN - time_len]
        elif time_len < ISO_FORMAT_LEN:
            time = time + '0' * (ISO_FORMAT_LEN - time_len)
        time += '+00:00'
    dt = datetime.fromisoformat(time)
    return dt.timestamp()


def unixtime_to_iso(time):
    dt = datetime.utcfromtimestamp(time)
    iso = dt.date().isoformat() + 'T' + dt.time().isoformat() + 'Z'
    return iso


def unixtime_now():
    dt = datetime.utcnow()
    return dt.timestamp()


class Logger:
    '''logging file utility'''
    def __init__(self, log_file_dir=None, flag_file_name=None, process_name=None):
        self.log_file_root_name = None
        self.log_file_name = None

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
        self.create_terminate_flag()

    def __del__(self):
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

        print(sorted_asks)
        print(sorted_bids)

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
