import json
import websocket
from websocket import WebSocketApp
from logger.util import *
import atexit

try:
    import thread
except ImportError:
    import _thread as thread


_END_POINT = 'wss://ws.lightstream.bitflyer.com/json-rpc'
CHANNEL_EXECUTION = 'lightning_executions_FX_BTC_JPY'
CHANNEL_BOARD_SNAPSHOT = 'lightning_board_snapshot_FX_BTC_JPY'
CHANNEL_BOARD = 'lightning_board_FX_BTC_JPY'


class BfClient:
    def __init__(self):
        self.ws = WebSocketApp(
            self._get_url(),
            on_message=self._on_message,
            on_close=self.on_close,
            on_error=self._on_error
        )

        self.ws.on_open = self.on_open
        self.log = Logger(process_name='BF')
        self.current_time = ''
        self.compress = BoardCompress()

    def on_open(self):
        self.ws.send(json.dumps(
            [{"method": "subscribe", "params": {"channel": CHANNEL_EXECUTION}},
             {"method": "subscribe", "params": {"channel": CHANNEL_BOARD_SNAPSHOT}},
             {"method": "subscribe", "params": {"channel": CHANNEL_BOARD}}
             ]))

    def _on_message(self, message):
        json_message = json.loads(message)

        channel = json_message['params']['channel']
        message = json_message['params']['message']

        csv = ''
        if channel == CHANNEL_EXECUTION:
            csv = self.trade_message_to_csv(message)
        elif channel == CHANNEL_BOARD_SNAPSHOT or channel == CHANNEL_BOARD:
            csv = self.board_message_to_csv(message, channel)

        self.log.write(csv)

        if self.log.check_terminate_flag():
            self.ws.close()

    def _get_url(self):
        return _END_POINT

    def on_close(self):
        self.log.close()

    def _on_error(self, error):
        self.ws.close()
        print('error', error)

    def connect(self):
        self.ws.run_forever(ping_interval=70, ping_timeout=30)

    def _board_message_to_csv(self, message: str, channel):
        message = message.replace("'", '"')
        json_message = json.loads(message)
        return self.board_message_to_csv(json_message, channel)

    def board_message_to_csv(self, json_message: json, channel):
        bids = json_message['bids']
        asks = json_message['asks']
        time = str(self.current_time)

        m = ""
        if channel == CHANNEL_BOARD_SNAPSHOT:
            m += 'P,'
        elif channel == CHANNEL_BOARD:
            m += 'U,'
        else:
            print("ERROR")

        m += str(time) + ',' + '0' + ','
        m += self._board_to_csv(bids, asks)

        return m + '\n'

    def _board_to_csv(self, bids, asks):
        self.compress.clear()

        for board in bids:
            self.compress.set_bids(board['price'], board['size'])

        for board in asks:
            self.compress.set_asks(board['price'], board['size'])

        return self.compress.encode()

    def _trade_message_to_csv(self, message):
        message = message.replace("'", '"')
        print(message)
        json_message = json.loads(message)

    def trade_message_to_csv(self, json_message):
        m = ''
        for execute in json_message:
            m += self.single_trade_message(execute)
        return m

    def single_trade_message(self, message):
        time = message['exec_date']
        self.current_time = isotime_to_unix(time)
        side = message['side']
        price = message['price']
        size = message['size']
        id = message['id']
        liquidation = 0

        m = ''
        if side == 'SELL':
            m += 'S'
        elif side == 'BUY':
            m += 'B'
        else:
            print('ERROR')

        if liquidation == 0:
            m += '0,'
        else:
            m += '1,'

        m += str(id) + ','
        m += str(isotime_to_unix(time)) + ','
        m += str(price) + ','
        m += str(size) + '\n'

        return m


if __name__ == '__main__':
    websocket.enableTrace(True)
    client = BfClient()
    atexit.register(client.on_close)
    client.connect()




