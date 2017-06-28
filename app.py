#coding=utf-8
from bottle import Bottle,route,run,template,static_file,get,post,request,error
import MySQLdb
import hashlib
from json import dumps

app=Bottle()

@app.route('/')
def hello():
    return 'hello world'

@app.error(404)
def error404(error):
    return '404 error'

@app.route('/register')
def register():
    return template('register')

@app.route('/register', method='POST')
def do_register():
    name=request.forms.get('name')
    first_passwd=request.forms.get('first_password')
    second_passwd=request.forms.get('second_password')
    ok=register_info(name, first_passwd)
    if ok:
        return {'status':'ok'}
    else:
        return {'status':'error'}

def register_info(name, passwd):
    return True

@app.route('/login')
def login():
    return template('login')

@app.route('/login', method='POST')
def do_login():
    name=request.forms.get('name')
    password=request.forms.get('password')
    ok,reason = check_login_by_mysqldb(name, password)
    if ok:
        return {'status':'ok'}
    else:
        request.status=401
        return {'status':'error','reason':reason}

def check_login_by_mysqldb(name, password):
    if not name:
        return False,'name error'
    if not password:
        return False,'passwd error'
    try:
        conn = MySQLdb.connect(host='192.168.1.152',port=3308,user='ucheck',passwd='ucheck',db='uPlatform')
        cursor = conn.cursor()
        query = "SELECT employee_password FROM u_employee WHERE employee_ename='{0}';".format(name)
        print query
        if not cursor.execute(query):
            return False,'can not find data'
        sql_password = cursor.fetchone()
        calc_password = get_str_md5(password)
        print sql_password[0], calc_password
        if sql_password[0] == calc_password:
            return True,'login ok'
        else:
            return False,'passwd error'
                  
    except MySQLdb.Error as err:
        print ("mysql connect wrong:{0}".format(err))
        return False,'sql connect error'

    finally:
        cursor.close()
        conn.close()

@app.route('/upload')
def upload():
    return template('upload')

upload_path='C:/Users/michael_shu.SOUTHBAYTECH/Desktop/image/upload'
@app.route('/upload', method='POST')
def do_upload():
    filename=request.forms.get('filename')
    upload_file=request.files.get('filadata')
    upload_file.save(upload_path, overwrite=True)
    return {'status':'ok'}

root_path='C:/Users/michael_shu.SOUTHBAYTECH/Desktop/image/upload'
@app.route('/download/<filename:path>')
def download(filename):
    return static_file(filename, root=root_path, download=True)

@app.route('/static/<filename:path>')
def server_static(filename):
    return static_file(filename, root=root_path)
    
def get_str_md5(content):
    if not isinstance(content, (str, unicode)):
        return ''
    m = hashlib.md5()
    m.update(content)
    return m.hexdigest()

app.run(host='localhost',port=8081,debug=True)