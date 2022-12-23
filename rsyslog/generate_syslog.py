import syslog
import time

def gen_syslog(t, n):
    for i in range(n):
        syslog.openlog("RAQ Testing:")
        syslog.syslog(level=syslog.LOG_INFO, "SYSLOG WRITE: {}:{}".format(t, i))
        syslog.closelog()
    return

def main():
    i = 0;
    while True:
        i = i + 1
        gen_syslog(i, 300);
        time.sleep(3);