from mod_utils import *
from ftp_utils import *
from ftplib import FTP
import os
import json

TARG_DIR = "local_maps"
def mkdirs(path):
    targdir = "%s" % path
    os.makedirs(targdir, exist_ok=True)
    return targdir

    
def to_coords(worldx,worldy,posx,posy,posz):
    xcoord = worldx*300+posx
    ycoord = worldy*300+posy
    return xcoord,ycoord,posz



def generate_teleport_from_spawnfile(mod,spawnfile):
    with open(spawnfile,"r") as fh:
                for line in fh:
                    if "worldX" in line:
                        args = line.strip().split("{")[1].split("}")[0].split(",")
                        params = {}
                        for arg in args:
                            field,value = arg.split("=")
                            params[field.strip()] = int(value.strip())

                        xcoord,ycoord,zcoord = to_coords(params["worldX"], params["worldY"], \
                            params["posX"], params["posY"], params["posZ"])
                        cmd = "/teleportto {x} {y} {z}".format(x=xcoord,y=ycoord,z=zcoord)
                        print("# mapname=%s, id=%s, coords=%s" % (mod["name"], mod["id"],json.dumps(params)))
                        print(cmd)
                        return


def generate_teleport_from_objectfile(mod,objectfile):
    with open(objectfile,"r") as fh:
        lines = list(fh.readlines())
        for match in ["SpawnPoint", "ParkingStall"]:
            for line in lines:
                if match in line:
                    args = line.strip().split("{")[1].split("}")[0].split(",")
                    params = {}
                    for arg in args:
                        field,value = arg.split("=")
                        params[field.strip()] = value.strip()

                    xcoord,ycoord,zcoord = params["x"], params["y"], params["z"]
                    cmd = "/teleportto {x} {y} {z}".format(x=xcoord,y=ycoord,z=zcoord)
                    print("# mapname=%s, id=%s, coords=%s" % (mod["name"], mod["id"],json.dumps(params)))
                    print(cmd)
                    return


def get_maps():
    mods = read_config("mods.txt")
    for mod in get_by_type(mods,"map"):
        filepath = "%s/%s/%s/media/maps" % (TARG_DIR, mod["id"], mod["map name"])
        for root,dirs,files in os.walk(filepath):
            for directory in dirs:
                subpath = filepath + "/" + directory                
                spawnfile = "%s/spawnpoints.lua" % subpath 
                objectfile = "%s/objects.lua" % subpath 
                paths = {}
                paths["local_spawn"] = spawnfile
                paths["local_object"] = objectfile
                paths["local_mapdir"] = subpath
                paths["local_maps"] =filepath 
                paths["local_mod"] = "%s/%s" % (TARG_DIR,mod["id"])
                paths["map_name"] = mod["map name"]
                paths["map_folder"] = directory

                paths["remote_mod"]= "/steamapps/workshop/content/108600/%s/mods" % mod["id"]
                paths["remote_mapdir"] = "/media/maps/%s" % paths["map_folder"]
                paths["remote_maps"] = "/media/maps" 
                paths["remote_spawn"] = "%s/spawnpoints.lua" % paths["remote_mapdir"]
                paths["mod"] = mod
                yield paths
     
def generate_teleports():
    print("=== Teleports ===")
    for paths in get_maps():
            spawnfile = paths["local_spawn"] 
            objectfile= paths["local_object"]
            if os.path.exists(spawnfile):
                generate_teleport_from_spawnfile(paths["mod"],spawnfile) 
            elif os.path.exists(objectfile):
                generate_teleport_from_objectfile(paths["mod"],objectfile) 
            else:
                print("# mapname=%s id=%s" % (paths["mod"]["name"],paths["mod"]["id"]))
                print("# NONE")

def generate_map_regions(): 
    print("=== Map Region Snippet===")
    for mod in get_maps():
        fmtstr = "               { name=\"%s\", file=\"%s\" },"
        print(fmtstr % (mod["map_name"], mod["remote_spawn"]))


def upload_mods_to_media_folder():
    ftp = login()
    for paths in get_maps():
        upload_folder(ftp,paths["local_maps"],paths["remote_maps"])
        pass

def download_maps():
    ftp = login()
    mods = read_config("mods.txt")
    for mod in get_by_type(mods,"map"):
        print("-> %s" % mod["name"])
        src = "/steamapps/workshop/content/108600/%s/mods" % mod["id"]
        dest = "%s/%s" % (TARG_DIR,mod["id"])
        download_folder(ftp,src,dest)

#download_maps()
generate_teleports()
#upload_mods_to_media_folder()
#generate_map_regions()