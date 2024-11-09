import json
import csv
from functools import wraps
import time
import hashlib
import pickle
from logs import get_logger

logger = get_logger('share')


colors = {'HEADER': '\033[95m',
          'OKBLUE': '\033[94m',
          'OKCYAN': '\033[96m',
          'OKGREEN': '\033[92m',
          'WARNING': '\033[93m',
          'FAIL': '\033[91m',
          'ENDC': '\033[0m',
          'BOLD': '\033[1m',
          'UNDERLINE': '\033[4m'}


def save_pickle(var, path: str):
    with open(path, 'wb') as pickle_file:
        pickle.dump(var, pickle_file, pickle.HIGHEST_PROTOCOL)


def load_pickle(path: str):
    with open(path, 'rb') as pickle_file:
        return pickle.load(pickle_file)


def save_json(data, file):
    with open(file, "w", encoding='utf-8') as jf:
        json.dump(data, jf, ensure_ascii=False, indent=4)


def load_json(file):
    with open(file, "r", encoding='utf-8') as jf:
        data = json.load(jf)
    return data


def load_csv(file, delimiter=','):
    with open(file, "r", encoding='utf-8') as csv_file:
        for row in csv.reader(csv_file, delimiter=delimiter):
            yield row


class IncrementCounter:

    def __init__(self):
        self._value = 0

    def new_value(self):
        self._value += 1
        return self._value


def load_key_val(file: str):
    result = []
    with open(file, "r", encoding='utf-8') as key_val_file:
        for row in key_val_file.readlines():
            key_val_list = row.strip().split(',')
            result.append(
                {key_val.split('=')[0]: key_val.split('=')[1] for key_val in key_val_list if key_val.find('=') != -1})

    return result


def pars_key_val(row: str, key_list: [str]) -> dict:
    pars_data = {key: None for key in key_list}
    for key_val in row:
        for key in key_list:
            if key_val.startswith(f'{key}='):
                pars_data[key] = key_val.split('=')[1]
    return pars_data


def timeit(func):
    @wraps(func)
    def timeit_wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        total_time = end_time - start_time
        logger.info(f'Function {func.__name__}{args} {kwargs} Took {total_time:.4f} seconds')
        return result
    return timeit_wrapper


def get_hash(string: str):
    return hashlib.sha1(string.encode()).hexdigest()
