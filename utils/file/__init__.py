import os
import glob


def list_dir(path, name=None):
    files = []
    list_file = glob.glob(path + '//*')
    for i in list_file:
        if os.path.isdir(i):
            files.extend(list_dir(i))
        else:
            files.append(i)
    if name:
        files = [file for file in files if name in file]
    return files


class LogFile:

    def __init__(self, path, name=None):
        self.files = list_dir(path, name)
        self.cal = self.log_filter('LOG_CAL')
        self.raspeedi = self.log_filter('LOG_RASPEEDI')
        self.rasprog = self.log_filter('LOG_RASPROG')
        self.calibre = self.log_filter('CALIBRE')

    def log_filter(self, dir_name):
        return [file for file in self.files if dir_name in file]
