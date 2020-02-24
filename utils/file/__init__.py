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

    def __init__(self, path, name):
        # self.files = list_dir(path, name)
        self.path = os.path.join(path, 'LOGS')
        self.name = name
        self.calrt6 = self.log_filter('LOG_CAL_RT6')
        self.calrd45 = self.log_filter('LOG_CAL_RD45')
        self.raspeedi = self.log_filter('LOG_RASPEEDI')
        self.rasprog = self.log_filter('LOG_RASPROG')
        self.calibre = self.log_filter('CALIBRE')

    def log_filter(self, dir_name):
        files = list_dir(os.path.join(self.path, dir_name), self.name)
        return [file.split('/')[-1] for file in files if dir_name in file]
