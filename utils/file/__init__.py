import os
import codecs
import re
import glob
import pandas as pd


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
        self.paths = {
            'SMEG': os.path.join(self.path, 'LOG_RASPROG/'),
            'RT6': os.path.join(self.path, 'LOG_RASPEEDI/'),
            'cal_rt6': os.path.join(self.path, 'LOG_CAL_RT6'),
            'calibre': os.path.join(self.path, 'CALIBRE')
        }

    def log_filter(self, dir_name):
        path = os.path.join(self.path, dir_name)
        files = list_dir(path)
        return [file.replace(path + '/', '').split('/') for file in files]

    def vin_err_filter(self, product, file_name):
        keys = [key for key in self.paths.keys() if key in product]
        if keys:
            files = glob.glob(os.path.join(self.paths[keys[0]], f"{keys[0]}*/{file_name}") + "*_Erreur_VIN.txt")
            if files:
                with open(files[0], 'r') as f:
                    data = f.read()
                return data
        return None

    def export_cal(self, file_name):
        cal_list = []
        path = self._select_path('LOG_ECU_IN')
        files = self.log_filter('LOG_ECU_IN')
        files = [file[0] for file in self.log_filter('LOG_ECU_IN') if '.txt' in file[0]]
        for file in files:
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

    def export_cal_xelon(self, file_name):
        cal_list = []
        path = self._select_path('LOG_ECU_IN')
        df = self._dataframe(path)
        data = df.pivot_table(index=['cal'], aggfunc='size')
        for key, value in data.items():
            if int(value) >= 3:
                rows = df[df['cal'] == key]
                cal_list.append(str(key) + ';' + ';'.join(rows['xelon'][:3]) + '\n')

        # Descending order for CAL numbers
        cal_list.sort(reverse=True)

        # Creation of the CAL list file
        with open(os.path.join(path, file_name), "w") as f:
            for cal in cal_list:
                f.writelines(cal)
        return len(cal_list)

    def _dataframe(self, path):
        data = {"xelon": [], "cal": []}
        files = self.log_filter('LOG_ECU_IN')
        files = [file[0] for file in self.log_filter('LOG_ECU_IN') if '.txt' in file[0]]
        for file in files:
            try:
                with open(os.path.join(path, file), "r") as f:
                    xelon = cal = None
                    for line in f.readlines():
                        if "NumXelon=" in line:
                            xelon = line.split("=")[1].strip()
                            if not re.match(r'^[A_Z]00\d{7}$', xelon):
                                xelon = None
                        if "TxtCALPSA=" in line:
                            cal = line.split("=")[1].strip()
                            if not re.match(r'^9[68]\d{8}$', cal):
                                cal = None
                    if xelon and cal:
                        data["xelon"].append(xelon)
                        data["cal"].append(cal)
            except UnicodeDecodeError:
                pass
            except FileNotFoundError as err:
                print(f"FileNotFoundError : {err}")
        return pd.DataFrame(data)

    def _select_path(self, dirname):
        path = os.path.join(self.path, dirname)
        if not os.path.exists(path):
            os.makedirs(path)
        return path


def handle_uploaded_file(f):
    file_url = "/tmp/{}".format(f)
    with open(file_url, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return file_url


def convert_utf8_to_ansi(oldfile, newfile):
    """
    :param oldfile: path to UTF8 file
    :param newfile: path to the ANSI file to be saved
    """
    # Open UTF8 text file
    with codecs.open(oldfile, 'r', 'utf8') as f:
        utfstr = f.read()

    # Transcode UTF8 strings into ANSI strings
    outansestr = utfstr.encode('mbcs')

    # Save the transcoded text in binary format
    with open(newfile, 'wb') as f:
        f.write(outansestr)
