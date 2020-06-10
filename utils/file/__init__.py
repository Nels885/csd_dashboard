import os
import re
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
        # self.files = list_dir(path, name)
        self.path = os.path.join(path, 'LOGS')
        self.name = name
        self.calrt6 = self.log_filter('LOG_CAL_RT6')
        self.calrd45 = self.log_filter('LOG_CAL_RD45')
        self.raspeedi = self.log_filter('LOG_RASPEEDI')
        self.rasprog = self.log_filter('LOG_RASPROG')
        self.calibre = self.log_filter('CALIBRE')
        self.ecu = self.log_filter('LOG_ECU_IN')

    def log_filter(self, dir_name):
        files = list_dir(os.path.join(self.path, dir_name), self.name)
        return [file.split('/')[-1] for file in files if dir_name in file]

    def export_cal(self, file_name):
        cal_list = []
        path = os.path.join(self.path, 'LOG_ECU_IN')
        for file in self.ecu:
            with open(os.path.join(path, file), "r") as f:
                try:
                    for line in f.readlines():
                        if "TxtCALPSA=" in line:
                            value = line.split("=")[1]
                            if re.match(r'^9[68]\d{8}\n$', value) and not re.match(r'^9[68]F{6}80\n$', value):
                                cal_list.append(value)
                except UnicodeDecodeError:
                    pass

        # Descending order for CAL numbers
        cal_list.sort(reverse=True)

        # Creation of the CAL list file
        with open(os.path.join(path, file_name), "w") as f:
            for cal in cal_list:
                f.writelines(cal)
        return len(cal_list)


def handle_uploaded_file(f):
    file_url = "/tmp/{}".format(f)
    with open(file_url, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return file_url
