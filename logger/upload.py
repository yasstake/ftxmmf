import os
import sys, subprocess, glob
from google.cloud import storage
from logger.util import *


def upload(file, root_name, bucket_name):
    staging_file = file + '.stage'
    done_file = file + '.done'

    os.rename(file, staging_file)

    f_org = file.split(root_name)[1]

    file_root = f_org.split('-')

    worker = file_root[0]
    year   = file_root[1]
    month  = file_root[2]
    day    = file_root[3].split('T')[0]

    print(worker, year, month, day)

    """Uploads a file to the bucket."""
    source_file_name = staging_file
    destination_blob_name = year + '/' + month + '/' + day + '/' + f_org

    #storage_client = storage.Client('bitmmf')
    #bucket = storage_client.get_bucket(bucket_name)
    #blob = bucket.blob(destination_blob_name)

    try:
        # blob.upload_from_filename(source_file_name)
        os.rename(staging_file, done_file)
    except:
        os.rename(staging_file, file)  # rename org file name when error



def recover_file(log_dir, prefix, suffix, time):
    '''
    recovery file
    :param log_dir: recovery file dir
    :param suffix: recovery file suffix e.g, '.current'
    :param time:   recovery file age(in sec)
    :return: None
    '''

    file_list = glob.glob(log_dir + os.sep + prefix + '*.log.gz' + suffix)
    now = unixtime_now()

    for file in file_list:
        stat = os.stat(file)
        if stat:
            print(file, stat.st_ctime, now)
            if stat.st_ctime + time < now:
                org_file_name = file.replace(suffix, '')
                print('recovery', org_file_name, file)
                os.rename(file, org_file_name)


if __name__ == "__main__":
    '''
    python3 -m logger.upload [dir_to_upload]
       - compress and upload files
       - clean up(delete) uploaded (old=2D Old) files
       - recover *.current file that is not changed for 6H
       - recover *.stage file that is not changed for 2H
    '''

    log_dir = os.sep + 'tmp'
    file_prefix = ''

    if len(sys.argv) == 2:
        log_dir = sys.argv[1]
    elif len(sys.argv) == 3:
        log_dir = sys.argv[1]
        file_prefix = sys.argv[2]

    file_list = glob.glob(log_dir + os.sep + file_prefix + '*.log')
    for file in file_list:
        if os.path.exists('/bin/gzip'):
            subprocess.run(['/bin/gzip', '-9', file])
        else:
            subprocess.run(['/usr/bin/gzip', '-9', file])

    file_list = glob.glob(log_dir + os.sep + file_prefix + '*.log.gz')
    for file in file_list:
        print('uploading,,,', file)
        upload(file, file_prefix, file_prefix)

    file_list = glob.glob(log_dir + os.sep + file_prefix + '*.log.gz.done')
    now = unixtime_now()
    for file in file_list:
        stat = os.stat(file)
        if stat:
            # print(file, stat.st_ctime, now)
            if stat.st_ctime + 24 * 60 * 60 * 2 < now:  # 2 days old
                os.remove(file)
                print("delete", file)

    #recovery staging file
    recover_file(log_dir, file_prefix, '.stage', 60*60*2)  #2H

    #recovery current file
    recover_file(log_dir, file_prefix, '.current', 60*60*6) #6H

