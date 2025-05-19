# This script is used to watch the /var/log directory for changes
# It will count the number of writes to each file in the directory
# and print the results to the console

import json

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime
from time import sleep


'''
Stores
results = { "file_name": { "count": 0, "frequency": 0 } }
'''
results = {
}
start_time = datetime.now()

class SyslogWatch(FileSystemEventHandler):

    def on_modified(self, event):
        dt = datetime.now()
        global results
        with open("var_log_writes.txt", "w") as f:
            f.write("Syslog {} modified at:{}".format(event.src_path, dt.strftime('%Y-%m-%d %H:%M:%S.%f')))
            print("Syslog {} modified at:{}".format(event.src_path, dt.strftime('%Y-%m-%d %H:%M:%S.%f')))

        # skip for journal files
        if event.src_path.endswith(".journal"):
            return

        if event.src_path not in results:
            results[event.src_path] = { "count": 0, "frequency": 0 }

        results[event.src_path]["count"] += 1

        # Calculate frequency
        time_diff = datetime.now() - start_time
        results[event.src_path]["frequency"] = results[event.src_path]["count"] / time_diff.total_seconds()

        return

evhandle = SyslogWatch()
obs = Observer()
# watch all files in /var/log directory including subdirectories
obs.schedule(evhandle, path="/var/log/", recursive=True)
print("Observe Syslog")
obs.start()

while True:
    try:

        sleep(10)
        print("\n\n------------------")
        now = datetime.now()
        print("{}".format(now.strftime('%Y-%m-%d %H:%M:%S')))
        print("------------------")
        #for file_name, file_data in results.items():
        #    print("{}: {}".format(file_name, file_data["count"]))

        pass
    except KeyboardInterrupt:
        obs.stop()
        break

# write results to json file
with open("var_log_results.json", "w") as f:
    json.dump(results, f)

