#coding:utf-8

import requests
import urllib
import webbrowser
import mydb
import mytool
import json

login_url='http://localhost:8081/login'
upload_url='http://localhost:8081/upload'
download_url='http://localhost:8081/download'
local_db_path=r'C:\Users\michael_shu.SOUTHBAYTECH\Desktop\python\bottleTest\test.db'


def login_proecss(name, passwd):
    data={'name':name, 'password':passwd}
    try:
        res=requests.post(login_url, data=data, timeout=5)
        if not res.status_code == 200:
            return False
        res_dict=eval(res.text)
        if not res_dict['status'] == 'ok':
            return False

        return True
    except Exception,err:
        print err
        return False

def upload_insert_sql(file_info):
    sql="INSERT INTO picture_info (name,md5,size,ext) VALUES ('{0}','{1}','{2}','{3}');"
    sql=sql.format(file_info.name, file_info.md5, file_info.size, file_info.extension)
    try:
        with mydb.DB(local_db_path) as my_db:
            if my_db.insert(sql):
                return True
            else:
                return False
    except:
        return False

def upload_update_sql(file_info):
    sql="UPDATE picture_info SET md5='{0}', size='{1}' WHERE name='{2}';"
    sql=sql.format(file_info.md5, file_info.size, file_info.name)
    try:
        with mydb.DB(local_db_path) as my_db:
            if my_db.update(sql):
                return True
            else:
                return False
    except:
        return False
    
def check_file_upload_status_by_sql(file_info):
    sql="SELECT md5 FROM picture_info WHERE name='{0}';"
    sql=sql.format(file_info.name)
    try:
        with mydb.DB(local_db_path) as my_db:
            if not my_db.select(sql):
                return False, 'sql err'
            sql_md5=my_db.fetchone()
            if not sql_md5:
                return True, 'file need to insert'
            if not sql_md5==file_info.md5:
                return True, 'file need to update'

            return  False, 'file exits'
    except:
        return False, 'sql error'

def upload_small_file(file_path):
    try:
        data={'filename': file_path}
        files={'filadata':open(file_path, 'rb')}
        res=requests.post(upload_url, data=data, files=files, verify=False)
        if res.status_code == 200:
            return True
        else:
            return False
    except:
        return False

def select_all_pngfile_in_server():
    sql="SELECT name FROM picture_info WHERE ext='png';"
    try:
        with mydb.DB(local_db_path) as my_db:
            if not my_db.select(sql):
                return []
            return my_db.fetchall()
    except:
        return []

def download_small_file(file_path, file_name):
    root_file_name=download_url+'/'+file_name
    download_file_name=file_path+'/'+file_name
    try:
        res=requests.get(root_file_name, stream=True)
        if not res.status_code==200:
            return False
        with open(download_file_name, 'wb') as f:
            for chunk in res:
                f.write(chunk)
        return True
    except:
        return False

def open_login_browser():
    print webbrowser.open(login_url, new=0, autoraise=True)