
import json
import traceback
from functools import wraps
import functools
import os
import socket
from datetime import datetime, timedelta, time, date
from pytz import timezone
import time
import re
from retrying import retry
import pandas as pd
import numpy as np 
import ntpath

class Read(object):
    def read_csv(self,directory):
        return pd.read_csv(directory,encoding="ISO-8859-1")

    def convert_to_array(self,df):
        df.to_records()
        np.asarray(df)

    def array_from_csv(self,directory):
        df = self.read_csv(directory)
        return self.convert_to_array(df)

class SupportingFunctions(Read):
    def now_date_time_eastern(self, adjusted_time=True, strf='%m/%d/%y %I:%M:%S %p', eastern_time=True):
        if eastern_time:
            val = datetime.now(timezone('US/Eastern'))
        else:
            val = datetime.utcnow()
        if adjusted_time:
            val = val.strftime(strf)
        return val

    def field_parse(self, fields_dict, key_name, null_value=None):
        try:
            return ", ".join([D[key_name] for D in fields_dict])
        except KeyError:
            return null_value


    def special_character_remove(self, s, replacer=None):
        if replacer:
            l = re.findall('[^a-zA-Z0-9\n\.]', s)
            l = [i for i in l if i != ' ']
            for i in l:
                s = s.replace(i, replacer)
        else:
            s = re.sub('[^a-zA-Z0-9\n\.]', ' ', s)
        return s


    def unicode_check_fix(self,s):
        try:
            return str(s)
        except:
            try:
                return s.decode('utf8')
            except:
                try:
                    return s.decode('utf8','ignore')
                except:
                    return self.special_character_remove(s)

    def unicode_fix_whole_dictionary_key(self, D):
        dictionary_destruct = D.items()
        transformed_tups = [(tup[0],SupportingFunctions().unicode_check_fix(tup[1])) for tup in dictionary_destruct]
        return dict(transformed_tups)


    def dictionary_index_try(self, D, key, alt='None', success_func=None):
        if isinstance(key, list) and len(key) == 2:
            try:
                r = D[key[0]][key[1]]
                if success_func:
                    r = success_func(r)
                return r
            except:
                return alt

        try:
            r = D[key]
            if success_func:
                r = success_func(r)
            return r
        except:
            return alt
    def string_between_pull_multiple(self, val, start='Select', end='From'):
        try:
            regex = start + '(.*?)' + end
            val = re.findall(regex, val, re.IGNORECASE)
            return val
        except AttributeError:  # if no parenthesis
            return val


class FileFunctions(object):
    def static_directory_get(self,name):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        directory = os.path.join(dir_path,'static',name)
        return directory

    def file_stat_from_directory(self,directory):
        modified = time.ctime(os.path.getmtime(directory))
        created = time.ctime(os.path.getctime(directory))
        extension = os.path.splitext(directory)[1]
        file_name = ntpath.basename(directory).replace(extension,'')
        return {
            'file_name':file_name,
            'created':created,
            'modified':modified,
            'directory':directory,
            'extension':extension
        }

    def files_from_directory(self,directory):
        files = os.listdir(directory)
        directories = [os.path.join(directory,file) for file in files]
        array = [self.file_stat_from_directory(directory) for directory in directories]
        return array


def log_creator_save_file(func_name,log_dict):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    directory = os.path.join(dir_path,'static','logs',func_name)
    with open(directory, 'w+') as outfile:
        json.dump(log_dict, outfile)


def pid_get_try():
    try:
        return os.getpid()
    except:
        return '-'

def log_creator_dict_create(func_name,status,start_time,start_date_time,error_message=''):
    end_time = time.time()
    end_date_time = SupportingFunctions().now_date_time_eastern(strf='%Y-%m-%dT%H:%M:%S.%fZ')
    duration = str(int(end_time - start_time))
    log_dict = {
        'start_time':start_time,
        'start_date_time':start_date_time,
        'end_time':end_time,
        'end_date_time':end_date_time,
        'duration':duration,
        'status':status,
        'pid':str(pid_get_try()),
        'error':error_message
    }
    return log_dict

def log_creator_log(func_name,start_time,start_date_time,status,error_message=''):
    log_dict = log_creator_dict_create(func_name,status,start_time,start_date_time,error_message=error_message)
    log_creator_save_file(func_name,log_dict)

def log_creator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        func_name = func.__name__
        start_time = time.time()
        start_date_time = SupportingFunctions().now_date_time_eastern(strf='%Y-%m-%dT%H:%M:%S.%fZ')
        def log(status,error_message=''):
            log_creator_log(func_name,start_time,start_date_time,status,error_message=error_message)
        log('starting')

        try:
            result = func(*args, **kwargs)
            status = 'Success'
            error_message = "-"  # 'No error! Smooth as a cucumber :)'
            log('success')
        except Exception as err:
            error_message = traceback.format_exc()
            print (error_message)
            status = 'Error'
            result = 'None'
            log('error',error_message=error_message)

    return wrapper
