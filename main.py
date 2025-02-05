import time
import os
import ftputil
import config
import threading
from ftputil import FTPHost
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler





# 指定要监控的目录
path_to_monitor = "E:\\WorkSpace\\filesync"



class CustomFileHandler(FileSystemEventHandler):
    def on_any_event(self,event):
        
        ##如果是移动操作(修改文件 文件夹名称) 则取修改后的路径
        relative_path = os.path.relpath(event.dest_path,path_to_monitor).replace('\\','/') if event.event_type == 'moved' else os.path.relpath(event.src_path,path_to_monitor).replace('\\','/')
        with FTPHost(config.host, config.user, config.password) as host:

            def delete_dir_recursively(directory,ftp):
                    # 获取目录中的文件和子目录列表
                    files_and_dirs = ftp.listdir(directory)
                    
                    for item in files_and_dirs:
                        full_path = ftp.path.join(directory, item)
                        
                        # 如果是文件，则删除
                        if ftp.path.isfile(full_path):
                            ftp.remove(full_path)
                            print(f"Deleted file: {full_path}")
                        # 如果是目录，则递归删除
                        elif ftp.path.isdir(full_path):
                            delete_dir_recursively(full_path)
                            # 在递归删除子目录后，删除空目录本身
                            ftp.rmdir(full_path)
                            print(f"Deleted directory: {full_path}")
                    ftp.rmdir(directory)

            if event.is_directory == False:  ##如果是文件
                try:
                    ####上一级目录
                    directory = os.path.dirname(relative_path)
                    # fullfile = os.path.join(directory,os.path.basename(relative_path))
                    if event.event_type == 'created' or event.event_type == 'modified':   ##新增或修改情况 将文件进行覆盖上传
                        if directory:
                            # 确保远程目录存在
                            host.makedirs(directory, exist_ok=True)
                        host.upload(relative_path, relative_path)
                    
                    if event.event_type == 'deleted':   ##如果是删除文件
                        try:
                            host.remove(relative_path)
                        except ftputil.error.PermanentError as e:
                            if relative_path:
                                delete_dir_recursively(relative_path,host)

                    ## 如果是修改文件名称
                    if event.event_type == 'moved':
                        src = os.path.relpath(event.src_path,path_to_monitor).replace('\\','/')
                        host.rename(src,relative_path)
                except ftputil.error.PermanentError as e:
                   pass

            if event.is_directory == True:   ##如果是目录(文件夹)
                if relative_path:
                    ###创建
                    try:
                        if event.event_type == 'created':
                            host.makedirs(relative_path, exist_ok=True)
                        ###删除
                        if event.event_type == 'deleted':
                            #host.rmtree(relative_path,ignore_errors=True)
                            delete_dir_recursively(relative_path,host)
                        ###修改
                        if event.event_type == 'moved':
                            src = os.path.relpath(event.src_path,path_to_monitor).replace('\\','/')
                            host.rename(src,relative_path)
                    except ftputil.error.PermanentError as e:
                        pass

aa = 0
def sync():
    with ftputil.FTPHost(config.host, config.user, config.password) as ftp:
        entries = ftp.listdir("/")
        

    # global aa 
    # aa += 1
    # print("测试:{}".format(aa))
    threading.Timer(5, sync).start()



if __name__ == "__main__":

    threading.Timer(5, sync).start()

    # 创建事件处理器
    event_handler = CustomFileHandler()
    # 创建观察者并设置事件处理器
    observer = Observer()
    observer.schedule(event_handler, path=path_to_monitor, recursive=True)
    # 启动观察者
    observer.start()
    print("开始")
    try:
        # 保持脚本运行，以便持续监控
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        # 当用户按下 Ctrl+C 时退出
        observer.stop()
    # 等待观察者线程终止
    observer.join()
    #print("this is ")


    