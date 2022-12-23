from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime
from time import sleep
 
totalsyslogWrites = 0
totalauthWrites = 0
totalkernWrites = 0
totalteamdWrites = 0
totalotherWrites = 0
 
class SyslogWatch(FileSystemEventHandler):
 
    def on_modified(self, event):
        dt = datetime.now()
        global totalteamdWrites
        global totalkernWrites
        global totalauthWrites
        global totalsyslogWrites
        global totalotherWrites
        with open("var_log_writes.txt", "w") as f:
            f.write("Syslog {} modified at:{}".format(event.src_path, dt.strftime('%Y-%m-%d %H:%M:%S.%f')))
 
        if "syslog" in event.src_path:
            totalsyslogWrites = totalsyslogWrites + 1
        elif "auth" in event.src_path:
            totalauthWrites = totalauthWrites + 1
        elif "kern" in event.src_path:
            totalkernWrites = totalkernWrites + 1
        elif "teamd" in event.src_path:
            totalteamdWrites = totalteamdWrites + 1
        else:
            totalotherWrites = totalotherWrites + 1
 
        return
 
evhandle = SyslogWatch()
obs = Observer()
obs.schedule(evhandle, path="/var/log/", recursive=False)
print("Observe Syslog")
obs.start()
 
while True:
    try:
        totalteamdWrites = 0
        totalkernWrites = 0
        totalauthWrites = 0
        totalsyslogWrites = 0
        totalotherWrites = 0
 
        sleep(10)
        print("\n\n------------------")
        print("In last 10 secs")
        print("Syslog writes {}".format(totalsyslogWrites))
        print("auth writes {}".format(totalauthWrites))
        print("kern writes {}".format(totalkernWrites))
        print("teamd writes {}".format(totalteamdWrites))
        print("other writes {}".format(totalotherWrites))
        print("------------------\n\n")
        pass
    except KeyboardInterrupt:
        obs.stop()

