import threading
from collections import deque
import time
import psutil
import tkinter as tk
import requests
import netifaces


url = "http://www.google.com"
timeout = 5
transfer_rate = deque(maxlen=1)

window = tk.Tk()
greeting = tk.Label(text="Retrieving data ..", fg="#f8f8f2", bg="#282a36",borderwidth=1, relief="raised", cursor="exchange")
greeting.grid()




def get_current_interface():
    
    try:        
        return netifaces.gateways()['default'][netifaces.AF_INET][1]
    except:
        return "Disconnected"

def calc_ul_dl(rate, dt=2, interface=get_current_interface()):
    t0 = time.time()
    counter = psutil.net_io_counters(pernic=True)[interface]
    tot = (counter.bytes_sent, counter.bytes_recv)

    while True:
        last_tot = tot
        time.sleep(dt)
        counter = psutil.net_io_counters(pernic=True)[interface]
        t1 = time.time()
        tot = (counter.bytes_sent, counter.bytes_recv)
        ul, dl = [(now - last) / (t1 - t0) / 1000.0
                  for now, last in zip(tot, last_tot)]
        rate.append((ul, dl))
        t0 = time.time()

def print_rate(rate):
    try:
        text = '⯅ {0:.0f}kB/s - ⯆ {1:.0f}kB/s'.format(*rate[-1])
        upload = '{0:.0f}kB/s'.format(rate[-1][0])
        download = '{0:.0f}kB/s'.format(rate[-1][1])
        print(text)
        return upload, download
    except IndexError:
        'UL: - kB/s/ DL: - kB/s'
        return "0", "0"
    
def check_connection():
    try:
        requests.get(url, timeout=timeout)
        return True
    except (requests.ConnectionError, requests.Timeout):
        return False

def run_thread():
    # Create the ul/dl thread and a deque of length 1 to hold the ul/dl- values
    t = threading.Thread(target=calc_ul_dl, args=(transfer_rate,2, get_current_interface()))    
    # The program will exit if there are only daemonic threads left.
    t.daemon = True
    t.start()



interface = get_current_interface()

def main_loop() :    
    time.sleep(1)
    if(interface is not get_current_interface()):
        run_thread()

    up,down = print_rate(transfer_rate)
    greeting["text"] ="["+get_current_interface()+"]  "+ u"\u21D1" + up +u" - \u21D3" +down

    if(check_connection()):
        greeting["fg"] = "#8be9fd"
    else:
        greeting["fg"] = "#ff5555"

    window.after(1000,main_loop)

def main():
    run_thread()


    positionDown = int(window.winfo_screenheight()- 20)
    window.title("netspeed")
    window.geometry("+{}+{}".format(0, positionDown))
    window.attributes('-alpha', 0.0)
    window.overrideredirect(1)
    window.call('wm', 'attributes', '.', '-topmost', True)
    
    
    window.after(1000,main_loop)
    window.mainloop()


if __name__ == "__main__":
    main()
