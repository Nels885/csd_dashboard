import os
import glob


def list_dir(path, name=None):
    files = []
    list_file = glob.glob(path + '//*')
    for i in list_file:
        if os.path.isdir(i):
            files.extend(list_dir(i))
        if not os.path.isdir(i):
            files.append(i)
    if name:
        files = [x for x in files if name in x]
    return files
