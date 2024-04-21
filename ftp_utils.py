from ftplib import FTP
import os

def mkdirs(path):
    targdir = "%s" % path
    os.makedirs(targdir, exist_ok=True)
    return targdir


def read_ftp_config():
    settings = {}
    with open("ftp.txt","r") as fh:
        for line in fh:
            name,value = line.strip().split("=")
            settings[name] = value
    return settings


def login():
    cfg = read_ftp_config()
    ftp = FTP()  # connect to host, default port
    ftp.connect(host=cfg["URL"], port=int(cfg["PORT"]))
    ftp.login(user=cfg["USERNAME"], passwd=cfg["PASSWORD"])
    return ftp 



def upload_folder(ftp,src,dst):
    ftp.cwd(dst)  
    file_list = []
    ftp.retrlines('LIST', lambda x: file_list.append(x.strip().split()))
    existing_files = list(map(lambda e: " ".join(e[8:]), file_list))
    for root,dirs,files in os.walk(src):
        for direc in dirs:
            if not direc in existing_files:
                ftp.mkd(direc)
            upload_folder(ftp,root+"/"+direc, dst+"/"+direc)

        for file in files:
            local_filepath = root + "/" + file
            remote_filepath = dst + "/" + file
            if file in existing_files:
                continue
            
            ftp.storbinary('STOR ' + remote_filepath, open(local_filepath,'rb'))




def download_folder(ftp,src,dst):
    ftp.cwd(src)  
    file_list = []
    result = ftp.retrlines('LIST', lambda x: file_list.append(x.strip().split()))
    mkdirs(dst)
    for args in file_list:
        filename = " ".join(args[8:])
        if args[0].startswith("d"):
            subdir_src = "%s/%s" % (src,filename)
            subdir_dst = "%s/%s" % (dst,filename)
            download_folder(ftp,subdir_src, subdir_dst)
        else:
            src_file = "%s/%s" % (src,filename)
            dest_file = "%s/%s" % (dst,filename)
            print(dest_file)
            if os.path.exists(dest_file):
                continue

            with open(dest_file, 'wb+') as f:
                ftp.retrbinary('RETR {}'.format(src_file), f.write)
            f.close()
            print("file!")


