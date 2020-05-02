import json
import atexit
import websocket
from websocket import WebSocketApp
from logger.util import *
import csv

try:
    import thread
except ImportError:
    import _thread as thread




class FtxClient:
    _ENDPOINT = 'wss://ftx.com/ws/'

    def __init__(self):
        self.ws = WebSocketApp(
            self._get_url(),
            on_message=self._on_message,
            on_close=self._on_close,
            on_error=self._on_error,
            on_open=self.on_open
        )
        self.log = Logger(process_name='FTX')
        self.order_book = OrderBook()
        self.partial = False

    def on_open(self):
        self.send_message('{"op": "subscribe", "channel": "trades", "market": "BTC-PERP"}')
        self.send_message('{"op": "subscribe", "channel": "orderbook", "market": "BTC-PERP"}')

    def send_message(self, message):
        self.ws.send(message)

    def _get_url(self):
        return FtxClient._ENDPOINT

    def _on_message(self, raw_message: str):
        json_message = json.loads(raw_message)

        channel = json_message['channel']
        type = json_message['type']

        if type == 'subscribed':
            print('subscribed', raw_message)
            self.log.create_terminate_flag()
        else:
            csv = ''
            if channel == 'orderbook':
                data = json_message['data']
                csv, checksum = self.board_message_to_csv(data)
                crc = self.order_book.crc32()

                if crc != checksum and self.partial:
                    print('ERROR: checksum error')
                    self.ws.close()

                # self.log.write(csv)
            elif channel == 'trades':
                data = json_message['data']
                csv = self.trade_message_to_csv(data)

                if self.partial:
                    pass
                    # self.log.write(csv)

        if self.log.check_terminate_flag():
            self.ws.close()

    def _on_close(self):
        self.log.close()
        print('close')

    def _on_error(self, error):
        self.ws.close()
        print('error', error)

    def connect(self):
        self.ws.run_forever(ping_interval=70, ping_timeout=30)

    def _board_message_to_csv(self, message: str):
        message = message.replace("'", '"')
        json_message = json.loads(message)
        return self.board_message_to_csv(json_message)

    def board_message_to_csv(self, json_message: json):
        bids = json_message['bids']
        asks = json_message['asks']
        time = json_message['time']
        time = to_nsec(time)
        checksum = json_message['checksum']
        action = json_message['action']
        m = ""

        if action == 'update':
            m += 'U,'
        elif action == 'partial':
            m += 'P,'
            self.order_book.clear()
            self.partial = True
            self.log.write_action(Action.PARTIAL, time, None, None)

        m += str(time) + ',' + str(checksum) + ','
        m += self._board_to_csv(bids, asks, time, checksum)
        return m + '\n', checksum

    def _board_to_csv(self, bids, asks, time, checksum):
        m = 'B,' + str(len(bids)) + ','
        for board in bids:
            bid_price = board[0]
            bid_size = board[1]
            m += str(bid_price) + ',' + str(bid_size) + ','
            self.order_book.set_bids(bid_price, bid_size)
            self.log.write_action(Action.UPDATE_BIT, time, bid_price, bid_size)

        m += 'A,' + str(len(asks)) + ','
        for board in asks:
            ask_price = board[0]
            ask_size = board[1]
            m += str(ask_price) + ',' + str(ask_size) + ','
            self.order_book.set_asks(ask_price, ask_size)
            self.log.write_action(Action.UPDATE_ASK, time, ask_price, ask_size)

        if len(bids) or len(asks):
            self.log.write_check_sum(checksum)

        return m

    def _trade_message_to_csv(self, message: str):
        message = message.replace("'", '"')
        message = message.replace('False', '0')
        message = message.replace('false', '0')
        message = message.replace('True', '0')
        message = message.replace('true', '0')

        json_message = json.loads(message)
        self.trade_message_to_csv(json_message)

    def trade_message_to_csv(self, json_message: json):
        m = ''
        for execute in json_message:
            m += self.single_trade_message(execute)
        return m

    def single_trade_message(self, message):
        time = message['time']
        side = message['side']
        price = message['price']
        size = message['size']
        liquidation = message['liquidation']
        id = message['id']

        m = ''
        action = 0
        if side == 'sell':
            m += 'S'
            action = Action.TRADE_SHORT
        elif side == 'buy':
            m += 'B'
            action = Action.TRADE_LONG
        else:
            print('ERROR')

        if liquidation == 0:
            m += '0,'
        else:
            m += '1,'
            action += 1

        unix_time = isotime_to_unix(time, True)
        m += str(unix_time) + ','
        m += str(id) + ','
        m += str(price) + ','
        m += str(size) + '\n'

        self.log.write_action(action, unix_time, price, size, id)

        return m


if __name__ == '__main__':
    websocket.enableTrace(True)
    client = FtxClient()
    atexit.register(client._on_close)
    client.connect()




