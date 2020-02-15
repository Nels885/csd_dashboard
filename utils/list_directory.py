import glob
import os.path


def list_directory(path, name=None):
    file = []
    if name:
        list_file = glob.glob(path + '//' + name + '*')
    else:
        list_file = glob.glob(path + '//*')
    for i in list_file:
        if os.path.isdir(i):
            file.extend(list_directory(i))
        else:
            file.append(i)
    return file
