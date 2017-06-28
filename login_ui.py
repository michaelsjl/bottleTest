#coding:utf-8

import sys
import os
import threading
from PySide.QtCore import *
from PySide.QtGui import *
from process_data import *

image_ext=('exr','png','dpx')

class User():
    def __init__(self,name,passwd):
        self.name=name
        self.passwd=passwd

    def login(self):
        data={'name':self.name, 'password':self.passwd}
        try:
            res=requests.post(login_url,data=data,timeout=5)
            print res
            if res.status_code != 200:
                return False
            else:
                return True
        except:
            return False

class FileInfo(object):
    def __init__(self, file_name):
        self.name=file_name
        self.md5=''
        self.size=''
        self.extension=''

class FileManger(object):
    def __init__(self):
        self.total_count=0
        self.success_count=0
        self.fail_count=0

class SysStatus(object):
    def __init__(self):
        self.name=''
        self.login_status=False

class LoginApp(QLabel):
    def __init__(self):
        QLabel.__init__(self)
        self.setMinimumSize(QSize(300,200))
        self.setAlignment(Qt.AlignCenter)
        self.setWindowTitle('Logining...')

        self.name_text=QLineEdit(self)
        self.name_text.setMinimumWidth(150)
        self.name_text.move(75,30)

        self.passwd_text=QLineEdit(self)
        self.passwd_text.setMinimumWidth(150)
        self.passwd_text.move(75,60)
        self.passwd_text.setEchoMode(QLineEdit.Password)

        self.login_btn=QPushButton('Login',self)
        self.login_btn.setMinimumWidth(150)
        self.login_btn.move(75,100)
        self.login_btn.clicked.connect(self.do_login_slot)
    
    @Slot()
    def do_login_slot(self):
        name=self.name_text.text()
        passwd=self.passwd_text.text()
        login_status=login_proecss(name, passwd)
        if login_status:
            login.hide()
            southbay_app.mysys.name=name
            southbay_app.mysys.login_status=login_status
            southbay_app.show()
        else:
            QMessageBox.warning(self, 'WARN', 'LOGIN ERROR!')

    def closeEvent(self, event):
        login.hide()
        southbay_app.show()

class HelloWorldApp(QLabel):
    mysys=SysStatus()
    upload_file_signal=Signal()
    upload_file_finish_signal=Signal()
    upload_file_start_signal=Signal()
    current_value=0
    upload_status=FileManger()
    def __init__(self):
        QLabel.__init__(self)

        print 'welcome to southbay'
        self.setMinimumSize(QSize(600,400))
        self.setAlignment(Qt.AlignCenter)
        self.setWindowTitle('SouthbayTech')

        self.login_btn=QPushButton('no login? please login',self)
        self.login_btn.setMinimumWidth(145)
        self.login_btn.move(160,90)
        self.login_btn.clicked.connect(self.login_slot)

        self.upload_btn=QPushButton('Upload',self)
        self.upload_btn.setMinimumWidth(145)
        self.upload_btn.move(160,150)
        self.upload_btn.clicked.connect(self.upload_slot)

        self.download_btn=QPushButton('Download',self)
        self.download_btn.setMinimumWidth(145)
        self.download_btn.move(160,180)
        self.download_btn.clicked.connect(self.download_slot)

        self.upload_bar=QProgressBar(self)
        self.upload_bar.setGeometry(160, 210, 300, 20)

        self.upload_file_signal.connect(self.upload_file_signal_slot)
        self.upload_file_finish_signal.connect(self.upload_file_finish_signal_slot)
        self.upload_file_start_signal.connect(self.upload_file_start_signal_slot)
    
    def showEvent(self, event):
        if self.mysys.login_status:
            self.setWindowTitle('hello,'+self.mysys.name+'! Welcome to SouthbayTech!')
            self.login_btn.setVisible(False)
    
    def upload_file_process(self):
        self.upload_file_signal.emit()
    
    def upload_file_finish_process(self):
        self.upload_file_finish_signal.emit()

    def upload_file_start_process(self):
        self.upload_file_start_signal.emit()
    
    @Slot()
    def upload_file_signal_slot(self):
        self.current_value += 1
        self.upload_bar.setValue(self.current_value)
    
    @Slot()
    def upload_file_finish_signal_slot(self):
        print ('upload finashed! total[ %d ] success[ %d ] fail[ %d ].'\
        %(self.upload_status.total_count, self.upload_status.success_count, self.upload_status.fail_count))
    
    @Slot()
    def upload_file_start_signal_slot(self):
        self.current_value=0
        self.upload_status.success_count=0
        self.upload_status.fail_count=0

    @Slot()
    def login_slot(self):
        southbay_app.close()
        login.show()

    @Slot()
    def upload_slot(self):
        if not self.mysys.login_status:
            QMessageBox.warning(self, 'WARN', 'Please Login!')
            return

        dirt_path=QFileDialog.getExistingDirectory(self)
        dirt_path = dirt_path + '\\'
        list_files=os.listdir(dirt_path)
        list_upload_files=[]
        for file in list_files:
            if file.endswith(image_ext):
                list_upload_files.append(file)
        if not len(list_upload_files)>0:
            print 'no file need to upload'
            return
        
        self.upload_status.total_count=len(list_upload_files)
        self.upload_bar.setMinimum(0)
        self.upload_bar.setMaximum(self.upload_status.total_count)  
        self.upload_file_start_process()

        print 'start upload'
        t=threading.Thread(target=self.upload_thread_func, args=(dirt_path, list_upload_files, ))
        t.start()

    def upload_thread_func(self,dirt_path,list_files):
        for file_name in list_files:
            file_path = dirt_path + file_name
            upload_info=FileInfo(file_name)
            upload_info.md5=mytool.get_file_md5(file_path)
            upload_info.size=mytool.get_file_size(file_path)
            upload_info.extension=mytool.get_file_ext(file_name)

            up_status,reason = check_file_upload_status_by_sql(upload_info)
            if not up_status:
                self.upload_status.fail_count += 1
                self.upload_file_process()
                continue
            ok = upload_small_file(file_path)
            if ok:
                if reason=='file need to insert':
                    upload_insert_sql(upload_info)
                elif reason=='file need to update':
                    upload_update_sql(upload_info)

                self.upload_status.success_count += 1
                self.upload_file_process()
        
        self.upload_file_finish_process()
    
    @Slot()
    def download_slot(self):
        if not self.mysys.login_status:
            QMessageBox.warning(self, 'WARN', 'Please Login!')
            return

        dirt_path=QFileDialog.getExistingDirectory(self)
        list_names=select_all_pngfile_in_server()
        if not len(list_names)>0:
            return

        self.upload_status.total_count=len(list_names)
        self.upload_bar.setMinimum(0)
        self.upload_bar.setMaximum(self.upload_status.total_count)  
        self.upload_file_start_process()

        print 'start download'
        t=threading.Thread(target=self.download_thread_func, args=(dirt_path, list_names, ))
        t.start()

    def download_thread_func(self,dirt_path,list_files):
        for file in list_files:
            ok=download_small_file(dirt_path, file[0])
            if ok:
                self.upload_status.success_count += 1
                self.upload_file_process()
            else:
                self.upload_status.fail_count += 1
                self.upload_file_process()
        
        self.upload_file_finish_process()

if __name__ == '__main__':
    #login_status=False
    qt_app = QApplication(sys.argv)
    southbay_app=HelloWorldApp()
    southbay_app.show()
    login=LoginApp()
    qt_app.exec_()
    sys.exit()
