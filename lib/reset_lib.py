import http.client as httplib
import logging
import os
import socket
import subprocess

_logger = logging.getLogger(__name__)


def is_wifi_active():
    iwconfig_out = subprocess.check_output(
        'iwconfig wlan0', shell=True).decode('utf-8')
    wifi_active = True
    if "Access Point: Not-Associated" in iwconfig_out:
        wifi_active = False

    return wifi_active


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('8.8.8.8', 80))
        IP = s.getsockname()[0]
    except Exception:
        while not is_wifi_active():
            if not have_internet():
                IP = '127.0.0.1'
                break
            else:
                IP = get_ip()
    finally:
        s.close()
    return IP
 


def reset_to_host_mode():
    os.system('sudo wifi-connect --portal-ssid "RFID Attendance System"')


def update_repo():
    os.chdir('/home/pi/ras')
    os.system("sudo git fetch origin")
    os.system('sudo git reset --hard origin/refactoring_2')

def reboot():
    print("rebooting")
    os.system('sudo reboot')

def run_tests():
    os.chdir('/home/pi/ras')
    os.system('sudo sh run_tests.sh')
    
def have_internet():
    _logger.debug("check internet connection")
    conn = httplib.HTTPConnection("www.google.com", timeout=10)
    try:
        conn.request("HEAD", "/")
        _logger.debug("Have internet")
        conn.close()
        return True
    except Exception as e:
        _logger.debug(e)
        conn.close()
        return False
