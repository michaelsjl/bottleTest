#coding:utf-8
import hashlib
import os

buffer_size=65535
def get_file_md5(full_path):
    md5=hashlib.md5()
    try:
        with open(full_path, 'rb') as fp:
            buff=fp.read(buffer_size)
            while buff:
                md5.update(buff)
                buff=fp.read(buffer_size)
            return md5.hexdigest()
    except IOError:
        return 'read file error'

def get_file_ext(file_name):
    parts=file_name.split('.')
    return parts[-1] if len(parts)>1 else ''

def get_file_size(full_path):
    try:
        size=os.path.getsize(full_path)
        return size
    except Exception as err:
        return err
        