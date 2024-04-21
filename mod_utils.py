

def read_config(filename):
    header = None
    mods =  {}
    with open(filename, "r") as fh:
        for line in fh:
            fields = line.strip().split(",")
            if header is None:
                header = list(map(lambda f: f.lower(), fields))
            else:
                datum = dict(zip(header,fields))
                mods[datum["id"]] = datum
    
    return list(mods.values())

def get_by_type(mods,type_):
    for datum in mods:
        if datum["type"] == type_:
            yield datum

def get_field(mods,field):
    for mod in mods:
        yield mod[field]
        