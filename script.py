import os
import sys
from pathlib import *
import shutil
import logging
import hashlib
import time


def deep_copy(folder_src, folder_rpl, logger, sleep_time):

    logger.info('synchronization started')

    for el in os.walk(folder_src):
        src_path = Path(el[0])
        rpl_path = Path(os.path.join(*[folder_rpl, *src_path.parts[1:]]))

        src_dirs = el[1]
        src_files = el[2]

        rpl_dirs, rpl_files = os.walk(rpl_path).__next__()[1:]

        for element in rpl_dirs + rpl_files:
            if element not in src_dirs + src_files:
                path = os.path.join(rpl_path, element)
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
                logger.info(f'{path} was deleted')

        for direct in src_dirs:
            path = rpl_path / direct
            if os.path.exists(path):
                # logger.info(f'{path} exists')
                pass
            else:
                os.mkdir(path)
                logger.info(f'{path} was created')

        for file in src_files:
            path = rpl_path / file
            if os.path.exists(path):
                # logger.info(f'{path} exists')
                original_hash = file_hash(src_path / file)
                replica_hash = file_hash(path)
                if not original_hash == replica_hash:
                    logger.info(f'{path} hash does not match the original file hash')
                    shutil.copyfile(src_path / file, path)
                    logger.info(f'{src_path / file} was copied to {path}')
            else:
                logger.info(f'{path} does not exist in replica')
                shutil.copyfile(src_path / file, path)
                logger.info(f'{src_path / file} was copied to {path}')

    logger.info('synchronization complete')
    logger.info(f'fall asleep for {sleep_time} seconds')


def setup_logger(name):
    log = logging.getLogger(name)
    log.setLevel(logging.INFO)
    file_handler = logging.FileHandler(log_path, 'w', 'utf-8')
    formatter = logging.Formatter('%(asctime)s - '
                                  '%(name)s - '
                                  '%(levelname)s - '
                                  '%(message)s')
    file_handler.setFormatter(formatter)
    log.addHandler(file_handler)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    log.addHandler(console_handler)

    return log


def file_hash(file_name):
    md5 = hashlib.md5()
    buf = 65536

    with open(file_name, 'br') as f:
        while True:
            data = f.read(buf)
            if not data:
                break
            md5.update(data)

    return md5.hexdigest()


if __name__ == '__main__':
    try:
        source_folder, replica_folder, synch_delay, log_path = sys.argv[1:]
    except BaseException as error:
        print(error)
    # source_folder, replica_folder, synch_delay, log_path = 'src', 'rpl', 1, 'log.log'

    log = setup_logger('copier')

    while True:

        deep_copy(source_folder, replica_folder, log, synch_delay)

        time.sleep(int(synch_delay))

