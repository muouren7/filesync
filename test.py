import ftputil
import config

# FTP 服务器的配置信息
ftp_host = config.host
ftp_user = config.user
ftp_passwd = config.password

# 连接到 FTP 服务器
with ftputil.FTPHost(ftp_host, ftp_user, ftp_passwd) as ftp:
    # 指定要遍历的起始目录，这里假设从根目录开始
    start_dir = '/'
    
    def list_files(ftp, path='/'):
        # 获取当前目录下的文件和文件夹列表
        entries = ftp.listdir(path)
        #print(entries)
        for entry in entries:
            full_path = ftp.path.join(path, entry)
            if ftp.path.isdir(entry):
                # 如果是文件夹，递归遍历
                print(f"Directory: {entry}")
                list_files(ftp, entry)
            else:
                # 如果是文件，打印文件路径
                print(f"File: {full_path}")
    
    # 调用函数开始遍历
    list_files(ftp, start_dir)