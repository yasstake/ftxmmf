from datetime import datetime
import os

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
    dt = datetime.fromtimestamp(time)
    iso = dt.date().isoformat() + 'T' + dt.time().isoformat()
    return iso


def unixtime_now():
    dt = datetime.utcnow()
    return dt.timestamp()


class Logger:
    '''logging file utility'''
    def __init__(self, log_file_dir=None, flag_file_name=None, id=None):
        self.log_file_root_name = None
        self.log_file_name = None

        if log_file_dir:
            self.log_file_dir = log_file_dir
        else:
            self.log_file_dir = os.sep + "tmp"

        if flag_file_name:
            self.flag_file_name = flag_file_name
        else:
            self.flag_file_name = os.sep + "tmp" + os.sep + self.get_process_name()

        self.last_time = 0
        self.terminate_count = 200
        self.terminated_by_peer = False
        if id:
            self.pid = id
        else:
            self.pid = str(os.getpid())

        self.reset()

        self.flag_file_name = flag_file_name

        if not self.fix_file:
            self.rotate_file()

    def get_process_name(self):
        return 'LOG'

    def __del__(self):
        # self.dump_message()
        self.rotate_file()
        self.remove_terminate_flag()

    def get_flag_file_name(self):
        return self.flag_file_name

    def create_terminate_flag(self):
        self.remove_terminate_flag()
        file_name = self.get_flag_file_name()
        with open(file_name + "tmp", "w") as file:
            file.write(self.get_process_id())
            file.close()
            os.rename(file_name + "tmp", file_name)

    def check_terminate_flag(self):
        file_name = self.get_flag_file_name()

        if os.path.isfile(file_name):
            with open(file_name, "r") as file:
                id = file.readline()
                if id != self.get_process_id():
                    self.terminate_count = self.terminate_count - 1
                    if self.terminate_count == 0:
                        return True
        return False

    def get_process_id(self):
        return self.pid

    def remove_terminate_flag(self):
        file_name = self.get_flag_file_name()
        if os.path.isfile(file_name):
            os.remove(file_name)

    def rotate_file(self):
        if self.log_file_name:
            if os.path.isfile(self.log_file_name):
                os.rename(self.log_file_name, self.log_file_root_name)

        time_string = unixtime_to_iso(unixtime_now()).replace(":", "-").replace('+', '-')

        self.log_file_root_name = self.log_file_dir + os.sep + self.get_process_name() + '-' \
                                  + self.get_process_id() + '-' + time_string + ".log"

        self.log_file_name = self.log_file_root_name + ".current"

    def write(self, message):
        file_name = self.log_file_name

        with open(file_name, "a") as file:
            file.write(message)
