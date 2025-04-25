from collections import defaultdict

def gen_index_maps(list_of_keys):
    k2i = {}
    i2k = {}
    for i, k in enumerate(list_of_keys):
        k2i[k]=i
        i2k[i]=k
    return k2i, i2k


def dynamic_dict():
    return defaultdict(dynamic_dict)


def init_mapping(keys,value):
    n_map = {}
    for k in keys:
        n_map[k]=value
    return n_map