import csv
import sys
from tables import IsDescription, UInt8Col, Int64Col, UInt32Col, Float32Col
import tables

import numpy as np
import pandas as pd
from tqdm import tqdm
from logger.util import Action
from logger.util import unix_time_to_date


class LogRecord(IsDescription):
    time = Int64Col(pos=1)    # nano sec
    index = UInt32Col(pos=2)  # index or id
    action = UInt8Col(pos=3)  # Action class
    price = UInt32Col(pos=4)  # price in USD(100c) or JPY(1Yen)
    size = Float32Col(pos=5)  # volume in BTC


class LogTable:
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

    def open_db(self, file_name, time=None):
        FILTERS = tables.Filters(complib='zlib', complevel=9)
        self.h5file = tables.open_file(file_name, mode='a', title='testfile', filters=FILTERS)

    def _group_name(self, time=None):
        path = 'LOG'
        if time:
            path = unix_time_to_date(time, ns=True).replace('-', '')
        return path

    def drop_group(self, time=None):
        path = self._group_name()

        log_group = self.h5file.get_node('/' + path)
        if log_group:
            del log_group

    def create_or_open_table(self, time=None):
        path = self._group_name(time)

        if '/' + path in self.h5file:
            self.open_table(path)
        else:
            self.create_table(path)

    def open_table(self, path):
        log_group = self.h5file.get_node('/' + path)
        self.board_table = log_group.board
        self.trade_table = log_group.trade
        self.board_record = self.board_table.row
        self.trade_record = self.trade_table.row

    def create_table(self, path):
        log_group = self.h5file.create_group('/', path, 'Log directory')
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

    def trade_data(self):
        self.trade_table

    def load(self, log_file):
        table_opened = False

        with open(log_file) as f:
            reader = csv.reader(f)
            for row in tqdm(reader):
                if len(row) == 0:
                    continue

                action, time, index, price, size = LogTable.parse_line(row)

                if not table_opened:
                    self.create_or_open_table(time=time)

                record = None
                table = None
                if action == Action.PARTIAL or \
                    action == Action.UPDATE_BUY or \
                    action == Action.UPDATE_SELL:
                    record = self.board_record
                    table = self.board_table
                elif action == Action.TRADE_BUY or \
                    action == Action.TRADE_SELL or \
                    action == Action.TRADE_BUY_LIQUID or \
                    action == Action.TRADE_SELL_LIQUID:
                    record = self.trade_record
                    table = self.trade_table
                else:
                    print('unknown actionERROR', action, record)

                record['action'] = action
                record['time'] = time
                record['index'] = index
                record['price'] = price
                record['size'] = size
                record.append()




if __name__ == '__main__':
    argc = len(sys.argv)

    logfile = None
    db_file = './logdb.h5'
    if argc == 2:
        logfile = sys.argv[1]
    elif argc == 3:
        logfile = sys.argv[1]
        db_file = sys.argv[2]
    else:
        print('[usage] table_test.py logfile.log [dbfile.hd5]')
        exit(-1)

    loader = LogTable()
    loader.open_db(db_file)
    loader.drop_group()
    loader.load(logfile)
    loader.close_db()

