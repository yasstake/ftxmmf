import json
import atexit
import websocket
from websocket import WebSocketApp
from logger.util import *
import zlib


try:
    import thread
except ImportError:
    import _thread as thread

TERMINATE_PERIOD = 500

_ENDPOINT = 'wss://real.OKEx.com:8443/ws/v3'


def inflate(data):
    decompress = zlib.decompressobj(-zlib.MAX_WBITS)
    inflated = decompress.decompress(data)
    inflated += decompress.flush()
    return inflated


class OkExClient:
    """
    https://www.okex.com/docs/en/#spot_ws-channel
    """

    def __init__(self, log_dir=None):
        self.ws = WebSocketApp(
            self._get_url(),
            on_message=self._on_message,
            on_close=self._on_close,
            on_error=self._on_error,
            on_open=self.on_open
        )
        self.log = Logger(log_file_dir=log_dir, process_name='OK', flag_file_dir=log_dir)
        self.order_book = OrderBook()
        self.partial = False
        self.terminate_count = 0

    def on_open(self):
        self.log.create_terminate_flag()
        self.send_message('{"op": "subscribe", "args": ["spot/trade:BTC-USDT", "spot/depth:BTC-USDT"]}')

    def send_message(self, message):
        self.ws.send(message)

    def _get_url(self):
        return _ENDPOINT

    def _on_message(self, raw_message):
        message = inflate(raw_message)
        # print(message)
        json_message = json.loads(message)

        if 'event' in json_message:
            print('EVENT', message)
        elif 'table' in json_message:
            type = json_message['table']

            if type == 'spot/depth':
                action = json_message['action']
                data = json_message['data']

                for item in data:
                    checksum = self.board_message_to_csv(item, action)

                    ''' 
                    TODO: implement crc for okex
                    crc = self.order_book.okex_crc32()
                    

                    print('[checksum]', checksum, crc)
                    if crc != checksum and self.partial:
                        print('ERROR: checksum error', crc, checksum)
                        #self.ws.close()
                    '''

            elif type == 'spot/trade':
                data = json_message['data']
                self.trade_message_to_csv(data)
        else:
            print('ERROR unknown message', message)

        if self.terminate_count:
            self.terminate_count += 1
            if TERMINATE_PERIOD < self.terminate_count:
                self.ws.close()
        elif self.log.check_terminate_flag():
            self.terminate_count = 1

    def _on_close(self):
        self.log.close()
        print('connection closed')

    def _on_error(self, error):
        self.ws.close()
        print('error', error)

    def connect(self):
        self.ws.run_forever(ping_interval=70, ping_timeout=30)

    def board_message_to_csv(self, json_message: json, action):
        bids = json_message['bids']
        asks = json_message['asks']
        time = json_message['timestamp']
        time = isotime_to_unix(time, ns=True)
        checksum = json_message['checksum']

        if action == 'partial':
            self.partial = True
            self.log.set_enable()

            self.order_book.clear()
            self.log.write_action(Action.PARTIAL, time, None, None)
            # print('[PARTIAL]', time, self.log._enable)

        self._board_to_csv(bids, asks, time, checksum)

        return checksum

    def _board_to_csv(self, bids, asks, time, checksum):
        for board in bids:
            bid_price = board[0]
            bid_size = board[1]
            self.order_book.set_bids(bid_price, bid_size)
            self.log.write_action(Action.UPDATE_BIT, time, bid_price, bid_size)

        for board in asks:
            ask_price = board[0]
            ask_size = board[1]
            self.order_book.set_asks(ask_price, ask_size)
            self.log.write_action(Action.UPDATE_ASK, time, ask_price, ask_size)

        if len(bids) or len(asks):
            self.log.write_check_sum(checksum)

    def _trade_message_to_csv(self, message: str):
        message = message.replace("'", '"')
        message = message.replace('False', '0')
        message = message.replace('false', '0')
        message = message.replace('True', '0')
        message = message.replace('true', '0')

        json_message = json.loads(message)
        self.trade_message_to_csv(json_message)

    def trade_message_to_csv(self, json_message: json):
        for execute in json_message:
            self.single_trade_message(execute)

    def single_trade_message(self, message):
        time = message['timestamp']
        side = message['side']
        price = float(message['price'])
        size = float(message['size'])
        id = message['trade_id']

        action = 0
        if side == 'sell':
            action = Action.TRADE_SHORT
        elif side == 'buy':
            action = Action.TRADE_LONG
        else:
            print('ERROR')

        unix_time = isotime_to_unix(time, True)
        self.log.write_action(action, unix_time, price, size, id)

import sys

if __name__ == '__main__':
    log_dir = None
    if len(sys.argv) == 2:
        log_dir = sys.argv[1]

    websocket.enableTrace(True)
    client = OkExClient(log_dir)
    atexit.register(client._on_close)
    client.connect()




