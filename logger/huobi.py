import json
import websocket
from websocket import WebSocketApp
from logger.util import *
import atexit

try:
    import thread
except ImportError:
    import _thread as thread

# wss://api-aws.huobi.pro/ws
_END_POINT = 'wss://api-cloud.huobi.co.jp/ws'
TERMINATE_PERIOD = 3


class HuobiClient:
    def __init__(self, log_dir=None):
        self.ws = WebSocketApp(
            self._get_url(),
            on_message=self._on_message,
            on_close=self.on_close,
            on_error=self._on_error
        )

        self.ws.on_open = self.on_open
        self.log = Logger(log_file_dir=log_dir, process_name='HU', flag_file_dir=log_dir)
        self.current_time = None
        self.partial = False
        self.terminate_count = 0

    def on_open(self):
        self.log.create_terminate_flag()

        #self.ws.send('{"id": "id generate by client", "sub": "topic to sub", "freq-ms": 1000}')

        # self.ws.send('{"sub": "market.btcjpy.kline.1min", "id": "id1"}')

        self.ws.send('{"sub": "market.btcjpy.trade.detail", "id": "id1"}')

        '''
        self.ws.send(json.dumps(
            [{"method": "subscribe", "params": {"channel": CHANNEL_EXECUTION}},
             {"method": "subscribe", "params": {"channel": CHANNEL_BOARD_SNAPSHOT}},
             {"method": "subscribe", "params": {"channel": CHANNEL_BOARD}}
             ]))
        '''

    def _on_message(self, message):
        m = gzip.decompress(message)
        print(m)

        j = json.loads(m)

        if 'ping' in j:
            id = j['ping']
            pong = '{"pong":' + str(id) + '}'
            self.ws.send(pong)
        '''
        json_message = json.loads(message)

        channel = json_message['params']['channel']
        message = json_message['params']['message']
        '''
        '''
        if channel == CHANNEL_EXECUTION:
            self.trade_message_to_csv(message)
        elif channel == CHANNEL_BOARD_SNAPSHOT or channel == CHANNEL_BOARD:
            self.board_message_to_csv(message, channel)
        else:
            print('other channel', channel)

        if TERMINATE_PERIOD < self.terminate_count:
            self.ws.close()
        '''

    def _get_url(self):
        return _END_POINT

    def on_close(self):
        self.log.close()
        print('connection closed')

    def _on_error(self, error):
        self.ws.close()
        print('error', error)

    def connect(self):
        self.ws.run_forever()

    def _board_message_to_csv(self, message: str, channel):
        message = message.replace("'", '"')
        json_message = json.loads(message)
        self.board_message_to_csv(json_message, channel)

    def board_message_to_csv(self, json_message: json, channel):
        '''
        bids = json_message['bids']
        asks = json_message['asks']

        m = ""
        if channel == CHANNEL_BOARD_SNAPSHOT:
            self.partial = True

            if self.current_time:
                self.log.set_enable()

            print('[PARTIAL]', self.current_time, self.log._enable)
            self.log.write_action(Action.PARTIAL, self.current_time, None, None)

            if self.terminate_count:
                self.terminate_count += 1
            elif self.log.check_terminate_flag():
                self.terminate_count = 1


        self._board_to_csv(bids, asks)
        '''

    def _board_to_csv(self, bids, asks):
        '''
        for board in bids:
            price, size = board['price'], board['size']
            self.log.write_action(Action.UPDATE_BIT, self.current_time, price, size)

        for board in asks:
            price, size = board['price'], board['size']
            self.log.write_action(Action.UPDATE_ASK, self.current_time, price, size)
        '''

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
            action = Action.TRADE_SELL
        elif side == 'BUY':
            action = Action.TRADE_BUY
        else:
            print('ERROR')

        self.log.write_action(action, time, price, size, id)


import sys

if __name__ == '__main__':
    log_dir = None
    if len(sys.argv) == 2:
        log_dir = sys.argv[1]

    websocket.enableTrace(True)
    client = HuobiClient(log_dir=log_dir)
    atexit.register(client.on_close)
    client.connect()




