#  Linux Rsyslog disk write improvement [SONiC]

# Table of Contents
- [ 1. Linux logging system:](##Linux-logging-system)
- [2. Observation](#2-observation)


## Linux logging system:
Below diagram depicts the components involved in Linux logging,

![](https://github.com/praveen-li/equilibrium/blob/main/rsyslog/rsyslogimage2022-7-27_18-1-53.png)

### Kernel Logs:

Kernel logs are stored in Kernel Ring Buffer. Each printk() call in kernel puts a log message in this ring buffer. Command 'dmsg' can be used to read kernel logs. To read from kernel ring buffer, user process such as rsyslod uses character device file /proc/kmsg. File /proc/kmsg is read only channel to get logs from kernel.

We can see who is using this file. Usually rsyslogd will be one of the process reading it.

```
$ sudo fuser /proc/kmsg
/proc/kmsg:          1646256
$ ps aux | grep 1646256
root     1646256  0.0  0.2 454488 11008 ?        Ssl  00:51   0:57 /usr/sbin/rsyslogd -n
```

Rsyslogd inserts a module 'imklog' on start up, which is responsible to read /proc/kmsg.

### User Space Logs:
Systemd takes care of logs from user process and from services. Usually syslog() system call will push a log to systemd from user process. Systemd has support for multiple channels, facilities and severities for logging. These logs can be read via /dev/log file.

check user for /dev/log
```
$ sudo fuser /dev/log
/run/systemd/journal/dev-log:     1   339  1099 201927 202027 202412 202894 203072 203764 203780 203781 203800 203809
$ ps aux | grep 339
root         339  0.0  0.3  47544 13812 ?        Ss   Jun24  17:33 /lib/systemd/systemd-journald
admin@host $ ps aux | grep rsyslogd
root        1099  0.0  0.0 223804  3248 pts/0    Sl   Jun24   0:00 /usr/sbin/rsyslogd -n -iNONE
root      201562  0.1  0.1 454488  7720 ?        Ssl  Jul26   2:56 /usr/sbin/rsyslogd -n
root      201927  0.0  0.0 223804  3580 pts/0    Sl   Jul26   0:00 /usr/sbin/rsyslogd -n -iNONE
root      202027  0.0  0.0 223804  3824 pts/0    Sl   Jul26   0:00 /usr/sbin/rsyslogd -n -iNONE
root      202412  0.0  0.1 223804  5768 pts/0    Sl   Jul26   0:17 /usr/sbin/rsyslogd -n -iNONE
root      202894  0.0  0.0 223804  3732 pts/0    Sl   Jul26   0:26 /usr/sbin/rsyslogd -n -iNONE
root      203072  0.0  0.0 223804  3596 pts/0    Sl   Jul26   0:00 /usr/sbin/rsyslogd -n -iNONE
root      203764  0.0  0.1 223804  5696 pts/0    Sl   Jul26   0:00 /usr/sbin/rsyslogd -n -iNONE
root      203780  0.0  0.0 223804  3588 pts/0    Sl   Jul26   0:00 /usr/sbin/rsyslogd -n -iNONE
root      203781  0.0  0.0 223804  3532 pts/0    Sl   Jul26   0:00 /usr/sbin/rsyslogd -n -iNONE
root      203800  0.0  0.0 223804  3612 pts/0    Sl   Jul26   0:00 /usr/sbin/rsyslogd -n -iNONE
root      203809  0.0  0.1 223804  5628 pts/0    Sl   Jul26   0:00 /usr/sbin/rsyslogd -n -iNONE
```

Rsyslogd is reading /dev/log device file, via many processes. The module responsible to read /dev/log in rsyslogd is imuxsock.

Rsyslogd module information can be found from the threads running under rsyslogd.

```
$ ps -p 201562
    PID TTY          TIME CMD
 201562 ?        00:02:57 rsyslogd
$ ps -T -p 201562
    PID    SPID TTY          TIME CMD
 201562  201562 ?        00:00:00 rsyslogd
 201562  201563 ?        00:00:53 in:imuxsock
 201562  201564 ?        00:00:00 in:imklog
 201562  201565 ?        00:00:00 in:imudp
 201562  201568 ?        00:00:00 in:imtcp
 201562  201569 ?        00:02:02 rs:main Q:Reg
 201562  201571 ?        00:00:00 in:imtcp
 201562  201572 ?        00:00:00 in:imtcp
 201562  201573 ?        00:00:00 in:imtcp
 201562  201574 ?        00:00:00 in:imtcp
```


Right now rsyslogd is running only Main Queue Worker thread to process log queue, more on that below.


## Rsyslogd:

Rsyslogd maintains a main Queue (Usual size 10k Messages) to store logs. 'Main Queue Worker' thread parses the logs. Main Queue worker thread may write the log directly to log file such as /var/log/syslog or may write in an action queue. In latest versions of rsyslogd, main queue is also known as ruleset queue and it is possible to have multiple ruleset/main queues and multiple main queue worker threads.

![](https://github.com/praveen-li/equilibrium/blob/main/rsyslog/rsyslogimage2022-7-28_10-18-10.png)

Rsyslog supports action queues, where main worker thread can write the logs. Action queue are used for performance tuning as per receiver of logs. Receiver of logs can be a remote system or the log file on local host machine. Action queue are by default of type 'Direct' which means no queue. Other types are 'FixedArray', 'LinkedList' and 'Disk'. By default deque batch size from action queue is 128 messages.

In few OS, files under /var/log/ are modified by rsyslog with high frequency due to amount of logs, which resulted in more frequent SSD failures. Below config can be used in /etc/rsyslog.conf for disk write improvement:

```
action(type="omfile" file="/var/log/syslog" template="Template"
    flushOnTXEnd="off" asyncWriting="on" flushInterval="5" ioBufferSize="64k")
```

In above Config, a non-direct Action queue is added for /var/log/syslog writes. Here:

    type=omfile:      modules, which writes to a file.

    flushOnTXEnd:  If off rsyslogd will wait, till buffer is full or flushInterval is passed before invoking action queue worker to write in log file.
    
    asyncWriting:    By default off. If on, Action queue will have separate thread for Action queue workers with double buffer for logs in action queue. Flush Interval will be ignored, if asyncWriting is off.
    
    flushInterval:     Action queue workers will write to file after expire of this period if there is 1+ logs in queue.
    
    ioBufferSize:      Size of Action queue in bytes.

Restart rsyslogd for new config to take effect.

```
sudo systemctl restart rsyslog.service
```

## Testing:

### /var/log/syslog file write improvement.

By using below libraries a test script is written to watch writes in /var/log/ folder. [Code not shared in this document]

```
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
```

Using syslog module in python, another script can be written to push N (600 for example below) logs per 10 secs.  [Code not shared in this document]

#### Observe file write per 10 secs before new rsyslog config:

```
------------------
In last 10 secs
------------------
Syslog writes 71
auth writes 3
kern writes 0
teamd writes 3
other writes 1
 
------------------
In last 10 secs
------------------
Syslog writes 87
auth writes 0
kern writes 0
teamd writes 5
other writes 0
 
------------------
```

Syslog files was modified around 65-85 times within each 10 secs period. Output for only 20 secs is copied above to save space.

#### Observe file write per 10 secs after new rsyslog config:

```
------------------
In last 10 secs
------------------
Syslog writes 2
auth writes 0
kern writes 0
teamd writes 0
other writes 0
 
------------------
In last 10 secs
------------------
Syslog writes 4
auth writes 0
kern writes 0
teamd writes 4
other writes 0
 
-----------------
```

With 64k main memory, disk write by rsyslog are reduced by 95%. 

### Verify disk write are done before rsyslogd\system shutdown, so that logs are always saved

#### Rsyslog restart test

Change the Config to write once in 2 mins with 128k buffer:


```
action(type="omfile" file="/var/log/syslog"   flushOnTXEnd="off" asyncWriting="on" flushInterval="120" ioBufferSize="128k")
```

Then let`s push only 5 syslogs per 5 secs (120 logs per 2 minutes), which is not suffiecient to fill 128 k with in 2 mins.

Observe syslog file is written once per 2 mins.

```
Syslog /var/log/syslog modified at:2022-08-09 05:33:49.683308
Syslog /var/log/syslog modified at:2022-08-09 05:35:49.695919
Syslog /var/log/syslog modified at:2022-08-09 05:37:52.382366
```

stop pushing syslogs and mark specific last syslog messsage at 05:38.07,  with end marker messsage as  66:4

```
Writing at:2022-08-09 05:38:07.499906
Writing: PC print 66:4
```


restart rsyslogd service, verify that syslog file is written same time.

```
$ date && sudo service rsyslog restart
Tue 09 Aug 2022 05:38:12 AM UTC
Syslog /var/log/syslog modified at:2022-08-09 05:38:12.712411
```


make sure last messsage i.e. 66:4 is present in syslog file.

```
Aug  9 05:38:07.501260 host INFO syslog_exe: PC print 66:0
Aug  9 05:38:07.501542 host INFO syslog_exe: PC print 66:1
Aug  9 05:38:07.501715 host INFO syslog_exe: PC print 66:2
Aug  9 05:38:07.501882 host INFO syslog_exe: PC print 66:3
Aug  9 05:38:07.502065 host INFO syslog_exe: PC print 66:4
```

#### System Reboot Test :

Change the Config to write once in 2 mins with 128k buffer:

```
action(type="omfile" file="/var/log/syslog"   flushOnTXEnd="off" asyncWriting="on" flushInterval="120" ioBufferSize="128k")
```

Then let`s push only 5 syslogs per 5 secs (120 logs per 2 minutes), which is not suffiecient to fill 128 k with in 2 mins.

Observe syslog file is written once per 2 mins.

```
Syslog /var/log/syslog modified at:2022-08-09 06:01:27.855368
Syslog /var/log/syslog modified at:2022-08-09 06:03:32.585908
```
End marker at 06:03:42, i.e. look for 48:4 in syslog file

```
Writing at:2022-08-09 06:03:42.692070
Writing: PC print 48:4
```

reboot system

```
$ date && sudo reboot
Tue 09 Aug 2022 06:03:50 AM UTC
requested COLD shutdown
```

uptime:

```
$ uptime
 06:08:18 up 3 min,  1 user,  load average: 0.52, 0.67, 0.31
```

syslog write before reboot:

```
Syslog /var/log/syslog modified at:2022-08-09 06:03:59.581341
```

marker present is syslog:

```
Aug  9 06:03:42.693518 host INFO syslog_exe: PC print 48:4
```

Thanks a ton !!!
