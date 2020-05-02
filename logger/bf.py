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
        self.current_time = None
        self.partial = False

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

        if channel == CHANNEL_EXECUTION:
            self.trade_message_to_csv(message)
        elif channel == CHANNEL_BOARD_SNAPSHOT or channel == CHANNEL_BOARD:
            self.board_message_to_csv(message, channel)
        else:
            print('other channel', channel)

        if self.partial and self.log.check_terminate_flag():
            self.ws.close()

    def _get_url(self):
        return _END_POINT

    def on_close(self):
        self.log.close()
        print('connection closed')

    def _on_error(self, error):
        self.ws.close()
        print('error', error)

    def connect(self):
        self.ws.run_forever(ping_interval=70, ping_timeout=30)

    def _board_message_to_csv(self, message: str, channel):
        message = message.replace("'", '"')
        json_message = json.loads(message)
        self.board_message_to_csv(json_message, channel)

    def board_message_to_csv(self, json_message: json, channel):
        bids = json_message['bids']
        asks = json_message['asks']
        time = str(self.current_time)

        m = ""
        if channel == CHANNEL_BOARD_SNAPSHOT:
            if not self.partial and self.current_time:
                self.partial = True
                self.log.set_enable()
                self.log.create_terminate_flag()
            self.log.write_action(Action.PARTIAL, time, None, None)

        self._board_to_csv(bids, asks)

    def _board_to_csv(self, bids, asks):
        for board in bids:
            price, size = board['price'], board['size']
            self.log.write_action(Action.UPDATE_BIT, self.current_time, price, size)

        for board in asks:
            price, size = board['price'], board['size']
            self.log.write_action(Action.UPDATE_ASK, self.current_time, price, size)

    def _trade_message_to_csv(self, message):
        message = message.replace("'", '"')
        json_message = json.loads(message)
        self.trade_message_to_csv(json_message)

    def trade_message_to_csv(self, json_message):
        for execute in json_message:
            self.single_trade_message(execute)

    def single_trade_message(self, message):
        time = message['exec_date']
        time = isotime_to_unix(time, ns=True)
        self.current_time = time
        side = message['side']
        price = message['price']
        size = message['size']
        id = message['id']

        action = 0
        if side == 'SELL':
            action = Action.TRADE_SHORT
        elif side == 'BUY':
            action = Action.TRADE_LONG
        else:
            print('ERROR')

        self.log.write_action(action, time, price, size, id)


if __name__ == '__main__':
    websocket.enableTrace(True)
    client = BfClient()
    atexit.register(client.on_close)
    client.connect()




