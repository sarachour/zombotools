from mod_utils import *
from ftplib import FTP

def login():
    URL = "194.140.197.194"
    PORT = 28631 
    PASSWORD = "9ZxtUMse"
    USERNAME = "gpftp10303082587667454"
    ftp = FTP()  # connect to host, default port
    ftp.connect(host=URL, port=PORT)
    ftp.login(user=USERNAME, passwd=PASSWORD)
    return ftp 

def get_modnames():
    mods = read_config("mods.txt")
    ftp = login()

    for mod in mods:
        src = "/steamapps/workshop/content/108600/%s/mods" % mod["id"]
        file_list = []
        ftp.cwd(src)
        ftp.retrlines('LIST', lambda x: file_list.append(x.strip().split()))
        existing_files = list(map(lambda e: " ".join(e[8:]), file_list))
        for args in file_list:
            filename = " ".join(args[8:])
            if args[0].startswith("d"):
                info_path = src + "/"+filename+"/mod.info"
                with open("tmp.txt", 'wb+') as f:
                    ftp.retrbinary('RETR {}'.format(info_path), f.write)

                print(info_path)
                with open("tmp.txt", "r") as fh:
                    for line in fh:
                        if "name=" in line or "id=" in line:
                            field,value = line.strip().split("=")
                            if "id" in field:
                                mod["modid"] = value
                            else:
                                mod["modname"] = value

    with open("modinfo.csv", "w+") as fh:
        fh.write("id,modid,modname")
        for mod in mods:
            text = "%s,%s,%s\n" % (mod["id"], mod["modid"], mod["modname"])
            fh.write(text)

    print(mod)


def reorder_mods(order,mods):
    ord_mods = []
    for type_ in order:
        ord_mods += get_by_type(mods,type_)
    
    missing = []
    for mod in mods:
        if len(list(filter(lambda m: m["id"] == mod["id"],ord_mods))) == 0:
            missing.append(mod)
    
    ord_mods += missing
    assert(len(mods)==len(ord_mods))
    return ord_mods

def print_modlists():
    order = ["priority","map","core","overhaul","gameplay","tweaks","weaponsarmor","vehicles","items","music"]
    mods = read_config("mods.txt")
    mods = reorder_mods(order,mods)

    print("=== Mods by Name ===")
    text = ";".join(get_field(mods, "mod id"))
    print(text)

    print("=== Mods by ID ===")
    text = ";".join(get_field(mods, "id"))
    print(text)

print_modlists()
#get_modnames()