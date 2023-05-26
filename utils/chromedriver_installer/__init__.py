import logging
import subprocess

logger = logging.getLogger('command')


def install():
    chrome_version = get_chrome_version()
    chromedriver_version = get_chromedriver_version()
    if get_major_version(chrome_version) != get_major_version(chromedriver_version):
        logger.error(f"Chromedriver {chromedriver_version} incompatible with google-chrome {chrome_version}")
    return get_chromedriver_path()


def get_chrome_version():
    try:
        output = subprocess.check_output("google-chrome -version", shell=True, encoding='utf-8').split(' ')
        return output[2]
    except Exception:
        return None


def get_chromedriver_version():
    try:
        output = subprocess.check_output("chromedriver -version", shell=True, encoding='utf-8').split(' ')
        return output[1]
    except Exception:
        return None


def get_chromedriver_path():
    try:
        return subprocess.check_output("which chromedriver", shell=True, encoding='utf-8').strip()
    except Exception:
        return None


def get_major_version(version):
    if isinstance(version, str):
        return version.split('.')[0]
    return None
