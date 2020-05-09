import json
import websocket
from websocket import WebSocketApp
from logger.util import *
import atexit
import sys

try:
    import thread
except ImportError:
    import _thread as thread


_END_POINT = 'wss://stream.bybit.com/realtime_public'
CHANNEL_ORDER_BOOK = 'orderBook_200.100ms.BTCUSDT'
CHANNEL_TRADE = 'trade.BTCUSDT'
CHANNEL_INSTRUMENT = 'instrument_info.100ms.BTCUSDT'
TERMINATE_PERIOD = 3


class BybitClient:
    def __init__(self, log_dir=None):
        self.ws = WebSocketApp(
            self._get_url(),
            on_message=self._on_message,
            on_close=self.on_close,
            on_error=self._on_error
        )

        self.ws.on_open = self.on_open
        self.log = Logger(log_file_dir=log_dir, process_name='BB', flag_file_dir=log_dir)
        self.current_time = None
        self.partial = False
        self.terminate_count = 0

    def on_open(self):
        self.log.create_terminate_flag()

        self.ws.send('{"op": "subscribe", "args": ["' + CHANNEL_ORDER_BOOK + '"]}')
        self.ws.send('{"op": "subscribe", "args": ["' + CHANNEL_TRADE + '"]}')
        self.ws.send('{"op": "subscribe", "args": ["' + CHANNEL_INSTRUMENT + '"]}')

    def _on_message(self, message):
        json_message = json.loads(message)

        if 'topic' in json_message:
            self.on_topic(json_message)
        elif 'success' in json_message:
            print('success', json_message)
        else:
            print('unknown type', json_message)

    def on_topic(self, json_message:json):
        channel = json_message['topic']
        data = json_message['data']
        if 'timestamp_e6' in json_message:
            time_stamp = json_message['timestamp_e6']
            self.current_time = time_stamp

        if channel == CHANNEL_ORDER_BOOK:
            message_type = json_message['type'] # 'delta' or 'snapshot'
            self.board_message_to_csv(data, message_type)
            pass
        elif channel == CHANNEL_TRADE:
            self.trade_message_to_csv(data)
            pass
        elif channel == CHANNEL_INSTRUMENT:
            pass
        else:
            print('Unknown channel')

        if self.terminate_count:
            self.terminate_count += 1
            if TERMINATE_PERIOD < self.terminate_count:
                self.ws.close()
        elif self.log.check_terminate_flag():
            self.terminate_count = 1

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

    def board_message_to_csv(self, json_data: json, message_type: str):
        if message_type == 'snapshot':
            print('snapshot-----')
            self.partial = True
            self.log.set_enable()
            self.log.write_action(Action.PARTIAL, self.current_time, None, None)

        for key in json_data.keys():
            self._process_board_message(key, json_data[key])

    def _process_board_message(self, key, line):
        for rec in line:
            side = rec['side']
            if side == 'Sell':
                action = Action.UPDATE_BIT
            elif side == 'Buy':
                action = Action.UPDATE_ASK
            else:
                print('error unknown side')

            price = float(rec['price'])
            if key == 'delete':
                size = 0
            else:
                size = rec['size']
            self.log.write_action(action, self.current_time, price, size)

    def _trade_message_to_csv(self, message):
        message = message.replace("'", '"')
        json_message = json.loads(message)
        self.trade_message_to_csv(json_message)

    def trade_message_to_csv(self, json_message):
        for execute in json_message:
            self.single_trade_message(execute)

    def single_trade_message(self, message):
        self.current_time = message['trade_time_ms']
        side = message['side']
        price = float(message['price'])
        size = float(message['size'])
        trade_id = str(message['trade_id'])

        action = 0
        if side == 'Sell':
            action = Action.TRADE_SHORT
        elif side == 'Buy':
            action = Action.TRADE_LONG
        else:
            print('ERROR')

        self.log.write_action(action, self.current_time, price, size, trade_id)


if __name__ == '__main__':
    log_dir = None
    if len(sys.argv) == 2:
        log_dir = sys.argv[1]

    websocket.enableTrace(True)
    client = BybitClient(log_dir=log_dir)
    atexit.register(client.on_close)
    client.connect()




