import time

files = [
    "/var/log/nginx/access.log",
    "/var/log/nvued.log",
    "/var/log/switchd.log",
    "/var/log/nv-cli.log",
    "/var/log/frr/frr.log"
]


import syslog
import random

def write_logs_to_files(frequency=1):
    """
    Write logs to files using syslog with given frequency
    Args:
        frequency: Number of seconds between log writes (default 1 second)
    """
    programs = {
        "/var/log/nvued.log": "nvued",
       # "/var/log/switchd.log": "switchd",
       # "/var/log/nv-cli.log": "nv-cli",
    }

    seq = 0
    while True:
        seq += 1
        for logfile in files:
            # Get program name for this log file
            program = programs.get(logfile)

            if program is None:
                continue

            # Generate random message
            message = f"PC LOG: {seq}"

            # Open connection to system logger
            syslog.openlog(program)

            # Write log with random priority
            priority = random.choice([syslog.LOG_INFO, syslog.LOG_WARNING, syslog.LOG_ERR])
            syslog.syslog(priority, message)

            # Close syslog connection
            syslog.closelog()
            print(f"Wrote log to {logfile} with seq:{seq} at {time.strftime('%Y-%m-%d %H:%M:%S.%f')}")

        # Wait for specified frequency
        time.sleep(1/frequency)

if __name__ == "__main__":
    write_logs_to_files()


