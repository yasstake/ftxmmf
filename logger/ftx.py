import json
import websocket
from websocket import WebSocketApp
from logger.util import *

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

    def on_open(self):
        self.send_message('{"op": "subscribe", "channel": "trades", "market": "BTC-PERP"}')
        self.send_message('{"op": "subscribe", "channel": "orderbook", "market": "BTC-PERP"}')

    def send_message(self, message):
        self.ws.send(message)

    def _get_url(self):
        return FtxClient._ENDPOINT

    def _on_message(self, raw_message: str):
        print(raw_message)

        json_message = json.loads(raw_message)

        channel = json_message['channel']
        type =json_message['type']

        if type == 'subscribed':
            print('subscribed', raw_message)
        else:
            csv = ''
            if channel == 'orderbook':
                data = json_message['data']
                csv = self.board_message_to_csv(data)
            elif channel == 'trades':
                data = json_message['data']
                csv = self.trade_message_to_csv(data)

            self.log.write(csv)

        if self.log.check_terminate_flag():
            self.ws.close()

    def _on_close(self):
        print('close')
        pass

    def _on_error(self, error):
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
        checksum = json_message['checksum']
        action = json_message['action']
        m = ""

        if action == 'update':
            m += 'U,'
        elif action == 'partial':
            m += 'P,'

        m += str(time) + ',' + str(checksum) + ','
        m += self._board_to_csv(bids, asks)
        return m + '\n'

    def _board_to_csv(self, bids, asks):
        m = 'B,' + str(len(bids)) + ','
        for board in bids:
            m += str(board[0]) + ',' + str(board[1]) + ','

        m += 'A,' + str(len(asks)) + ','
        for board in asks:
            m += str(board[0]) + ',' + str(board[1]) + ','

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
        if side == 'sell':
            m += 'S'
        elif side == 'buy':
            m += 'B'
        else:
            print('ERROR')

        if liquidation == 0:
            m += '0,'
        else:
            m += '1,'

        m += str(isotime_to_unix(time)) + ','
        m += str(id) + ','
        m += str(price) + ','
        m += str(size) + '\n'

        return m



if __name__ == '__main__':
    websocket.enableTrace(True)
    client = FtxClient()
    client.connect()




