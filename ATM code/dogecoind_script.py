import subprocess
import psutil

def is_dogecoind_running():
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == 'dogecoind':
            return True
    return False

def start_dogecoind():
    if is_dogecoind_running():
        return "1"
    else:
        try:
            subprocess.Popen(['/home/dogecoinatm/dogecoin-1.14.6/bin/dogecoind'])
            return "1"
        except FileNotFoundError:
            return "0"
        except Exception as e:
            return f"0"

if __name__ == '__main__':
    status = start_dogecoind()
    print(status)
