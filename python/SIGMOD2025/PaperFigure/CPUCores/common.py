import numpy as np
import time
import operator
import re
import pandas as pd
from matplotlib.ticker import FuncFormatter, MaxNLocator, LogLocator, LogFormatter
from collections import namedtuple
from globalvalues import THROUGHPUT_LIMIT, L0FNUM_LIMIT, CMPSIZE_LIMIT, FLUSHSIZE_LIMIT, RTWSFREQ_LIMIT, P99TAILLATENCY_LIMIT, PATH, WS_THROUGHPUT,XYLABEL_FONTSIZE,AVG_THROUGHPUT_LIMIT
from globalvalues import CMPSIZE_LIMIT_TOTAL_GB, ARRIVAL_RATE, TOTAL_OPS, X_AXIS, AVG_LATENCY_LIMIT,STEPS, XSTART, XEND
from globalvalues import XYLABEL_SIZE, XYTICKS_SIZE, TITLE_SIZE, LEGEND_SIZE, LINE_WIDTH, GRAY_LINE_WIDTH, TICK_WIDTH, TICK_LENGTH
FIGPATH = PATH

def match_level(file_Lx):
    if file_Lx == '"files_L0":' or file_Lx == '"files_L0"':
        return 0
    elif file_Lx == '"files_L1":' or file_Lx == '"files_L1"':
        return 1
    elif file_Lx == '"files_L2":' or file_Lx == '"files_L2"':
        return 2
    elif file_Lx == '"files_L3":' or file_Lx == '"files_L3"':
        return 3
    elif file_Lx == '"files_L4":' or file_Lx == '"files_L4"':
        return 4
    elif file_Lx == '"files_L5":' or file_Lx == '"files_L5"':
        return 5
    elif file_Lx == '"files_L6":' or file_Lx == '"files_L6"':
        return 6
    elif file_Lx == '"files_L7":' or file_Lx == '"files_L7"':
        return 7


def match_level_cmp(input, output):
    if input == 0:
        if output == 0:
            return 0
        else:
            return 1
    elif input == 1:
        return 2
    elif input == 2:
        return 3
    elif input == 3:
        return 4
    elif input == 4:
        return 5
    elif input == 5:
        return 6
    elif input == 6:
        return 7


# -------------------------------------------------------Get Information-------------------------------------------------------#
def rocksdb_starttime(filename):
    f = open(filename, 'r')
    eachrow = f.readline()
    sep_eachrow_space = eachrow.split()
    date_time_str = sep_eachrow_space[0]
    start_time_struct = time.strptime(date_time_str, "%Y/%m/%d-%H:%M:%S.%f")
    start_time = int(time.mktime(start_time_struct))
    f.close()
    return start_time

def max_overlapping_cmp(tasks):
    events = []
    for i, (start, end) in enumerate(tasks):
        events.append((start, 'start', i))
        events.append((end, 'end', i))

    # Sort events by time; if two events have the same time, start events come before end events
    events.sort(key=lambda x: (x[0], 0 if x[1] == 'start' else 1))

    max_overlap = 0
    current_overlap = 0
    active_tasks = set()
    max_intervals = set()

    for event in events:
        time, event_type, task_index = event
        if event_type == 'start':
            current_overlap += 1
            active_tasks.add(task_index)
            if current_overlap > max_overlap:
                max_overlap = current_overlap
                max_intervals = active_tasks.copy()
            elif current_overlap == max_overlap:
                max_intervals.update(active_tasks)
        else:
            if current_overlap == max_overlap:
                max_intervals.update(active_tasks)
            active_tasks.remove(task_index)
            current_overlap -= 1

    # Extract the original intervals corresponding to the max overlap
    result_intervals = [tasks[i] for i in max_intervals]

    return max_overlap, result_intervals
def Compaction_duration(filename):
    db_start_time = rocksdb_starttime(filename)
    f = open(filename, 'r')
    eachrow = f.readline()
    started_ids = []
    started_infos = []
    cmp_started_times = []
    cmp_started_size = []
    finished_ids = []
    finished_infos = []
    cmp_times = [[], [], [], [], [], [], [], []]  # 00,01,12,23,34,45,56,67
    cmp_size = [[], [], [], [], [], [], [], []]

    while (eachrow):
        sep_eachrow_comma = eachrow.strip().split(',')
        sep_eachrow_space = eachrow.split()
        if ' "event": "compaction_started"' in sep_eachrow_comma:
            for s in sep_eachrow_comma:
                if operator.contains(s, "job"):
                    job_str = s
                elif operator.contains(s, "files_L"):
                    input_level_str = s
                elif operator.contains(s, "input_data_size"):
                    input_size_str = s
            # job_id
            job_id = int(job_str.split(":")[1])
            # input_level
            file_Lx = input_level_str.split(":")[0]
            input_level = match_level(file_Lx.split()[0])
            # input_size
            input_size_str = input_size_str.split()[1]
            input_size_bytes = int(input_size_str.split('}')[0])
            input_size_mb = int(input_size_bytes / (1024 * 1024))
            # cur_time
            date_time_str = sep_eachrow_space[0]
            cur_time_struct = time.strptime(date_time_str, "%Y/%m/%d-%H:%M:%S.%f")
            cur_time = int(time.mktime(cur_time_struct))
            sec = cur_time - db_start_time

            started_ids.append(job_id)
            started_info = [input_level, input_size_mb, sec]
            started_infos.append(started_info)
            cmp_started_times.append(sec)
            cmp_started_size.append(input_size_mb)

        if ' "event": "compaction_finished"' in sep_eachrow_comma:
            for s in sep_eachrow_comma:
                if operator.contains(s, "output_level"):
                    output_level_str = s
                elif operator.contains(s, "num_output_files"):
                    num_output_files_str = s
                elif operator.contains(s, "total_output_size"):
                    output_size_str = s
            # job_id
            job_id = int(sep_eachrow_comma[1].split(":")[1])
            # output_level
            output_level = int(output_level_str.split(":")[1])
            # output_size
            output_size_bytes = int(output_size_str.split()[1])
            output_size_mb = int(output_size_bytes / (1024 * 1024))
            # output_file_#
            output_file_num = int(num_output_files_str.split()[1])
            # cur_time
            date_time_str = sep_eachrow_space[0]
            cur_time_struct = time.strptime(date_time_str, "%Y/%m/%d-%H:%M:%S.%f")
            cur_time = int(time.mktime(cur_time_struct))
            sec = cur_time - db_start_time

            finished_ids.append(job_id)
            finished_info = [output_level, output_size_mb, sec, output_file_num]
            finished_infos.append(finished_info)

        eachrow = f.readline()
    f.close()

    level_cmp_stat = [[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0],
                      [0, 0, 0]]  # [size, time, num]
    for i in range(0, len(started_ids) - 1):
        job_id = started_ids[i]
        input_level = started_infos[i][0]
        input_size = started_infos[i][1]
        started_time = started_infos[i][2]
        if job_id in finished_ids:
            j = finished_ids.index(job_id)
            output_level = finished_infos[j][0]
            output_size = finished_infos[j][1]
            finished_time = finished_infos[j][2]

            compaction_size = input_size + output_size
            compaction_time = finished_time - started_time
            idx = match_level_cmp(input_level, output_level)

            level_cmp_stat[idx][0] += compaction_size
            level_cmp_stat[idx][1] += compaction_time
            level_cmp_stat[idx][2] += 1

            cmp_times[output_level].append(started_time)
            cmp_size[output_level].append(input_size)
            cmp_times[output_level].append(finished_time)
            cmp_size[output_level].append(output_size)

    cmp_freq = 0
    cmp_sumsize = 0
    for c in cmp_times:
        cmp_freq += int(len(c) / 2)
    for c in cmp_size:
        cmp_sumsize += sum(c)

    cmp_intervals = []
    for c in cmp_times:
        for i in range(0, len(c)-1):
            if(i%2 == 0):
                cmp_intervals.append((c[i], c[i+1]))
    max_overlap_info = max_overlapping_cmp(cmp_intervals)
    print("max_overlap compaction: ", max_overlap_info[0])
    print("max_overlap compaction intervals: ", max_overlap_info[1])
    cmp_sumsize = int(cmp_sumsize/1024) #GB
    return [cmp_times, cmp_size,cmp_freq, cmp_sumsize]


def Compaction_Stat(LOG):
    cmp_info = Compaction_duration(LOG)
    cmp_times = cmp_info[0]
    cmp_size = cmp_info[1]
    cmp_freq = 0
    cmp_sumsize = 0
    # for c in cmp_times:
    #     cmp_freq += int(len(c) / 2)
    # for c in cmp_size:
    #     cmp_sumsize += sum(c)
    # print(LOG)
    # print("cmp freq: ", cmp_freq, "cmp size: ", cmp_sumsize)
    cmp_info_LL = []
    for i in range(0, len(cmp_times)):
        cmp_freq_tmp = int(len(cmp_times[i]) / 2)
        cmp_sumsize_tmp = int(sum(cmp_size[i]) / 1024)  # GB
        text = " freq:{}; sum_size:{} GB".format(cmp_freq_tmp, cmp_sumsize_tmp)
        cmp_info_LL.append((cmp_freq_tmp,cmp_sumsize_tmp))
    return cmp_info_LL

def Compaction_Stats(LOG_list, path_list):
    cmp_info = []
    for i in range(len(LOG_list)):
        path = path_list[i]
        fullpath = path + LOG_list[i]
        cmp_info_LL = Compaction_Stat(fullpath)
        cmp_info.append(cmp_info_LL)
    return cmp_info

def Compaction_Start_Summary(LOG):
    f = open(LOG, 'r')
    eachrow = f.readline()
    while (eachrow):
        sep_eachrow_comma = eachrow.strip().split(',')
        sep_eachrow_space = eachrow.strip().split()
        # if 'Compaction' in sep_eachrow_space and 'start' in sep_eachrow_space and 'summary' in sep_eachrow_space:
        # if 'start' in sep_eachrow_space and 'summary' in sep_eachrow_space:
        if 'Compaction' in sep_eachrow_space:
            if 'start' in sep_eachrow_space:
                print(eachrow)
        eachrow = f.readline()
    f.close()


def Flush(filename):
    db_start_time = rocksdb_starttime(filename)
    f = open(filename, 'r')
    started_id = []
    started_sec = []
    finished_id = []
    finished_sec = []
    flush_size = []
    eachrow = f.readline()
    while (eachrow):
        SILK = False
        sep_eachrow_comma = eachrow.strip().split(',')
        sep_eachrow_space = eachrow.strip().split()
        if ' "event": "flush_started"' in sep_eachrow_comma:
            # print(eachrow)
            for s in sep_eachrow_comma:
                if operator.contains(s, "total_data_size"):
                    input_size_str = s
                elif operator.contains(s, "memory_usage"):
                    input_size_str = s
                    SILK = True
            # job_id
            job_id = int(sep_eachrow_comma[1].split()[1])
            # input_size
            if SILK:
                input_size_str = input_size_str.split(":")[1].split('}')[0]
            else:
                input_size_str = input_size_str.split()[1]
            input_size_bytes = int(input_size_str)
            input_size_mb = int(input_size_bytes / (1024 * 1024))
            # cur_time
            date_time_str = sep_eachrow_space[0]
            cur_time_struct = time.strptime(date_time_str, "%Y/%m/%d-%H:%M:%S.%f")
            cur_time = int(time.mktime(cur_time_struct))
            sec = cur_time - db_start_time

            started_id.append(job_id)
            flush_size.append(input_size_mb)
            started_sec.append(sec)

        if ' "event": "flush_finished"' in sep_eachrow_comma:
            # print(eachrow)
            # job_id
            job_id = int(sep_eachrow_comma[1].split()[1])
            # cur_time
            date_time_str = sep_eachrow_space[0]
            cur_time_struct = time.strptime(date_time_str, "%Y/%m/%d-%H:%M:%S.%f")
            cur_time = int(time.mktime(cur_time_struct))
            sec = cur_time - db_start_time

            finished_id.append(job_id)
            finished_sec.append(sec)

        eachrow = f.readline()
    f.close()
    flush_time_ = []
    flush_size_ = []
    flush_duration = []
    for i in range(0, len(started_id) - 1):
        job_id = started_id[i]
        started_time = started_sec[i]
        size = flush_size[i]
        j = finished_id.index(job_id)
        finished_time = finished_sec[j]
        flush_time_.append(started_time)
        flush_size_.append(size)
        flush_time_.append(finished_time)
        flush_size_.append(size)
        flush_duration.append(finished_time - started_time)

    print(filename, "Flush Freq: ", len(flush_time_), "Flush Size: ", sum(flush_size), "MB/s", "Avg Flush Duration: ",
          int(sum(flush_duration) / len(flush_duration)))
    flush_info = []
    flush_info.append(flush_time_)
    flush_info.append(flush_size_)
    return flush_info

class RTWSs:
    def __init__(self, Mem_slow=0, Mem_stop=0, L0_slow=0, L0_stop=0, PS_slow=0, PS_stop=0):
        self.Mem_slow = Mem_slow
        self.Mem_stop = Mem_stop
        self.L0_slow = L0_slow
        self.L0_stop = L0_stop
        self.PS_slow = PS_slow
        self.PS_stop = PS_stop
        self.slow = self.Mem_slow + self.L0_slow + self.PS_slow
        self.stop = self.Mem_stop + self.L0_stop + self.PS_stop

def Three_RTWSs_SlowStop(filename):
    db_start_time = rocksdb_starttime(filename)
    f = open(filename, 'r')
    print(filename, ": Three_RTWSs_SlowStop")
    rdb_stallstop_sec = [[], [], []]  # memtable, Level0, Pending compaction input size
    rdb_stall_freq = [0, 0, 0]
    rdb_stop_freq = [0, 0, 0]
    eachrow = f.readline()
    while (eachrow):
        sep_eachrow_space = eachrow.split()

        if 'Stalling' in sep_eachrow_space:
            # cur time
            date_time_str = sep_eachrow_space[0]
            cur_time_struct = time.strptime(date_time_str, "%Y/%m/%d-%H:%M:%S.%f")
            cur_time = int(time.mktime(cur_time_struct))
            sec = cur_time - db_start_time

            if 'immutable' in sep_eachrow_space:
                rdb_stallstop_sec[0].append(sec)
                rdb_stall_freq[0] += 1
            elif 'level-0' in sep_eachrow_space:
                rdb_stallstop_sec[1].append(sec)
                rdb_stall_freq[1] += 1
            elif 'compaction' in sep_eachrow_space:
                rdb_stallstop_sec[2].append(sec)
                rdb_stall_freq[2] += 1
        elif 'Stopping' in sep_eachrow_space:
            # cur time
            date_time_str = sep_eachrow_space[0]
            cur_time_struct = time.strptime(date_time_str, "%Y/%m/%d-%H:%M:%S.%f")
            cur_time = int(time.mktime(cur_time_struct))
            sec = cur_time - db_start_time

            if 'immutable' in sep_eachrow_space:
                rdb_stallstop_sec[0].append(sec)
                rdb_stop_freq[0] += 1
            elif 'level-0' in sep_eachrow_space:
                rdb_stallstop_sec[1].append(sec)
                rdb_stop_freq[1] += 1
            elif 'compaction' in sep_eachrow_space:
                rdb_stallstop_sec[2].append(sec)
                rdb_stop_freq[2] += 1
        eachrow = f.readline()
    f.close()
    RT_WSs = RTWSs(rdb_stall_freq[0],rdb_stop_freq[0],rdb_stall_freq[1],rdb_stop_freq[1],rdb_stall_freq[2],rdb_stop_freq[2])
    return [rdb_stallstop_sec,rdb_stall_freq,rdb_stop_freq,RT_WSs]

def L0fnum_PS_info(LOG):
    db_start_time = rocksdb_starttime(LOG)
    f = open(LOG, 'r')
    eachrow = f.readline()
    time_elapsed = []
    L0fnum = []
    level0to1_PCsize = []
    deeperlevel_PCsize = []
    PCsize = []
    while(eachrow):
        sep_eachrow_space = eachrow.split()
        if 'RecalculateWriteStallConditions:' in sep_eachrow_space:
            # cur time
            date_time_str = sep_eachrow_space[0]
            cur_time_struct = time.strptime(date_time_str, "%Y/%m/%d-%H:%M:%S.%f")
            cur_time = int(time.mktime(cur_time_struct))
            sec = cur_time - db_start_time

            #level0 file
            # previous index 7, new index 9
            if(sep_eachrow_space[9]=='pending'):
                level0fnum_str = sep_eachrow_space[7]
            else:
                level0fnum_str = sep_eachrow_space[9]
            level0fnum = int(level0fnum_str)

            # PS
            #previous index 15, new index 12, newest 14 when level0 is 9
            # print(sep_eachrow_space)
            if(sep_eachrow_space[11] == 'bytes'):
                ps_bytes = int(sep_eachrow_space[12])
            elif(sep_eachrow_space[12] == 'level0to1'):
                ps_bytes = int(sep_eachrow_space[15])
            elif(sep_eachrow_space[13] == 'bytes'):
                ps_bytes = int(sep_eachrow_space[14])

            ps_GB = int(ps_bytes/(1024*1024*1024))

            time_elapsed.append(sec)
            L0fnum.append(level0fnum)
            PCsize.append(ps_GB)

        eachrow = f.readline()
    f.close()
    return [time_elapsed,L0fnum,level0to1_PCsize,deeperlevel_PCsize,PCsize]

def ADOC_L0fnum_PS_info(LOG):
    db_start_time = rocksdb_starttime(LOG)
    f = open(LOG, 'r')
    eachrow = f.readline()
    time_elapsed = []
    L0fnum = []
    level0to1_PCsize = []
    deeperlevel_PCsize = []
    PCsize = []
    while(eachrow):
        sep_eachrow_space = eachrow.split()
        if 'ADOCRecalculateWriteStallConditions:' in sep_eachrow_space:
            # cur time
            date_time_str = sep_eachrow_space[0]
            cur_time_struct = time.strptime(date_time_str, "%Y/%m/%d-%H:%M:%S.%f")
            cur_time = int(time.mktime(cur_time_struct))
            sec = cur_time - db_start_time

            #level0 file
            # previous index 7, new index 9
            if(sep_eachrow_space[9]=='pending'):
                level0fnum_str = sep_eachrow_space[7]
            else:
                level0fnum_str = sep_eachrow_space[9]
            level0fnum = int(level0fnum_str)

            # PS
            #previous index 15, new index 12, newest 14 when level0 is 9
            # print(sep_eachrow_space)
            if(sep_eachrow_space[11] == 'bytes'):
                ps_bytes = int(sep_eachrow_space[12])
            elif(sep_eachrow_space[12] == 'level0to1'):
                ps_bytes = int(sep_eachrow_space[15])
            elif(sep_eachrow_space[13] == 'bytes'):
                ps_bytes = int(sep_eachrow_space[14])

            ps_GB = int(ps_bytes/(1024*1024*1024))

            time_elapsed.append(sec)
            L0fnum.append(level0fnum)
            PCsize.append(ps_GB)

        eachrow = f.readline()
    f.close()
    return [time_elapsed,L0fnum,level0to1_PCsize,deeperlevel_PCsize,PCsize]

def ADOC_MaxBytes_BaseLevel(LOG):
    db_start_time = rocksdb_starttime(LOG)
    f = open(LOG, 'r')
    eachrow = f.readline()
    time_elapsed = []
    L0fnum = []
    level0to1_PCsize = []
    deeperlevel_PCsize = []
    base_level_size = []
    while(eachrow):
        sep_eachrow_space = eachrow.split()
        if 'ADOCMaxBytesForBaseLevel:' in sep_eachrow_space:
            # cur time
            date_time_str = sep_eachrow_space[0]
            cur_time_struct = time.strptime(date_time_str, "%Y/%m/%d-%H:%M:%S.%f")
            cur_time = int(time.mktime(cur_time_struct))
            sec = cur_time - db_start_time

            #level0 file
            # previous index 7, new index 9
            if(sep_eachrow_space[9]=='pending'):
                level0fnum_str = sep_eachrow_space[7]
            else:
                level0fnum_str = sep_eachrow_space[9]
            level0fnum = int(level0fnum_str)

            baselevel_bytes = int(sep_eachrow_space[14])

            baselevel_GB = int(baselevel_bytes/(1024*1024*1024))

            time_elapsed.append(sec)
            L0fnum.append(level0fnum)
            base_level_size.append(baselevel_GB)

        eachrow = f.readline()
    f.close()
    return [time_elapsed,L0fnum,level0to1_PCsize,deeperlevel_PCsize,base_level_size]

def Throughput(report):
    f = open(report, 'r')
    eachrow = f.readline()
    eachrow = f.readline()
    # Throughput = 0
    stalling_duration = []
    duration = 0
    started_stalling = 0
    # Throughput nearly to zero
    slow_duration = []
    s_duration = 0
    started_slow = 0

    time_elapsed = []
    tpt = []
    prev_time = 0
    while (eachrow):
        sep_eachrow_comma = eachrow.split(',')
        secs_elapsed = int(sep_eachrow_comma[0])
        interval_qps = int(sep_eachrow_comma[1])

        interval = secs_elapsed - prev_time
        avg_qps = int(interval_qps / interval)

        for i in range(prev_time + 1, secs_elapsed + 1):
            time_elapsed.append(i)
            tpt.append(avg_qps)

        prev_time = secs_elapsed
        if interval_qps == 0:
            if started_stalling == 1:
                duration += 1
            else:
                started_stalling = 1
                duration += 1
        elif interval_qps != 0 and started_stalling == 1:
            started_stalling = 0
            stalling_duration.append(duration * interval)
            duration = 0

        if avg_qps < WS_THROUGHPUT:
            if started_slow == 1:
                s_duration += 1
            else:
                started_slow = 1
                s_duration += 1
        elif avg_qps >= WS_THROUGHPUT and started_slow == 1:
            started_slow = 0
            slow_duration.append(s_duration * interval)
            s_duration = 0

        eachrow = f.readline()
    f.close()
    l = len(stalling_duration)
    s = sum(stalling_duration)
    l_slow = len(slow_duration)
    s_slow = sum(slow_duration)
    if l != 0:
        avg = int(s / l)
        print("stall freq: ", l, "stall duration(s): ", s, "avg stall duration(s): ", avg)
    return [time_elapsed, tpt, l, s, l_slow, s_slow]

def Throughput_YCSB(report):
    f = open(report, 'r')
    eachrow = f.readline()
    time_elapsed = []
    throughput = []
    latency = []
    while (eachrow):
        sep_eachrow_space = eachrow.split()
        if 'sec:' not in sep_eachrow_space:
            eachrow = f.readline()
            continue
        if sep_eachrow_space[6]=='est':
            eachrow = f.readline()
            continue
        t = int(float(sep_eachrow_space[6]))
        sec = int(sep_eachrow_space[2])
        time_elapsed.append(sec)
        throughput.append(t)
        eachrow = f.readline()
    f.close()
    return [time_elapsed, throughput]


def ReadInsert_QueueLatency_YCSB(report):
    time_elapsed = []
    avg_read_latency = []
    avg_intended_read_latency = []
    avg_write_latency = []
    avg_intended_write_latency = []

    with open(report, 'r') as file:
        for line in file:
            # Extract the elapsed time
            time_match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}):\d{3} (\d+) sec', line)
            if time_match:
                time_elapsed.append(int(time_match.group(2)))
            else:
                continue  # Skip the line if no time information is found

            # Initialize default latencies as 0.0
            read_latency = 0.0
            write_latency = 0.0
            intended_read_latency = 0.0
            intended_write_latency = 0.0

            # Check for READ latency
            read_match = re.search(r'\[READ: .*? Avg=(\d+\.\d+)', line)
            if read_match:
                read_latency = float(read_match.group(1))
                if read_latency > AVG_LATENCY_LIMIT:
                    read_latency = AVG_LATENCY_LIMIT

            # Check for INSERT (write) latency
            write_match = re.search(r'\[INSERT: .*? Avg=(\d+\.\d+)', line)
            if write_match:
                write_latency = float(write_match.group(1))
                if write_latency > AVG_LATENCY_LIMIT:
                    write_latency = AVG_LATENCY_LIMIT

            # Check for Intended-READ latency
            intended_read_match = re.search(r'\[Intended-READ: .*? Avg=(\d+\.\d+)', line)
            if intended_read_match:
                intended_read_latency = float(intended_read_match.group(1))

            # Check for Intended-INSERT (write) latency
            intended_write_match = re.search(r'\[Intended-INSERT: .*? Avg=(\d+\.\d+)', line)
            if intended_write_match:
                intended_write_latency = float(intended_write_match.group(1))

            # Append the latencies to their respective lists
            avg_read_latency.append(read_latency)
            avg_write_latency.append(write_latency)
            avg_intended_read_latency.append(intended_read_latency)
            avg_intended_write_latency.append(intended_write_latency)
    # print(avg_write_latency)
    return {
        'time_elapsed': time_elapsed,
        'avg_read_latency': avg_read_latency,
        'avg_intended_read_latency': avg_intended_read_latency,
        'avg_write_latency': avg_write_latency,
        'avg_intended_write_latency': avg_intended_write_latency
    }
def ReadInsertLatency_YCSB(report,has_read=False,has_insert=True):
    """
    Extracts time elapsed, insert latency, and read latency from a YCSB report.
    Args: report_file (str): Path to the report file.
    Returns: list: A list containing three lists - time_elapsed, insert_latency, read_latency.
    """
    time_elapsed = []
    insert_latency = []
    read_latency = []
    avg_insert_latency = 0
    p95_insert_latency = 0
    p99_insert_latency = 0
    avg_read_latency = 0
    p95_read_latency = 0
    p99_read_latency = 0
    stop_time = []
    with open(report, 'r') as file:
        for line in file:
            # Check if the line contains latency information
            # if 'Stop requested for workload. Now Joining!' in line:
            #     break
            if 'sec:' in line and ('READ AverageLatency(us)' in line or 'INSERT AverageLatency(us)' in line) and ('CLEANUP' not in line):
                # Extract time elapsed
                time_str = line.split(' sec:')[0].split()[-1]
                try:
                    time_elapsed.append(int(time_str))
                except ValueError:
                    # In case of format issues, skip this entry
                    continue
                    # Extract read and insert latencies
                if 'READ AverageLatency(us)' in line:
                    read_latency_str = line.split('[READ AverageLatency(us)=')[1].split(']')[0]
                    try:
                        read_latency.append(float(read_latency_str))
                    except ValueError:
                        # In case of format issues, skip this entry
                        continue
                if 'INSERT AverageLatency(us)' in line:
                    insert_latency_str = line.split('[INSERT AverageLatency(us)=')[1].split(']')[0]
                    try:
                        insert_latency.append(float(insert_latency_str))
                    except ValueError:
                        # In case of format issues, skip this entry
                        continue
                if ('INSERT AverageLatency(us)' not in line) and has_insert:
                    insert_latency.append(25000)
                if ('READ AverageLatency(us)' not in line) and has_read:
                    read_latency.append(25000)
            elif 'sec:' in line and '0 current ops/sec;' in line:
                time_str = line.split(' sec:')[0].split()[-1]
                time_int = int(time_str)
                if time_int > 2:
                    time_elapsed.append(time_int)
                    stop_time.append(time_int)
                    if has_read:
                        read_latency.append(25000)
                    if has_insert:
                        insert_latency.append(25000)
            if (len(time_elapsed) != len(insert_latency)) and has_insert:
                print("[len(time_elapsed) = {}] != [len(insert_latency) = {}]".format(len(time_elapsed),len(insert_latency)))
                print(line)
                return
            if (len(time_elapsed) != len(read_latency)) and has_read:
                print("[len(time_elapsed) = {}] != [len(read_latency) = {}]".format(len(time_elapsed),
                                                                                      len(read_latency)))
                print(line)
                return
            if '[INSERT], AverageLatency(us),' in line:
                avg_insert_latency_str = line.split()[2]
                avg_insert_latency = float(avg_insert_latency_str)
            if '[INSERT], 95thPercentileLatency(us),' in line:
                p95_insert_latency_str = line.split()[2]
                p95_insert_latency = float(p95_insert_latency_str)
            if '[INSERT], 99thPercentileLatency(us),' in line:
                p99_insert_latency_str = line.split()[2]
                p99_insert_latency = float(p99_insert_latency_str)
            if '[READ], AverageLatency(us),' in line:
                avg_read_latency_str = line.split()[2]
                avg_read_latency = float(avg_read_latency_str)
            if '[READ], 95thPercentileLatency(us),' in line:
                p95_read_latency_str = line.split()[2]
                p95_read_latency = float(p95_read_latency_str)
            if '[READ], 99thPercentileLatency(us),' in line:
                p99_read_latency_str = line.split()[2]
                p99_read_latency = float(p99_read_latency_str)
    print(time_elapsed)
    print(insert_latency)
    print(read_latency)
    return [time_elapsed, insert_latency, read_latency,[avg_insert_latency,p95_insert_latency,p99_insert_latency],[avg_read_latency,p95_read_latency,p99_read_latency],stop_time]


def RealTimeProcessLatency_YCSB(report):
    f = open(report, 'r')
    eachrow = f.readline()
    time_elapsed = []
    insert_latency = []
    read_latency = []
    latency = []
    while (eachrow):
        sep_eachrow_space = eachrow.split()
        # print(sep_eachrow_space)
        if 'sec:' not in sep_eachrow_space:
            eachrow = f.readline()
            continue
        if sep_eachrow_space[6] == 'est':
            eachrow = f.readline()
            continue
        sep_eachrow_comma = eachrow.split(',')
        str = sep_eachrow_comma[3]
        cleaned_string = str.replace('Avg=', '').replace(',', '')
        lt = float(cleaned_string)
        sec = int(sep_eachrow_space[2])
        time_elapsed.append(sec)
        latency.append(lt)
        eachrow = f.readline()
    f.close()
    time_elapsed = time_elapsed[0:-1]
    latency = latency[0:-1]
    return [time_elapsed, latency]


def extract_last_cumulative_stall_time(file_path):
    """
    Extracts the last occurrence of lines containing "Cumulative stall:" from a file
    and converts the time in H:M:S format to minutes (as an integer).

    Args:
    file_path (str): The full path of the file to be read.

    Returns:
    int: The cumulative stall time in minutes.
    """
    # Initialize variables
    last_line = ""

    # Read the file and extract the relevant lines
    try:
        with open(file_path, 'r') as file:
            for line in file:
                if "Cumulative stall:" in line:
                    last_line = line
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None

    # Extract the time from the last line
    if last_line:
        # time_str = last_line.split("Cumulative stall:")[1].split("H:M:S")[0].strip()
        # hours, minutes, seconds = [float(t) for t in time_str.split(':')]
        # total_minutes = int(hours * 60 + minutes + (seconds / 60))
        # return total_minutes
        original_time_str = last_line.split("Cumulative stall:")[1].split(",")[0].strip()
        hours, minutes, seconds = [float(t) for t in original_time_str.split("H:M:S")[0].split(':')]
        total_minutes = int(hours * 60 + minutes + (seconds / 60))
        total_sec = int(hours*60*60 + minutes*60 + seconds)
        return total_sec, original_time_str
    else:
        print("No 'Cumulative stall:' line found in the file.")
        return None


def extract_stall_data(file_path):
    """
    Extracts the last occurrence of lines containing specific stall information from a file,
    and calculates various counts based on the extracted data.

    Args:
    file_path (str): The full path of the file to be read.

    Returns:
    tuple: A tuple containing L0_CC, EC_CC, MT_CC, Total_CC, and the original line.
    """
    # Initialize variables
    last_line = ""
    L0_CC = EC_CC = MT_CC = Total_CC = 0

    # Regular expression patterns
    # level0_pattern = r"level0_[\w]+, (\d+)"
    # ec_cc_pattern = r"(?:slowdown|stop) for pending_compaction_bytes, (\d+)"
    # mt_cc_pattern = r"memtable_[\w]+, (\d+)"
    # total_cc_pattern = r"interval (\d+) total count"

    level0_pattern = r"(\d+) level0_[\w]+,"
    ec_cc_pattern = r"(\d+) (?:slowdown|stop) for pending_compaction_bytes,"
    mt_cc_pattern = r"(\d+) memtable_[\w]+,"
    total_cc_pattern = r"interval (\d+) total count"

    # Read the file and extract the relevant lines
    try:
        with open(file_path, 'r') as file:
            for line in file:
                if "Stalls(count):" in line:
                    last_line = line
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None, None, None, None, None

    # Extract data from the last line
    if last_line:
        ec = re.findall(ec_cc_pattern,last_line)
        L0_CC = sum(map(int, re.findall(level0_pattern, last_line)))
        EC_CC = sum(map(int, re.findall(ec_cc_pattern, last_line)))
        MT_CC = sum(map(int, re.findall(mt_cc_pattern, last_line)))
        # Total_CC_matches = re.search(total_cc_pattern, last_line)
        # Total_CC = int(Total_CC_matches.group(1)) if Total_CC_matches else 0
        Total_CC = MT_CC + L0_CC +EC_CC

        return MT_CC, L0_CC, EC_CC, Total_CC, last_line.strip()
    else:
        print("No 'Stalls(count):' line found in the file.")
        return None, None, None, None, None

class Latency_YCSB:
    def __init__(self, average=0, P95=0, P99=0):
        self.average = average
        self.P95 = P95
        self.P99 = P99

class QueueProcessLatency:
    def __init__(self, is100w=False, iswr=False, pwlatency=None,qpwlatency=None,prlatency=None,qprlatency=None):
        self.is100w = is100w # is 100% writes workload?
        self.iswr = iswr # is writes reads mix workload?
        self.pwlatency = Latency_YCSB(pwlatency.average,pwlatency.P95,pwlatency.P99) # write process latency
        self.qpwlatency = Latency_YCSB(qpwlatency.average, qpwlatency.P95, qpwlatency.P99) # write queue +  process latency
        self.prlatency = Latency_YCSB(prlatency.average, prlatency.P95, prlatency.P99) # read process latency
        self.qprlatency = Latency_YCSB(qprlatency.average, qprlatency.P95, qprlatency.P99) # read queue +  process latency

def QueueProcessLatency_YCSB(report):
    f = open(report, 'r')
    eachrow = f.readline()
    pwlatency=Latency_YCSB()
    qpwlatency=Latency_YCSB()
    prlatency=Latency_YCSB()
    qprlatency=Latency_YCSB()
    hasw = False
    hasr = False
    while(eachrow):
        sep_eachrow_space = eachrow.split(',')
        if '[READ]' in sep_eachrow_space:
            hasr = True
            if ' AverageLatency(us)' in sep_eachrow_space:
                prlatency.average = round(float(sep_eachrow_space[-1]),2)
            elif ' 95thPercentileLatency(us)' in sep_eachrow_space:
                prlatency.P95 = round(float(sep_eachrow_space[-1]), 2)
            elif ' 99thPercentileLatency(us)' in sep_eachrow_space:
                prlatency.P99 = round(float(sep_eachrow_space[-1]), 2)
        elif '[Intended-READ]' in sep_eachrow_space:
            if ' AverageLatency(us)' in sep_eachrow_space:
                qprlatency.average = round(float(sep_eachrow_space[-1]),2)
            elif ' 95thPercentileLatency(us)' in sep_eachrow_space:
                qprlatency.P95 = round(float(sep_eachrow_space[-1]), 2)
            elif ' 99thPercentileLatency(us)' in sep_eachrow_space:
                qprlatency.P99 = round(float(sep_eachrow_space[-1]), 2)
        if '[INSERT]' in sep_eachrow_space:
            hasw = True
            if ' AverageLatency(us)' in sep_eachrow_space:
                pwlatency.average = round(float(sep_eachrow_space[-1]),2)
            elif ' 95thPercentileLatency(us)' in sep_eachrow_space:
                pwlatency.P95 = round(float(sep_eachrow_space[-1]), 2)
            elif ' 99thPercentileLatency(us)' in sep_eachrow_space:
                pwlatency.P99 = round(float(sep_eachrow_space[-1]), 2)
        elif '[Intended-INSERT]' in sep_eachrow_space:
            if ' AverageLatency(us)' in sep_eachrow_space:
                qpwlatency.average = round(float(sep_eachrow_space[-1]),2)
            elif ' 95thPercentileLatency(us)' in sep_eachrow_space:
                qpwlatency.P95 = round(float(sep_eachrow_space[-1]), 2)
            elif ' 99thPercentileLatency(us)' in sep_eachrow_space:
                qpwlatency.P99 = round(float(sep_eachrow_space[-1]), 2)
        eachrow = f.readline()
    f.close()
    is100w = hasw and (not hasr)
    iswr = hasw and hasr
    return QueueProcessLatency(is100w,iswr,pwlatency,qpwlatency,prlatency,qprlatency)

class IOCPU:
    def __init__(self, rKB=0, wKB=0, rMB=0, wMB=0, rawait=0, wawait=0, util=0, idle=0, iowait=0):
        self.rKB = rKB
        self.wKB = wKB
        self.rMB = rMB
        self.wMB = wMB
        self.rawait = rawait
        self.wawait = wawait
        self.util = util
        self.idle = idle
        self.iowait = iowait

def iocpu_info(iostat):
    f = open(iostat, 'r')
    eachrow = f.readline()
    time_elapsed = []
    iocpu_info = []
    while(eachrow):
        sep_eachrow_space = eachrow.split()
        if 'avg-cpu:' in sep_eachrow_space:
            iocpu = IOCPU()
            eachrow = f.readline()
            sep_eachrow_space = eachrow.split()
            iocpu.idle = float(sep_eachrow_space[-1])
            iocpu.iowait = float(sep_eachrow_space[3])

            eachrow = f.readline()
            eachrow = f.readline()
            eachrow = f.readline()
            sep_eachrow_space = eachrow.split()
            iocpu.util = float(sep_eachrow_space[-1])
            rKB = float(sep_eachrow_space[2])
            wKB = float(sep_eachrow_space[8])
            iocpu.rKB = rKB
            iocpu.wKB = wKB
            iocpu.rMB = int(rKB/1000)
            iocpu.wMB = int(wKB/1000)
            iocpu.rawait = float(sep_eachrow_space[5])
            iocpu.wawait = float(sep_eachrow_space[11])

            iocpu_info.append(iocpu)
        eachrow = f.readline()
    f.close()
    return iocpu_info

# Define a struct for storing CPU utilization and iowait time
CPUStats = namedtuple('CPUStats', ['utilization', 'iowait'])

def cpu_info(cpustat):
    with open(cpustat, 'r') as file:
        lines = file.readlines()

    # Skip the first header line
    lines = lines[2:]

    # Extract the header and data lines
    header_line = lines[0].strip().split()
    data_lines = [line for line in lines[1:] if line.strip()]

    # Identify the number of cores by counting the lines between header lines
    core_count = 0
    for line in data_lines:
        if 'CPU' in line:
            break
        core_count += 1

    data = []
    for line in data_lines:
        if 'CPU' not in line:
            parts = line.strip().split()
            if len(parts) == 12:  # Ensure the line has the correct number of columns
                data.append(parts)

    if len(data) == 0:
        return []

    # Create DataFrame
    df = pd.DataFrame(data, columns=header_line)
    # Convert columns to appropriate data types
    df['CPU'] = df['CPU'].astype(int)
    for col in df.columns[2:]:
        df[col] = df[col].astype(float)

    # Compute the average utilization and iowait for each second
    df['Total_Utilization'] = 100 - df['%idle']
    avg_utilization_per_second = df.groupby(df.index // core_count)['Total_Utilization'].mean().tolist()
    avg_iowait_per_second = df.groupby(df.index // core_count)['%iowait'].mean().tolist()

    # Create a list of CPUStats structs
    cpu_stats_list = [CPUStats(utilization=util, iowait=iowait) for util, iowait in zip(avg_utilization_per_second, avg_iowait_per_second)]

    return cpu_stats_list
def ADOC_threadbatch(report):
    f = open(report, 'r')
    eachrow = f.readline()
    eachrow = f.readline()
    time_elapsed = []
    thread_num = []
    batch_size = []
    while (eachrow):
        sep_eachrow_comma = eachrow.split(',')
        secs_elapsed = int(sep_eachrow_comma[0])
        b_size = int(sep_eachrow_comma[2])
        t_num = int(sep_eachrow_comma[3])

        time_elapsed.append(secs_elapsed)
        batch_size.append(b_size)
        thread_num.append(t_num)
        eachrow = f.readline()
    f.close()
    return [time_elapsed, batch_size, thread_num]

def Max_TimeElapse(report):
    tpt_info = Throughput(report)
    time_elapse = tpt_info[0]
    return time_elapse[len(time_elapse) - 1]

def lsm_state(filename):
    db_start_time = rocksdb_starttime(filename)
    f = open(filename, 'r')
    eachrow = f.readline()
    lsm_states = []
    time_elapsed = []
    while (eachrow):
        sep_eachrow_space = eachrow.split()
        sep_eachrow_comma = eachrow.split(',')
        length = len(sep_eachrow_comma)
        if '"lsm_state":' in sep_eachrow_space:
            # cur_time
            date_time_str = sep_eachrow_space[0]
            cur_time_struct = time.strptime(date_time_str, "%Y/%m/%d-%H:%M:%S.%f")
            cur_time = int(time.mktime(cur_time_struct))
            sec = cur_time - db_start_time
            time_elapsed.append(sec)

            str = ""
            if ' "event": "compaction_finished"' in sep_eachrow_comma:
                for i in range(length - 7, length):
                    str += sep_eachrow_comma[i]
            elif ' "event": "flush_finished"' in sep_eachrow_comma:
                for i in range(length - 8, length - 1):
                    str += sep_eachrow_comma[i]
            str.strip()
            level_filenum_str = str.split('[')[1].split(']')[0]
            levels = level_filenum_str.split()
            tmp_lsm = []
            for i in range(len(levels)):
                tmp_lsm.append(int(levels[i]))
            lsm_states.append(tmp_lsm)

        eachrow = f.readline()
    f.close()
    return [time_elapsed, lsm_states]


def lsm_state_L0(filename):
    lsm_states_info = lsm_state(filename)
    time_elapsed = lsm_states_info[0]
    lsm_states = lsm_states_info[1]
    lsm_states_L0 = []
    for lsm in lsm_states:
        lsm_states_L0.append(lsm[0])
    return [time_elapsed, lsm_states_L0]


def lsm_state_final(LOG):
    lsm_states_info = lsm_state(LOG)
    time_elapsed = lsm_states_info[0]
    lsm_states = lsm_states_info[1]
    print(LOG)
    print("LSM-state L0-L6: ", lsm_states[-1], "SUM: ", sum(lsm_states[-1]))


def lsm_state_finals(LOG_list, path):
    for log in LOG_list:
        fullpath = path + log
        lsm_state_final(fullpath)

class Latency:
    def __init__(self):
        self.AVG = 0
        self.StdDev = 0
        self.WR = 0
        self.P50 = 0
        self.P75 = 0
        self.P99 = 0
        self.P99_9 = 0
        self.P99_99 = 0

def latency(tpt):
    f = open(tpt, 'r')
    eachrow = f.readline()
    L = Latency()
    while (eachrow):
        sep_eachrow_space = eachrow.split()
        if 'Average:' in sep_eachrow_space:
           # print(sep_eachrow_space)
           L.AVG = float(sep_eachrow_space[3])
           L.StdDev = float(sep_eachrow_space[5])
        elif 'Percentiles:' in sep_eachrow_space:
            # print(sep_eachrow_space)
            L.P50 = float(sep_eachrow_space[2])
            L.P75 = float(sep_eachrow_space[4])
            L.P99 = float(sep_eachrow_space[6])
            L.P99_9 = float(sep_eachrow_space[8])
            L.P99_99 = float(sep_eachrow_space[10])
        eachrow = f.readline()
    f.close()
    return L

def avgtpt(tpt):
    f = open(tpt, 'r')
    eachrow = f.readline()
    avgtpt = 0
    while (eachrow):
        sep_eachrow_space = eachrow.split()
        if 'fillrandom' in sep_eachrow_space:
           # print(sep_eachrow_space)
           avgtpt = int(sep_eachrow_space[4])
        eachrow = f.readline()
    f.close()
    return avgtpt

def avgtpt_list(tpt_list,path_list):
    avgtpt_info = []
    for i in range(len(tpt_list)):
        path = path_list[i]
        tpt = path + tpt_list[i]
        avgtpt_info.append(avgtpt(tpt))
    return avgtpt_info

class performance_info:
    def __init__(self):
        self.avgtpt = 0
        self.Latency = None
        self.TD0duration = 0
        self.RT_WSs = None

def RTWSs_TD0_Latency(LOG,report,tpt):
    pi = performance_info()
    pi.Latency = latency(tpt)
    pi.RT_WSs = Three_RTWSs_SlowStop(LOG)[3]
    tpt_info = Throughput(report)
    pi.avgtpt = int(sum(tpt_info[1])/len(tpt_info[0]))
    pi.TD0duration = tpt_info[3]
    return pi

def LatencyDistribution(tpt):
    f = open(tpt, 'r')
    eachrow = f.readline()
    ranges = []
    distribution = []
    percentages = []
    while (eachrow):
        sep_eachrow_space = eachrow.split()
        if sep_eachrow_space[0]=='Percentiles:':
            eachrow = f.readline()
            eachrow = f.readline()
            break
        else:
            eachrow = f.readline()
    while(eachrow):
        # print("eachrow--"+eachrow+"--eachrow")
        sep_eachrow_space = eachrow.split()
        if len(sep_eachrow_space)<1:
            break
        range_start = sep_eachrow_space[1].strip(',')
        range_end = sep_eachrow_space[2]
        range_str = f'{range_start}-{range_end}'
        cnt = int(sep_eachrow_space[4])
        percentage = float(sep_eachrow_space[5].strip('%'))  # convert percentage to float

        # add the range and percentage to the arrays
        ranges.append(range_str)
        percentages.append(percentage)
        distribution.append(cnt)
        eachrow = f.readline()
    f.close()
    return [ranges,distribution,percentage]
# -------------------------------------------------------Draw one AX---------------------------------------------------------------#
def format_latency_tick(x, pos):
    return f'{int(x / 1000)}' if x != 0 else '0'
def Draw_ReadInsert_QueueLatency_YCSB_ax(ax, report, LOG, addylabel=True, addxlabel=False, legend=True):
    latency_info = ReadInsert_QueueLatency_YCSB(report)

    # Convert latency from microseconds to milliseconds
    time_elapsed = latency_info['time_elapsed']
    avg_insert_latency = np.array(latency_info['avg_write_latency']) / 1000.0
    avg_intended_insert_latency = np.array(latency_info['avg_intended_write_latency']) / 1000.0
    avg_read_latency = np.array(latency_info['avg_read_latency']) / 1000.0
    avg_intended_read_latency = np.array(latency_info['avg_intended_read_latency']) / 1000.0

    time_elapsed = time_elapsed[XSTART:XEND]
    avg_intended_insert_latency = avg_intended_insert_latency[XSTART:XEND]
    avg_intended_read_latency = avg_intended_read_latency[XSTART:XEND]

    if addylabel:
        ax.set_ylabel('Latency (s)', fontsize=XYLABEL_SIZE)
    if addxlabel:
        ax.set_xlabel('Elapsed Time (s)', fontsize=XYLABEL_SIZE)

    ax.plot(time_elapsed, avg_intended_insert_latency, color='#FFAA00', label='Write Queuing Latency', linewidth=LINE_WIDTH)
    if sum(avg_read_latency) > 0:
        ax.plot(time_elapsed, avg_intended_read_latency, color='#00BFA5', label='Read Queuing Latency', linewidth=LINE_WIDTH)
    for x in range(XSTART, XEND + 1, STEPS):  # Starts from 50, ends at 1000, steps by 50
        ax.axvline(x=x, color='gray', linestyle='--', linewidth=GRAY_LINE_WIDTH)
    if legend:
        ax.legend(loc='upper left', fontsize=LEGEND_SIZE)
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontweight('bold')
    ax.yaxis.set_major_formatter(FuncFormatter(format_latency_tick))
    ax.tick_params(axis='both', which='both', direction='in', labelsize=XYTICKS_SIZE, length=TICK_LENGTH, width=TICK_WIDTH, pad=25)

def Draw_ReadInsert_ProcessLatency_YCSB_ax(ax,report,LOG, addylabel=True,addxlabel=False,legend=True):
    latency_info = ReadInsert_QueueLatency_YCSB(report)
    time_elapsed = latency_info['time_elapsed']
    avg_write_latency = latency_info['avg_write_latency']
    avg_intended_insert_latency = latency_info['avg_intended_write_latency']
    avg_read_latency = latency_info['avg_read_latency']
    avg_intended_read_latency = latency_info['avg_intended_read_latency']

    time_elapsed = time_elapsed[XSTART:XEND]
    avg_write_latency = avg_write_latency[XSTART:XEND]
    avg_read_latency = avg_read_latency[XSTART:XEND]
    if addylabel:
        ax.set_ylabel('Latency (ms)', fontsize=XYLABEL_SIZE)
    if addxlabel:
        ax.set_xlabel('Elapsed Time (s)', fontsize=XYLABEL_SIZE)

    ax.plot(time_elapsed, avg_write_latency, color='#FF4500', label='Write Processing Latency',linewidth=LINE_WIDTH)
    if sum(avg_read_latency)>0:
        ax.plot(time_elapsed, avg_read_latency, color='#00CED1', label='Read Processing Latency',linewidth=LINE_WIDTH)
    for x in range(XSTART, XEND+1, STEPS):  # Starts from 50, ends at 1000, steps by 50
        ax.axvline(x=x, color='gray', linestyle='--', linewidth=GRAY_LINE_WIDTH)
    if legend:
        ax.legend(loc='upper left', fontsize=LEGEND_SIZE)
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontweight('bold')
    ax.yaxis.set_major_formatter(FuncFormatter(format_latency_tick))
    ax.tick_params(axis='both', which='both', direction='in', labelsize=XYTICKS_SIZE, length=TICK_LENGTH, width=TICK_WIDTH, pad=25)

def Draw_ReadInsertLatency_YCSB_ax(ax,report,LOG, addylabel=True,addxlabel=False, has_read=True, has_insert=True):
    print(report,": Draw_ReadInsertLatency_YCSB_ax")
    latency_info = ReadInsertLatency_YCSB(report,has_read,has_insert)
    time_elapsed = latency_info[0]
    insert_latency = latency_info[1]
    read_latency = latency_info[2]
    insert_latency_info = latency_info[3]
    read_latency_info = latency_info[4]
    stop_time = latency_info[5]
    stop_latency = [20000]*len(stop_time)
    stall_info = extract_last_cumulative_stall_time(LOG)
    # ax.scatter(stop_time, stop_latency, color='red', label='0 Ops', marker="+", s=100)
    if addylabel:
        ax.set_ylabel('Latency (us)', fontsize=20)
    if addxlabel:
        ax.set_xlabel('Elapsed Time (Sec)', fontsize=20)
    ax.set_ylim((0, AVG_LATENCY_LIMIT))
    # ax.set_ylim((0,25000))
    latency_text=""
    max_insert_latency = 0
    max_read_latency = 0
    if len(insert_latency) != 0:
        ax.plot(time_elapsed, insert_latency,color='#BEB8DC',label='Insert',linewidth=3.5)
        avg_insert_latency = int(insert_latency_info[0])
        ax.axhline(y=avg_insert_latency, color='black', linestyle='--', label="avg_insert_latency")
        text = "insert: " + str(avg_insert_latency) + " us"
        ax.text(1, avg_insert_latency, text, fontsize=25, fontweight='bold')
        latency_text += "[insert(us)]\n p95:{}\n p99:{}\n".format(int(insert_latency_info[1]),int(insert_latency_info[2]))
        # ax.text(1, 10000, text, fontsize=25, fontweight='bold')
        max_insert_latency = max(insert_latency)
    if len(read_latency) != 0:
        ax.plot(time_elapsed, read_latency,color='#82B0D2',label='Read',linewidth=3.5)
        avg_read_latency = int(read_latency_info[0])
        ax.axhline(y=avg_read_latency, color='black', linestyle='dotted', label="avg_read_latency")
        text = "read: " + str(avg_read_latency) + " us"
        ax.text(int(len(time_elapsed)/2), avg_read_latency, text, fontsize=25, fontweight='bold')
        latency_text += "[read(us)]\n p95:{}\n p99:{}\n".format(int(read_latency_info[1]),
                                                          int(read_latency_info[2]))
        # ax.text(1, 20000, text, fontsize=25, fontweight='bold')
        max_read_latency = max(read_latency)
    # pos = int(max(max_insert_latency,max_read_latency)/2)
    # pos = 10000
    # ax.text(1, pos, latency_text, fontsize=25, fontweight='bold')
    for x in range(0, X_AXIS+1, STEPS):  # Starts from 50, ends at 1000, steps by 50
        ax.axvline(x=x, color='gray', linestyle='--', linewidth=1)
    # stall_text = "stall duration(min): {}\n".format(stall_info[0]) + s
    # tall_info[1]
    # ax.text(500, 10000, stall_text, fontsize=25, fontweight='bold')
    ax.tick_params(axis='both', labelsize=20)
    ax.legend(loc='upper right')

def Draw_LatencyDistribution_ax(ax, tpt, addfigtitle=False,figtitle=None, addxlabel=False,addylable=False):
    latency_info = LatencyDistribution(tpt)
    ranges = latency_info[0]
    print(ranges)
    distribution = latency_info[1]
    percentage = latency_info[2]
    x_locations = np.arange(len(ranges))
    ax.set_xticks(x_locations)
    ax.set_xticklabels(ranges, fontsize=10, rotation=90)
    if addxlabel:
        ax.set_xlabel('Latency Range (us)',fontsize=XYLABEL_FONTSIZE)
    # ax.set_xticklabels(ranges, fontsize=10, rotation=45)
    ax.bar(np.arange(len(ranges)), distribution, width=0.5, color='#B3ADD4')
    for i in range(len(ranges)):
        if distribution[i] <= 1000:
            ax.text(i, distribution[i] + 1, str(int(distribution[i])), ha='center', va='bottom', fontsize=15,rotation=45)
    if addfigtitle:
        ax.set_title(figtitle, fontsize=30)
    if addylable:
        ax.set_ylabel('Distribution (ops)', fontsize=XYLABEL_FONTSIZE)
    # else:
    #     ax.set_yticklabels([])
    #     ax.set_yticks([])

def Draw_AVGTPTStat_ax(ax, tpt_list, path_list, xaixs_labels):
    avgtpt = avgtpt_list(tpt_list,path_list)
    x_len = len(xaixs_labels)
    ax.set_ylabel('Throughput(op/s)',fontsize=XYLABEL_FONTSIZE)
    ax.set_xticks(np.arange(x_len))
    ax.set_xticklabels(xaixs_labels,fontsize=XYLABEL_FONTSIZE)
    ax.plot(np.arange(x_len) , avgtpt, label="Avg Throughput", zorder=10)
    ax.scatter(np.arange(x_len) , avgtpt, marker="+", color="black", zorder=10)
    for i in range(x_len):
        ax.text(i , avgtpt[i], str(int(avgtpt[i] / 1000)), ha='center', color='black', fontweight='bold',fontsize=20)
    # if(max(tpt) <= int(THROUGHPUT_LIMIT/2)):
    #     ax1.set_ylim((0, int(THROUGHPUT_LIMIT/4)))
    # else:
    #     ax1.set_ylim((0, THROUGHPUT_LIMIT))
    ax.set_ylim((0, AVG_THROUGHPUT_LIMIT))
    ax.set_yticks([0, AVG_THROUGHPUT_LIMIT], ['0', str(int(AVG_THROUGHPUT_LIMIT/1000))+'k'])
    ax.legend(loc='upper left')

def Draw_CMPStat_ax(ax, LOG_list, path_list, xaixs_labels):
    cmp_info = Compaction_Stats(LOG_list,path_list)
    bar_width=0.2
    x_len = len(cmp_info)
    ax.set_xticks(np.arange(x_len) )
    ax.set_xticklabels(xaixs_labels, fontsize=XYLABEL_FONTSIZE)
    ax.set_ylabel('Compaction Size(GB)', fontsize=XYLABEL_FONTSIZE)
    Lii_Cmp_freq = [[],[],[],[],[],[],[],[]]
    Lii_Cmp_size = [[], [], [], [], [], [], [], []]
    for j in range(len(cmp_info)):
        cmp_info_LL = cmp_info[j]
        for i in range(len(Lii_Cmp_freq)):
            if i<len(cmp_info_LL):
                Lii_Cmp_freq[i].append(cmp_info_LL[i][0])
                Lii_Cmp_size[i].append(cmp_info_LL[i][1])
            else:
                Lii_Cmp_freq[i].append(0)
                Lii_Cmp_size[i].append(0)
    colors = ['#A1A9D0','#F0988C','#B883D4', '#9E9E9E','#CFEAF1','#C4A5DE','#F6CAE5','#96CCCB']
    # colors = ["orange", "red", "green", "purple", "black", "beige", "cyan", "magenta"]
    labels = ["L0L0", "L0L1", "L1L2", "L2L3", "L3L4", "L4L5", "L5L6", "L6L7"]
    ax.bar(np.arange(x_len) , Lii_Cmp_size[0], width=bar_width,label=labels[0], color=colors[0])
    for i in range(1,len(Lii_Cmp_freq)):
        bottom_values = [sum(Lii_Cmp_size[j][k] for j in range(i)) for k in range(x_len)]
        ax.bar(np.arange(x_len), Lii_Cmp_size[i], bottom= bottom_values, width=bar_width,label=labels[i], color=colors[i])
    cmp_size_sums = []
    for i in range(x_len):
        cmp_size_sum = sum([info[1] for info in cmp_info[i]])
        cmp_size_sums.append(cmp_size_sum)
        ax.text(i , cmp_size_sum + 1, str(int(cmp_size_sum)), ha='center', va='bottom', fontsize=20)
    ax.plot(np.arange(x_len),cmp_size_sums)
    ax.set_ylim((0, CMPSIZE_LIMIT_TOTAL_GB))
    ax.legend(loc='upper right')

def Draw_IOCPU_ax(ax,LOG,report,iostat,addtitle=False,figtitle=None,addylabel=True,addxlabel=False):
    iocpu = iocpu_info(iostat)
    throughput_info = Throughput(report)
    time_elapsed = throughput_info[0]

    length = min(len(time_elapsed), len(iocpu))
    time_elapsed = time_elapsed[:length]
    iocpu = iocpu[:length]
    # print(LOG.split('/')[-1])
    # print("len(time_elapsed)=",len(time_elapsed), "len(iocpu)=",len(iocpu))
    io_util = [i.util for i in iocpu]
    avg_io_util = round(float(sum(io_util)/len(io_util)),1)
    cpu_idle = [i.idle for i in iocpu]
    cpu_util = [float(100-i.idle) for i in iocpu]
    avg_cpu_util = round(float(sum(cpu_util)/len(cpu_util)),1)
    io100_timepoint = []
    for i in range(len(io100_timepoint)):
        if io_util[i]==100:
            io100_timepoint.append(i)
    if addylabel:
        ax.set_ylabel('CPU / IO Util (%)',fontsize=20)
    if addxlabel:
        ax.set_xlabel('Elapsed Time (Sec)', fontsize=20)
    ax.tick_params(axis='both', labelsize=20)
    ax.plot(time_elapsed, io_util, color='orange', label="I/O Util %")
    ax.axhline(y=avg_io_util, color='black', linestyle='--', label="avg_io_util")
    text = str(avg_io_util) + "%"
    ax.text(1, avg_io_util, text, fontsize=25, fontweight='bold')
    # ax.scatter(io100_timepoint, [0]*len(io100_timepoint), color='orange', marker='+', label="IO util=100%")
    ax.plot(time_elapsed, cpu_util, color='red', label="CPU Util %")
    ax.axhline(y=avg_cpu_util, color='black', linestyle='dotted', label="avg_cpu_util")
    text = str(avg_cpu_util) + "%"
    ax.text(1, avg_cpu_util, text, fontsize=25, fontweight='bold')
    if addtitle:
        sep_path = iostat.split('/')
        sep_filename = sep_path[len(sep_path) - 1].split('_')
        fig_title = sep_filename[:len(sep_filename) - 1]
        ax.set_title(fig_title, fontsize=26)
    # ax.set_ylim((0, 100))
    ax.legend(loc='upper right')

def Draw_YCSB_BandwidthUsage_ax(ax,LOG,report,iostat,addtitle=False,figtitle=None,addylabel=True,addxlabel=False, legend=True):
    iocpu = iocpu_info(iostat)
    throughput_info = Throughput_YCSB(report)
    time_elapsed = throughput_info[0]

    length = min(len(time_elapsed), len(iocpu))
    time_elapsed = time_elapsed[-length:]
    iocpu = iocpu[-length:]

    read_bandwidth = [i.rMB for i in iocpu]
    write_bandwidth = [i.wMB for i in iocpu]
    total_bandwidth = [read_bandwidth[i] + write_bandwidth[i] for i in range(len(read_bandwidth))]
    # time_elapsed = time_elapsed[XSTART:XEND]
    # read_bandwidth = read_bandwidth[XSTART:XEND]
    # write_bandwidth = write_bandwidth[XSTART:XEND]
    # total_bandwidth = total_bandwidth[XSTART:XEND]
    read_bandwidth = [bd for time, bd in zip(time_elapsed, read_bandwidth) if XSTART <= time <= XEND]
    write_bandwidth = [bd for time, bd in zip(time_elapsed, write_bandwidth) if XSTART <= time <= XEND]
    total_bandwidth = [bd for time, bd in zip(time_elapsed, total_bandwidth) if XSTART <= time <= XEND]
    time_elapsed = [time for time in time_elapsed if XSTART <= time <= XEND]
    avg_total_bandwidth = int(sum(total_bandwidth) / len(total_bandwidth))
    peak_bandwidth = max(total_bandwidth)
    peak_write_bandwidth = max(write_bandwidth)
    peak_read_bandwidth = max(read_bandwidth)
    # if addylabel:
    #     ax.set_ylabel('Bandwidth (MB/s)', fontsize=XYLABEL_SIZE)
    if addxlabel:
        ax.set_xlabel('Elapsed Time (s)', fontsize=XYLABEL_SIZE, fontweight='bold')
    ax.plot(time_elapsed, read_bandwidth, color='#8ECFC9', label="Read", linewidth=LINE_WIDTH)
    ax.plot(time_elapsed, write_bandwidth, color='#FFBE7A', label="Write", linewidth=LINE_WIDTH)
    ax.plot(time_elapsed, total_bandwidth, color='#FA7F6F', label="Total", linewidth=LINE_WIDTH)
    ax.axhline(y=1500, color='black', linestyle='--', label="Peak", linewidth=LINE_WIDTH/2)
    # for x in range(XSTART, XEND + 1, STEPS):  # Starts from 50, ends at 1000, steps by 50
    #     ax.axvline(x=x, color='gray', linestyle='--', linewidth=GRAY_LINE_WIDTH)
    if legend:
        ax.legend(loc="center left", bbox_to_anchor=(1.01, 0.5), ncol=1, fontsize=LEGEND_SIZE,
                  borderaxespad=0.1, borderpad=0.05, handletextpad=0.2, handlelength=1)
    ax.set_xticks(range(XSTART, XEND + 1, 50))
    # Apply bold font style to tick labels
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontweight('bold')
    ax.tick_params(axis='both', which='both', direction='in', labelsize=XYTICKS_SIZE, length=TICK_LENGTH,
                   width=TICK_WIDTH, pad=25)
    ax.set_ylim((0, 2000))
    ax.set_yticks([0, 750, 1500])

def Draw_YCSB_BandwidthUtil_ax(ax,LOG,report,iostat,addtitle=False,figtitle=None,addylabel=True,addxlabel=False):
    iocpu = iocpu_info(iostat)
    throughput_info = Throughput_YCSB(report)
    time_elapsed = throughput_info[0]

    length = min(len(time_elapsed), len(iocpu))
    time_elapsed = time_elapsed[-length:]
    iocpu = iocpu[-length:]

    io_util = [i.util for i in iocpu]
    w_await = [i.wawait for i in iocpu]

    if addylabel:
        ax.set_ylabel('I/O Utilization (%)',fontsize=20)
    if addxlabel:
        ax.set_xlabel('Elapsed Time (Sec)', fontsize=20)
    ax.plot(time_elapsed, io_util, color='#8ECFC9', label="IO Util")
    ax.axhline(y=100, color='black', linestyle='dashed', linewidth=5)
    ax.legend(loc='upper right')
    ax.tick_params(axis='both', labelsize=20)

def Draw_YCSB_BandwidthAwait_ax(ax,LOG,report,iostat,addtitle=False,figtitle=None,addylabel=True,addxlabel=False, legend=True):
    iocpu = iocpu_info(iostat)
    throughput_info = Throughput_YCSB(report)
    time_elapsed = throughput_info[0]

    length = min(len(time_elapsed), len(iocpu))
    time_elapsed = time_elapsed[-length:]
    iocpu = iocpu[-length:]

    w_await = [i.wawait for i in iocpu]
    r_await = [i.rawait for i in iocpu]

    time_elapsed = time_elapsed[XSTART:XEND]
    w_await = w_await[XSTART:XEND]
    r_await = r_await[XSTART:XEND]

    if addylabel:
        ax.set_ylabel('I/O Await (ms)',fontsize=XYLABEL_SIZE)
    if addxlabel:
        ax.set_xlabel('Elapsed Time (s)', fontsize=XYLABEL_SIZE)
    ax.plot(time_elapsed, r_await, color='#8ECFC9', label="Read Request I/O Await",linewidth=LINE_WIDTH)
    ax.plot(time_elapsed, w_await, color='#FFBE7A', label="Write Request I/O Await",linewidth=LINE_WIDTH)
    for x in range(XSTART, XEND+1, STEPS):  # Starts from 50, ends at 1000, steps by 50
        ax.axvline(x=x, color='gray', linestyle='--', linewidth=GRAY_LINE_WIDTH)
    if legend:
        ax.legend(loc='upper left', fontsize=LEGEND_SIZE)
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontweight('bold')
    ax.set_ylim(top=100)
    ax.tick_params(axis='both', which='both', direction='in', labelsize=XYTICKS_SIZE, length=TICK_LENGTH, width=TICK_WIDTH, pad=25)

def Draw_YCSB_CPUUtil_ax(ax,LOG,report,cpustat,addtitle=False,figtitle=None,addylabel=True,addxlabel=False, legend=True):
    cpu = cpu_info(cpustat)
    throughput_info = Throughput_YCSB(report)
    time_elapsed = throughput_info[0]

    length = min(len(time_elapsed), len(cpu))
    time_elapsed = time_elapsed[-length:]
    cpu = cpu[-length:]
    time_elapsed = time_elapsed[XSTART:XEND]
    cpu = cpu[XSTART:XEND]

    cpu_util = [i.utilization for i in cpu]
    oiwait = [i.iowait for i in cpu]
    # if addylabel:
    #     ax.set_ylabel('CPU Util (%)', fontsize=XYLABEL_SIZE)
    if addxlabel:
        ax.set_xlabel('Elapsed Time (s)', fontsize=XYLABEL_SIZE)

    ax.axhline(y=100, color='black', linestyle='dashed', linewidth=LINE_WIDTH/2)
    ax.plot(time_elapsed, cpu_util, color='cyan', label="CPU Util", linewidth=LINE_WIDTH)
    # ax.plot(time_elapsed, oiwait, color='orange', label="IO Wait %",linewidth=3.5)

    # for x in range(XSTART, XEND + 1, STEPS):  # Starts from 50, ends at 1000, steps by 50
    #     ax.axvline(x=x, color='gray', linestyle='--', linewidth=GRAY_LINE_WIDTH)
    if legend:
        ax.legend(loc="center left", bbox_to_anchor=(1.01, 0.5), ncol=1, fontsize=LEGEND_SIZE,
                  borderaxespad=0.1, borderpad=0.05, handletextpad=0.2, handlelength=1)
    # Modify tick parameters
    ax.tick_params(axis='both', which='both', direction='in', labelsize=XYTICKS_SIZE, length=TICK_LENGTH, width=TICK_WIDTH, pad=25)

    # Apply bold font style to tick labels
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontweight('bold')
    ax.set_ylim((0, 125))
    ax.set_yticks(range(0, 100 + 1, 50))

def Draw_YCSB_IOCPU_ax(ax,LOG,report,iostat,addtitle=False,figtitle=None,addylabel=True,addxlabel=False):
    iocpu = iocpu_info(iostat)
    throughput_info = Throughput_YCSB(report)
    time_elapsed = throughput_info[0]

    length = min(len(time_elapsed), len(iocpu))
    time_elapsed = time_elapsed[:length]
    iocpu = iocpu[:length]
    # print(LOG.split('/')[-1])
    # print("len(time_elapsed)=",len(time_elapsed), "len(iocpu)=",len(iocpu))
    io_util = [i.util for i in iocpu]
    avg_io_util = round(float(sum(io_util)/len(io_util)),1)
    cpu_idle = [i.idle for i in iocpu]
    cpu_util = [float(100-i.idle) for i in iocpu]
    avg_cpu_util = round(float(sum(cpu_util)/len(cpu_util)),1)
    io100_timepoint = []
    for i in range(len(io100_timepoint)):
        if io_util[i]==100:
            io100_timepoint.append(i)
    if addylabel:
        ax.set_ylabel('CPU / IO util (%)',fontsize=20)
    if addxlabel:
        ax.set_xlabel('Elapsed Time (Sec)', fontsize=20)
    ax.plot(time_elapsed, io_util, color='orange', label="IO util %")
    ax.axhline(y=avg_io_util, color='black', linestyle='--', label="avg_io_util")
    text = str(avg_io_util) + "%"
    ax.text(1, avg_io_util, text, fontsize=25, fontweight='bold')
    # ax.scatter(io100_timepoint, [0]*len(io100_timepoint), color='orange', marker='+', label="IO util=100%")
    ax.plot(time_elapsed, cpu_util, color='red', label="CPU util %")
    ax.axhline(y=avg_cpu_util, color='black', linestyle='dotted', label="avg_cpu_util")
    text = str(avg_cpu_util) + "%"
    ax.text(1, avg_cpu_util, text, fontsize=25, fontweight='bold')
    if addtitle:
        sep_path = iostat.split('/')
        sep_filename = sep_path[len(sep_path) - 1].split('_')
        fig_title = sep_filename[:len(sep_filename) - 1]
        ax.set_title(fig_title, fontsize=26)
    # ax.set_xlim((0, 3000))
    ax.legend(loc='upper right')
    ax.tick_params(axis='both', labelsize=20)

def Draw_YCSB_CPU_ax(ax,LOG,report,iostat,addtitle=False,figtitle=None,addylabel=True,addxlabel=False):
    iocpu = iocpu_info(iostat)
    throughput_info = Throughput_YCSB(report)
    time_elapsed = throughput_info[0]

    length = min(len(time_elapsed), len(iocpu))
    time_elapsed = time_elapsed[:length]
    iocpu = iocpu[:length]

    cpu_iowait = [i.iowait for i in iocpu]
    avg_cpu_iowait = round(float(sum(cpu_iowait)/len(cpu_iowait)),1)
    cpu_util = [float(100-i.idle) for i in iocpu]
    avg_cpu_util = round(float(sum(cpu_util)/len(cpu_util)),1)

    if addylabel:
        ax.set_ylabel('CPU util (%)',fontsize=20)
    if addxlabel:
        ax.set_xlabel('Elapsed Time (Sec)', fontsize=20)

    ax.plot(time_elapsed, cpu_util, color='red', label="CPU util %")
    ax.axhline(y=avg_cpu_util, color='black', linestyle='dotted', label="avg_cpu_util")
    text = str(avg_cpu_util) + "%"
    ax.text(1, avg_cpu_util, text, fontsize=25, fontweight='bold')

    ax.plot(time_elapsed, cpu_iowait, color='gray', label="CPU iowait %")
    ax.axhline(y=avg_cpu_iowait, color='black', linestyle='dashed', label="avg_cpu_iowait")
    text = str(avg_cpu_iowait) + "%"
    ax.text(1, avg_cpu_iowait, text, fontsize=25, fontweight='bold')

    ax.axhline(y=100, color='black', linestyle='dashed',linewidth=5)

    if addtitle:
        sep_path = iostat.split('/')
        sep_filename = sep_path[len(sep_path) - 1].split('_')
        fig_title = sep_filename[:len(sep_filename) - 1]
        ax.set_title(fig_title, fontsize=26)
    # ax.set_xlim((0, 3000))
    ax.legend(loc='upper right')
    ax.tick_params(axis='both', labelsize=20)

def Draw_LSMState_ax(ax,LOG,addtitle=False):
    lsmstate_info = lsm_state(LOG)
    time_elapsed = lsmstate_info[0]
    lsmstate = lsmstate_info[1]
    ax.set_ylabel('# of Files')
    ax.set_xlabel('time elapsed(s)')
    colors = ["black", "orange", "red", "green", "purple",  "beige", "cyan", "magenta"]
    labels = ["L0", "L1", "L2", "L3", "L4", "L5", "L6", "L7"]
    level = len(lsmstate[0])
    for i in range(level):
        l_state = [l[i] for l in lsmstate]
        ax.plot(time_elapsed, l_state, linewidth=1, color=colors[i], label=labels[i])
    ax.set_ylim((0,600))
    if addtitle:
        sep_path = LOG.split('/')
        sep_filename = sep_path[len(sep_path) - 1].split('_')
        fig_title = sep_filename[:len(sep_filename) - 1]
        ax.set_title(fig_title, fontsize=26)
    ax.legend(loc='upper left')

def Draw_Throughput_withAVG_TailLatency_ax(ax, report, tpt, addtitle=False, addylabel=True, addxlabel=True):
    tpt_info = Throughput(report)
    tpt_info[0] = tpt_info[0]
    tpt_info[1] = tpt_info[1]
    # write_stall_duration = tpt_info[1].count(0)
    write_stall_duration = sum(1 for i in tpt_info[1] if i <= 8200)
    l = len(tpt_info[0])
    s = sum(tpt_info[1])
    # zero_tpt = [0] * l
    # avg_tpt = [int(s / l)] * l
    avg_tpt = int(s / l)
    print("AVG throughput: ", int(s / l), "Ops/Sec")
    if addylabel:
        ax.set_ylabel('Throughput (Ops/Sec)', fontsize=20)
    if addxlabel:
        ax.set_xlabel('Elapsed Time (Sec)', fontsize=20)
    # else:
    #     ax.set_xticklabels([])
    #     ax.set_xticks([])
    ax.set_ylim((0, 300000))
    # ax.set_ylim((0, 40000))
    ax.plot(tpt_info[0], tpt_info[1])
    ax.tick_params(axis='both', labelsize=20)
    ax.axhline(y=avg_tpt, color='orange', linestyle='--', label="average throughput")
    ax.axhline(y=0, color='red', linestyle='--', label="zero throughput")
    text = str(round(float(avg_tpt / 1000), 2)) + "KOps/Sec"
    ax.text(1, avg_tpt + 1000, text, fontsize=25, fontweight='bold')
    # text = "Write Stall Duration: " + str(write_stall_duration) + " s"
    # ax.text(tpt_info[0][int(l/4)], 80000, text, fontsize=25, fontweight='bold')

    # L = latency(tpt)
    # text = "Latency\n[avg: {}],[StdDev: {}],\n[P99: {}],[P99.9: {}],[P99.99: {}]".format(L.AVG,L.StdDev,L.P99,L.P99_9,L.P99_99)
    # ax.text(100, int(THROUGHPUT_LIMIT/5)*4, text,  fontsize=20)

    if addtitle:
        sep_path = report.split('/')
        sep_filename = sep_path[len(sep_path) - 1].split('_')
        fig_title = sep_filename[:len(sep_filename) - 1]
        ax.set_title(fig_title, fontsize=26)
    ax.legend(loc='upper left')

def format_tick(x, pos):
    return f'{int(x / 1000)}K' if x != 0 else '0'

def Draw_ThroughputYCSB_withAVG_TailLatency_ax(ax, report, addtitle=False, addylabel=True, addxlabel=True, legend=True):
    tpt_info = Throughput_YCSB(report)
    latency_info = QueueProcessLatency_YCSB(report)
    # tpt_info[0] = tpt_info[0][1:-1]
    # tpt_info[1] = tpt_info[1][1:-1]
    # tpt_info[0] = tpt_info[0][1:-1]
    # tpt_info[1] = tpt_info[1][1:-1]
    # tpt_info[0] = tpt_info[0][1:-1]
    # tpt_info[1] = tpt_info[1][1:-1]
    l = len(tpt_info[0])
    s = sum(tpt_info[1])

    tpt_info[1] = [tpt for time, tpt in zip(tpt_info[0], tpt_info[1]) if XSTART <= time <= XEND]
    tpt_info[0] = [time for time in tpt_info[0] if XSTART <= time <= XEND]
    avg_tpt = round(float(s / l), 2)

    print("AVG throughput: ", avg_tpt, "KOps/Sec")
    # if addylabel:
    #     ax.set_ylabel('Throughput (ops/s)', fontsize=XYLABEL_SIZE)
    if addxlabel:
        ax.set_xlabel('Elapsed Time (s)', fontsize=XYLABEL_SIZE)
    ax.plot(tpt_info[0], tpt_info[1], label="Throughput", linewidth=LINE_WIDTH)

    # Apply bold font style to tick labels
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontweight('bold')
    # ax.axhline(y=avg_tpt, color='red', linestyle='--', label="Average Throughput", linewidth=LINE_WIDTH)
    # arrival_rate = 30000
    # ax.axhline(y=arrival_rate, color='orange', linestyle='--', label="Arrival Rate", linewidth=LINE_WIDTH*2)
    # ax.axhline(y=0, color='red', linestyle='--', label="zero throughput", linewidth=5)
    text = str(round(float(avg_tpt / 1000), 2)) + "K ops/s"
    # text = str(round(float(arrival_rate / 1000), 2)) + "K ops/s"
    # ax.set_ylim((0, max(tpt_info[1]) + 5000))
    ax.set_ylim(bottom=0)
    # ax.text(XSTART+(XEND-XSTART)/2, 40000, text, fontsize=LEGEND_SIZE, fontweight='bold', bbox=dict(facecolor='white', alpha=1))
    # for x in range(XSTART, XEND + 1, STEPS):  # Starts from 50, ends at 1000, steps by 50
    #     ax.axvline(x=x, color='gray', linestyle='--', linewidth=GRAY_LINE_WIDTH)
    ax.yaxis.set_major_formatter(FuncFormatter(format_tick))
    if legend:
        ax.legend(loc="center left", bbox_to_anchor=(1.01, 0.5), ncol=1, fontsize=LEGEND_SIZE,
                      borderaxespad=0.1, borderpad=0.05, handletextpad=0.2, handlelength=1)
        # ax.legend(loc='best', fontsize=LEGEND_SIZE, handletextpad=0.5, handlelength=1.5, ncol=2)
    ax.tick_params(axis='both', which='both', direction='in', labelsize=XYTICKS_SIZE, length=TICK_LENGTH, width=TICK_WIDTH, pad=25)
def Draw_RealTime_ProcessLatency_YCSB_ax(ax, report, addtitle=False, addylabel=True, addxlabel=True):
    latency_info = RealTimeProcessLatency_YCSB(report)
    if addylabel:
        ax.set_ylabel('Process Latency(us)', fontsize=20)
    if addxlabel:
        ax.set_xlabel('time elapsed(s)', fontsize=20)
    ax.plot(latency_info[0], latency_info[1], label="process latency(us)")
    ax.tick_params(axis='both', labelsize=20)
    ax.legend(loc='upper left')

def Draw_Throughput_ax(ax, report, addtitle=False, addylabel=True, addxlabel=True):
    tpt_info = Throughput(report)
    l = len(tpt_info[0])
    s = sum(tpt_info[1])
    # zero_tpt = [0] * l
    avg_tpt = int(s / l)
    if addylabel:
        ax.set_ylabel('Throughput(op/s)', fontsize=20)
    if addxlabel:
        ax.set_xlabel('time elapsed(s)', fontsize=20)
    ax.plot(tpt_info[0], tpt_info[1])
    ax.set_ylim((0, THROUGHPUT_LIMIT))
    # ax.plot(tpt_info[0], zero_tpt, color="orange")
    # ax.plot(tpt_info[0], avg_tpt, color="orange",label="avg_throughput")
    ax.axhline(y=avg_tpt, color='orange', linestyle='--', label="avg_throughput")
    text = str(int(avg_tpt / 1000)) + "KOps/Sec"
    ax.text(1, avg_tpt + 1000, text, fontsize=25, fontweight='bold')

    if addtitle:
        sep_path = report.split('/')
        sep_filename = sep_path[len(sep_path) - 1].split('_')
        fig_title = sep_filename[:len(sep_filename) - 1]
        ax.set_title(fig_title, fontsize=26)
    # ax.legend(loc='upper left')


def Draw_Threadnum_ax(ax, report, addylabel=True):
    tb_info = ADOC_threadbatch(report)
    if addylabel:
        ax.set_ylabel('Backgrond Thread #',fontsize=XYLABEL_FONTSIZE)
    # ax.set_xlabel('time elapsed(s)',fontsize=XYLABEL_FONTSIZE)
    ax.plot(tb_info[0], tb_info[2], color="orange", label="thread#")

    ax.set_ylim((0, 30))
    ax.legend(loc='upper left')


def Draw_Batchsize_ax(ax, report, addylabel=True):
    tb_info = ADOC_threadbatch(report)
    if addylabel:
        ax.set_ylabel('Batch Size (MB)', fontsize=XYLABEL_FONTSIZE)

    # ax.set_xlabel('time elapsed(s)')
    ax.plot(tb_info[0], tb_info[1], color="green", label="Batchsize")

    ax.set_ylim((0,600))
    ax.legend(loc='upper right')


def Draw_Flush_ax(ax, LOG):
    flush_info = Flush(LOG)
    x = np.array(flush_info[0])
    y = np.array(flush_info[1])
    ax.scatter(x, y, color="red", marker=5)

    for j in range(len(x)):
        if j % 2:
            x_range = [x[j - 1], x[j]]
            y_range = [y[j - 1], y[j]]
            if j == 1:
                ax.plot(x_range, y_range, linewidth=1, color="black", label="flush")
            else:
                ax.plot(x_range, y_range, linewidth=1, color="black")

    ax.set_ylim((0, FLUSHSIZE_LIMIT))
    ax.legend(loc='upper right')


def filter_intervals(cmp_times, cmp_size, XSTART, XEND):
    x = np.array(cmp_times)
    y = np.array(cmp_size)

    # Initialize lists to store valid x and y intervals
    x_filtered = []
    y_filtered = []

    # Iterate over the intervals in pairs (i, i+1)
    for i in range(0, len(x), 2):
        start, end = x[i], x[i + 1]
        size_start, size_end = y[i], y[i + 1]

        # Check if the interval spans the bounds and adjust
        if start < XSTART and end > XEND:
            start = XSTART
            end = XEND
        elif start < XSTART and end >= XSTART:
            start = XSTART
        elif start <= XEND and end > XEND:
            end = XEND

        # Only add intervals that are within or adjusted to the bounds
        if start >= XSTART and end <= XEND:
            x_filtered.append(start)
            x_filtered.append(end)
            y_filtered.append(size_start)
            y_filtered.append(size_end)

    # Convert lists to numpy arrays
    x_filtered = np.array(x_filtered)
    y_filtered = np.array(y_filtered)

    return x_filtered, y_filtered


def Draw_Cmp_ax(ax, LOG, set_ylabel=True, set_xlabel=False, legend=True):
    cmp_info = Compaction_duration(LOG)
    cmp_times = cmp_info[0]
    cmp_size = cmp_info[1]

    colors = ["cyan", "orange", "green", "purple", "black", "beige", "cyan", "magenta"]
    # labels = ["L0-L0 Compaction", "L0-L1 Compaction", "L1-L2 Compaction", "L2-L3 Compaction", "L3-L4 Compaction", "L4-L5 Compaction", "L5-L6 Compaction", "L6-L7 Compaction"]
    labels = ["L0-L0", "L0-L1", "L1-L2", "L2-L3", "L3-L4",
              "L4-L5", "L5-L6", "L6-L7"]
    maxsize = 0
    for i in range(0, len(cmp_times)):
        x,y = filter_intervals(cmp_times[i], cmp_size[i], XSTART, XEND)
        if cmp_size[i]:  # Check if the list is not empty
            maxsize = max(maxsize, max(cmp_size[i]))
        ax.scatter(x, y, color=colors[i], s=len(cmp_times) - i)
        linewidth = LINE_WIDTH
        if i == 1:
            linewidth = LINE_WIDTH*2
        for j in range(len(x)):
            if j % 2:
                x_range = [x[j - 1], x[j]]
                y_range = [y[j - 1], y[j]]
                if j == 1:
                    ax.plot(x_range, y_range, linewidth=linewidth, color=colors[i], label=labels[i])
                else:
                    ax.plot(x_range, y_range, linewidth=linewidth, color=colors[i])
    ax.set_yscale('log')
    ax.set_ylim((0,maxsize*2))

    # if set_ylabel:
    #     ax.set_ylabel('Size (MB)', fontsize=XYLABEL_SIZE)
    if set_xlabel:
        ax.set_xlabel('Elapsed Time (s)', fontsize=XYLABEL_SIZE)
    # for x in range(XSTART, XEND+1, STEPS):  # Starts from 50, ends at 1000, steps by 50
    #     ax.axvline(x=x, color='gray', linestyle='--', linewidth=GRAY_LINE_WIDTH)
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontweight('bold')

    if legend:
        ax.legend(loc="center left", bbox_to_anchor=(1.01, 0.5), ncol=1, fontsize=LEGEND_SIZE,
                  borderaxespad=0.1, borderpad=0.05, handletextpad=0.2, handlelength=1)
    # if legend:
    #     ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize=LEGEND_SIZE, ncol=1, handletextpad=0.5,
    #               handlelength=1, title="Compaction", title_fontsize=LEGEND_SIZE)
    ax.tick_params(axis='both', which='both', direction='in', labelsize=XYTICKS_SIZE, length=TICK_LENGTH,
                   width=TICK_WIDTH, pad=25)
    # base = 10
    # ax.yaxis.set_major_formatter(LogFormatter(base=base, labelOnlyBase=True))
    # ax.yaxis.set_major_locator(LogLocator(base=base))
    #
    # # Explicitly set the range of powers for the ticks
    # y_min, y_max = 10, 1000
    # ax.set_ylim(y_min, y_max)
    #
    # ticks = [base ** i for i in range(int(np.log10(y_min)), int(np.log10(y_max)) + 1)]
    # ax.set_yticks(ticks)


def Draw_RTWSs_SlowStop_ax(ax, LOG, report):
    rdb_stallstop_info = Three_RTWSs_SlowStop(LOG)
    rdb_stallstop_sec = rdb_stallstop_info[0]
    rdb_stall_freq = rdb_stallstop_info[1]
    rdb_stop_freq = rdb_stallstop_info[2]
    stalls_info = Throughput(report)
    ws = stalls_info[2]
    duration = stalls_info[3]
    near0_duration = stalls_info[5]
    # ax.set_ylabel('RT-WSs Type')
    colors = ["red", "orange", "purple"]
    labels = ["MT-CC", "L0-CC", "EC-CC"]
    for i in range(len(rdb_stallstop_sec)):
        if "MiccKV" in LOG:
            if i > 0:
                continue
        stall_type = []
        for j in range(len(rdb_stallstop_sec[i])):
            stall_type.append(i + 1.5)
        x_axis = np.array(rdb_stallstop_sec[i])
        y_axis = np.array(stall_type)
        # labels[i] += " Violation Freq: {}".format(rdb_stall_freq[i] + rdb_stop_freq[i])
        labels[i] += " Hit Freq: {}<-[{},{}]".format(rdb_stall_freq[i] + rdb_stop_freq[i], rdb_stall_freq[i],
                                                           rdb_stop_freq[i])
        ax.scatter(x_axis, y_axis, color=colors[i], label=labels[i])
    x_axis = []
    y_axis = []

    stall_freq = sum(rdb_stall_freq)
    stop_freq = sum(rdb_stop_freq)
    if "MICC" in LOG:
        total = rdb_stall_freq[0] + rdb_stop_freq[0]
    else:
        total = stall_freq + stop_freq

    text = "Write Stall Freq: {}".format(total)
    ax.scatter(x_axis, y_axis, color="black", label=text, marker="+")
    # text = "TD0 freq:{}; duration:{}s".format(ws, duration)
    # ax.scatter(x_axis, y_axis, color="black", label=text, marker="+")
    # text = "LowThroughput duration:{}s".format(near0_duration)
    # ax.scatter(x_axis, y_axis, color="black", label=text, marker="+")
    ax.legend(loc='upper right')
    ax.set_yticklabels([])
    ax.set_yticks([])

def Draw_YCSB_RTWSs_SlowStop_ax(ax, LOG, addylabel=True, legend=True):
    rdb_stallstop_info = Three_RTWSs_SlowStop(LOG)
    rdb_stallstop_sec = rdb_stallstop_info[0]
    markers = ['D', 'o', 's']
    y_value = [2,2.25,2.5]
    colors = ["red", "orange", "purple"]
    labels = ["MT-CC", "L0-CC", "EC-CC"]
    ax.set_ylim((0,6))
    for i in range(len(rdb_stallstop_sec)):
        stall_type = []
        rdb_stallstop_sec[i] = [time for time in rdb_stallstop_sec[i] if XSTART <= time <= XEND]
        for j in range(len(rdb_stallstop_sec[i])):
            stall_type.append(i + y_value[i])
        x_axis = np.array(rdb_stallstop_sec[i])
        y_axis = np.array(stall_type)
        ax.scatter(x_axis, y_axis, color=colors[i], label=labels[i], marker=markers[i], s=2500)

    for x in range(XSTART, XEND + 1, STEPS):  # Starts from 50, ends at 1000, steps by 50
        ax.axvline(x=x, color='gray', linestyle='--', linewidth=GRAY_LINE_WIDTH)
    if addylabel:
        ax.set_ylabel('Occurrence', fontsize=XYLABEL_SIZE)

    ax.set_yticks([])
    if legend:
        legend = ax.legend(loc='lower left', fontsize=LEGEND_SIZE, ncol=3, markerscale=4, handletextpad=0.5, handlelength=1.5)
    ax.tick_params(axis='both', which='both', direction='in', labelsize=XYTICKS_SIZE, length=TICK_LENGTH, width=TICK_WIDTH, pad=25)

def Draw_partLOfnum_ax(ax, LOG, report , addtitle=False, figtitle=None, set_xlabel=False, set_ylabel=False):
    L0fnum_info = lsm_state_L0(LOG)
    time_elapsed = L0fnum_info[0]
    L0fnum = L0fnum_info[1]
    l = len(time_elapsed)
    L0fnum_20 = [20] * l
    L0fnum_36 = [36] * l
    ax.plot(time_elapsed, L0fnum, color='#f8ac8c', label="L0file#",linewidth=2.5)
    # ax.plot(time_elapsed, L0fnum_20, color="orange", label="L0file#=20")
    # ax.plot(time_elapsed, L0fnum_36, color="red", label="L0file#=36")
    # ax.set_ylim((0, L0FNUM_LIMIT))
    ax.legend(loc='upper right')
    if addtitle:
        ax.set_title(figtitle, fontsize=10)
    if set_ylabel:
        ax.set_ylabel('L0 file #', fontsize=20)
    if set_xlabel:
        ax.set_xlabel('time elapsed(s)', fontsize=XYLABEL_FONTSIZE)
    ax.tick_params(axis='both', labelsize=20)
    print("Done LOfnum")
    ax2 = ax.twinx()
    Latency = QueueProcessLatency_YCSB(report)
    print("Done QueueProcessLatency_YCSB")
    x_axis = []
    y_axis = []
    if Latency.iswr:
        text = "[INSERT Process Latency(us)]: Average:{}; P95:{}; P99:{}".format(Latency.pwlatency.average, Latency.pwlatency.P95, Latency.pwlatency.P99)
        ax2.scatter(x_axis, y_axis, color="black", label=text)
        text = "[INSERT Queue+Process Latency(x10e6 us)]: Average:{}; P95:{}; P99:{}".format(int(Latency.qpwlatency.average/1000000),
                                                                                 int(Latency.qpwlatency.P95/1000000),
                                                                                 int(Latency.qpwlatency.P99/1000000))
        ax2.scatter(x_axis, y_axis, color="black", label=text)
        text = "[READ Process Latency(us)]: Average:{}; P95:{}; P99:{}".format(Latency.prlatency.average,
                                                                                 Latency.prlatency.P95,
                                                                                 Latency.prlatency.P99)
        ax2.scatter(x_axis, y_axis, color="black", label=text)
        text = "[READ Queue+Process Latency(x10e6 us)]: Average:{}; P95:{}; P99:{}".format(int(Latency.qprlatency.average/1000000),
                                                                                       int(Latency.qprlatency.P95/1000000),
                                                                                       int(Latency.qprlatency.P99/1000000))
        ax2.scatter(x_axis, y_axis, color="black", label=text)
    elif Latency.is100w:
        text = "[INSERT Process Latency(us)]: Average:{}; P95:{}; P99:{}".format(Latency.pwlatency.average, Latency.pwlatency.P95, Latency.pwlatency.P99)
        ax2.scatter(x_axis, y_axis, color="black", label=text)
        text = "[INSERT Queue+Process Latency(x10e6 us)]: Average:{}; P95:{}; P99:{}".format(int(Latency.qpwlatency.average/1000000),
                                                                                 int(Latency.qpwlatency.P95/1000000),
                                                                                 int(Latency.qpwlatency.P99/1000000))
        ax2.scatter(x_axis, y_axis, color="black", label=text)
    ax2.legend(loc='upper left')
    ax2.set_yticklabels([])
    ax2.set_yticks([])

def Draw_L0fnum_ax(ax, LOG, addtitle=False, figtitle=None, addxlabel=False, addylabel=False, legend=True):
    info = L0fnum_PS_info(LOG)
    time_elapsed = info[0]
    L0fnum = info[1]
    L0fnum = [num for time, num in zip(time_elapsed, L0fnum) if XSTART <= time <= XEND]
    time_elapsed = [time for time in time_elapsed if XSTART <= time <= XEND]
    ax.plot(time_elapsed, L0fnum, color='magenta', label="L0 Count", linewidth=LINE_WIDTH)
    # ax.axhline(y=36, color='black', linestyle='dashdot', label="L0-CC Hard Threshold", linewidth=5)
    ax.axhline(y=20, color='black', linestyle='--', label="Threshold",linewidth=LINE_WIDTH/2)
    # ax.axhline(y=4, color='black', linestyle='dotted', label="L0 Num = 4", linewidth=5)
    if legend:
        ax.legend(loc="center left", bbox_to_anchor=(1.01, 0.5), ncol=1, fontsize=LEGEND_SIZE,
                  borderaxespad=0.1, borderpad=0.05, handletextpad=0.2, handlelength=1)
    if addtitle:
        ax.set_title(figtitle, fontsize=TITLE_SIZE )
    # if addylabel:
    #     ax.set_ylabel('L0 Count', fontsize=XYLABEL_SIZE )
    if addxlabel:
        ax.set_xlabel('Elapsed Time (s)', fontsize=XYLABEL_SIZE, fontweight='bold')
    # for x in range(XSTART, XEND+1, STEPS):  # Starts from 50, ends at 1000, steps by 50
    #     ax.axvline(x=x, color='gray', linestyle='--', linewidth=GRAY_LINE_WIDTH)
    # Modify tick parameters
    ax.set_ylim((0, 25))
    ax.set_yticks([0, 10, 20])
    ax.set_xticks(range(XSTART, XEND+1, 100))
    ax.tick_params(axis='both', which='both', direction='in', labelsize=XYTICKS_SIZE, length=TICK_LENGTH, width=TICK_WIDTH, pad=25)
    # Apply bold font style to tick labels
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontweight('bold')
    # ax.yaxis.set_major_locator(MaxNLocator(integer=True))

def Draw_PCsize_ax(ax, LOG, addtitle=False, figtitle=None, addxlabel=False, addylabel=False, legend=True):
    info = L0fnum_PS_info(LOG)
    time_elapsed = info[0]
    ps = info[4]
    ps = [num for time, num in zip(time_elapsed, ps) if XSTART <= time <= XEND]
    time_elapsed = [time for time in time_elapsed if XSTART <= time <= XEND]
    # ax.axhline(y=128, color='black', linestyle='dashdot', label="Hard Threshold", linewidth=8)
    ax.plot(time_elapsed, ps, color='#39FF14', label="EC Size", linewidth=LINE_WIDTH)
    ax.axhline(y=64, color='black', linestyle='--', label="Threshold", linewidth=LINE_WIDTH/2)

    if legend:
        ax.legend(loc="center left", bbox_to_anchor=(1.01, 0.5), ncol=1, fontsize=LEGEND_SIZE,
                  borderaxespad=0.1, borderpad=0.05, handletextpad=0.2, handlelength=1)
    if addtitle:
        ax.set_title(figtitle, fontsize=10)
    # if addylabel:
    #     ax.set_ylabel('EC Size (GB)', fontsize=XYLABEL_SIZE)
    if addxlabel:
        ax.set_xlabel('Elapsed Time (s)', fontsize=XYLABEL_SIZE)
    # for x in range(XSTART, XEND + 1, STEPS):  # Starts from 50, ends at 1000, steps by 50
    #     ax.axvline(x=x, color='gray', linestyle='--', linewidth=GRAY_LINE_WIDTH)
    # Modify tick parameters
    # ax.set_xticks(range(XSTART, XEND+1, 100))
    # # ax.set_yticks(range(0, 80, 20))
    ax.tick_params(axis='both', which='both', direction='in', labelsize=XYTICKS_SIZE, length=TICK_LENGTH,
                   width=TICK_WIDTH, pad=25)

    # Apply bold font style to tick labels
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontweight('bold')
    ax.set_ylim((0, 80))
    ax.set_yticks([0, 32, 64])
    # ax.yaxis.set_major_locator(MaxNLocator(integer=True))


def Draw_ADOC_PCsize_ax(ax, LOG, addtitle=False, figtitle=None, set_xlabel=False, set_ylabel=False):
    info = ADOC_L0fnum_PS_info(LOG)
    time_elapsed = info[0]
    level0to1 = info[2]
    deeperlevel = info[3]
    ps = info[4]
    # ax.plot(time_elapsed, level0to1, color='#FFBE7A', label="level0to1", linewidth=3.5)
    # ax.plot(time_elapsed, deeperlevel, color='#FA7F6F', label="deeperlevel", linewidth=3.5)
    ax.plot(time_elapsed, ps, color='#8ECFC9', label="Pending Compaction Size", linewidth=3.5)
    # ax.axhline(y=64, color='#8ECFC9', linestyle='dashdot', label="Soft EC-CC")
    ax.axhline(y=128, color='black', linestyle='dotted', label="EC-CC Threshold", linewidth=5)
    if addtitle:
        ax.set_title(figtitle, fontsize=10)
    if set_ylabel:
        ax.set_ylabel('Estimated Pending Compaction Size(GB)', fontsize=20)
    if set_xlabel:
        ax.set_xlabel('Elapsed Time (Sec)', fontsize=XYLABEL_FONTSIZE)
    ax.tick_params(axis='both', labelsize=20)
    ax.legend(loc='upper right')
    ax.set_ylim((0, 20000000000))

def Draw_ADOC_BaseLevelsize_ax(ax, LOG, addtitle=False, figtitle=None, set_xlabel=False, set_ylabel=False):
    info = ADOC_MaxBytes_BaseLevel(LOG)
    time_elapsed = info[0]
    level0to1 = info[2]
    deeperlevel = info[3]
    lsize = info[4]
    ax.plot(time_elapsed, lsize, color='#8ECFC9', label="Max Base Level Size", linewidth=3.5)
    ax.axhline(y=lsize[0], color='black', linestyle='dotted', label="Initial Max Base Level Size", linewidth=5)
    if addtitle:
        ax.set_title(figtitle, fontsize=10)
    if set_ylabel:
        ax.set_ylabel('Max Base Level Size(GB)', fontsize=20)
    if set_xlabel:
        ax.set_xlabel('Elapsed Time (Sec)', fontsize=XYLABEL_FONTSIZE)
    ax.tick_params(axis='both', labelsize=20)
    ax.legend(loc='upper right')
    ax.set_ylim((0, 350))

def Draw_RTWSs_TD0_ax(ax1, pi_list, x_axis, addtitle=False):
    bar_width = 0.2
    slow = [[],[],[]] #[[mem],[l0],[ps]]
    stop = [[],[],[]]
    x_len = len(x_axis)
    duration = []
    ax1.set_xticks(np.arange(x_len) + 2*bar_width)
    ax1.set_xticklabels(x_axis)
    for pi in pi_list:
        rt = pi.RT_WSs
        slow[0].append(rt.Mem_slow)
        slow[1].append(rt.L0_slow)
        slow[2].append(rt.PS_slow)
        stop[0].append(rt.Mem_stop)
        stop[1].append(rt.L0_stop)
        stop[2].append(rt.PS_stop)
        duration.append(pi.TD0duration)

    slow = np.array(slow)
    stop = np.array(stop)

    slow_sum = [sum(slow[:,0]),sum(slow[:,1]),sum(slow[:,2])]
    ax1.bar(np.arange(x_len) + bar_width, slow[0], width=bar_width, label='Mem slow', color='#ADD8E6', alpha=0.7)
    ax1.bar(np.arange(x_len) + bar_width, slow[1], bottom= slow[0], width=bar_width, label='L0 slow',color='#4169E1', alpha=0.7)
    ax1.bar(np.arange(x_len) + bar_width, slow[2], bottom= slow[0] + slow[1], width=bar_width, label='PS slow',color='#1E90FF', alpha=0.7)
    for i in range(x_len):
        ax1.text(i + bar_width, slow_sum[i] + 1, str(int(slow_sum[i])), ha='center',va='bottom')

    stop_sum = [sum(stop[:, 0]), sum(stop[:, 1]), sum(stop[:, 2])]
    ax1.bar(np.arange(x_len) + 2*bar_width, stop[0], width=bar_width, label='Mem stop', color='#B7E4C7', alpha=0.7)
    ax1.bar(np.arange(x_len) + 2*bar_width, stop[1], bottom=stop[0], width=bar_width, label='L0 stop', color='#52BE80', alpha=0.7)
    ax1.bar(np.arange(x_len) + 2*bar_width, stop[2], bottom=stop[0] + stop[1], width=bar_width, label='PS stop', color='#1B4332', alpha=0.7)
    for i in range(x_len):
        ax1.text(i + 2* bar_width, stop_sum[i] + 1, str(int(stop_sum[i])), ha='center',va='bottom')

    ax1.bar(np.arange(x_len) + 3*bar_width, duration, width=bar_width, label='TD0 duration',color='#FFA07A')
    for i in range(x_len):
        ax1.text(i + 3* bar_width, duration[i] + 1, str(duration[i])+" sec", ha='center',va='bottom')

    ax1.set_ylim((0.1, RTWSFREQ_LIMIT))
    ax1.legend(loc='upper right')


def Draw_AVGTpt_ax(ax1, pi_list, x_axis, addtitle=False):
    bar_width = 0.2
    tpt = []
    for pi in pi_list:
        tpt.append(pi.avgtpt)
    x_len = len(x_axis)
    ax1.set_ylabel('Throughput(op/s)')
    ax1.set_xticks(np.arange(x_len) + bar_width)
    ax1.set_xticklabels(x_axis)
    ax1.plot(np.arange(x_len)+2* bar_width,tpt, label="Avg Throughput",zorder=10)
    ax1.scatter(np.arange(x_len) + 2 * bar_width, tpt, marker="+",color="black", zorder=10)
    for i in range(x_len):
        ax1.text(i+2* bar_width, tpt[i],str(int(tpt[i]/1000)),ha='center',color='red',fontweight='bold',fontsize=20, zorder=10)
    # if(max(tpt) <= int(THROUGHPUT_LIMIT/2)):
    #     ax1.set_ylim((0, int(THROUGHPUT_LIMIT/4)))
    # else:
    #     ax1.set_ylim((0, THROUGHPUT_LIMIT))
    ax1.set_ylim((0, THROUGHPUT_LIMIT))
    ax1.legend(loc='upper left')

def Draw_TailLatency_ax(ax1, pi_list, x_axis, addtitle=False):
    bar_width = 0.2
    t = []
    t_99_99 = []
    for pi in pi_list:
        L = pi.Latency
        t.append(L.P99)
        t_99_99.append(L.P99_99)
    x_len = len(x_axis)
    ax1.set_ylabel('tail latency(ms)')
    ax1.set_xticks(np.arange(x_len) + bar_width)
    ax1.set_xticklabels(x_axis)
    ax1.plot(np.arange(x_len)+2* bar_width,t, label="P99 tail latency",color="blue", zorder=10)
    ax1.plot(np.arange(x_len) + 2 * bar_width, t_99_99, label="P99_99 tail latency", color="green", zorder=10)
    ax1.scatter(np.arange(x_len) + 2 * bar_width, t, marker="+",color="black", zorder=10)
    for i in range(x_len):
        ax1.text(i+2* bar_width, t[i],str(t[i]),ha='center',color='blue',fontweight='bold',fontsize=20, zorder=10)
        ax1.text(i + 2 * bar_width, t_99_99[i], str(t_99_99[i]), ha='center', color='green', fontweight='bold', fontsize=20,
                 zorder=10)
    # if(max(tpt) <= int(THROUGHPUT_LIMIT/2)):
    #     ax1.set_ylim((0, int(THROUGHPUT_LIMIT/4)))
    # else:
    #     ax1.set_ylim((0, THROUGHPUT_LIMIT))
    ax1.set_ylim((0,P99TAILLATENCY_LIMIT))
    ax1.legend(loc='upper left')


# -------------------------------------------------------Draw Two AXs in one plot-------------------------------------------------------#
def Draw_CMPStat_AVGTpt_2ax(ax, LOG_list, tpt_list, path_list, xaxis_labels):
    Draw_AVGTPTStat_ax(ax, tpt_list, path_list, xaxis_labels)
    ax2 = ax.twinx()
    Draw_CMPStat_ax(ax2, LOG_list, path_list, xaxis_labels)

def Draw_IOCPU_Tpt_2ax(ax1, LOG, report, tpt, iostat, addtitle=False):
    Draw_Throughput_withAVG_TailLatency_ax(ax1, report,tpt)
    if addtitle:
        sep_path = report.split('/')
        sep_filename = sep_path[len(sep_path) - 1].split('_')
        fig_title = sep_filename[:len(sep_filename) - 1]
        ax1.set_title(fig_title, fontsize=26)

    ax2 = ax1.twinx()
    Draw_IOCPU_ax(ax2, LOG, report, iostat)


def Draw_RTWSs_TD0_AVGTpt_2ax(ax1, pi_list, x_axis,figtitle, addtitle=False):
    if addtitle:
        sep_figtitle = figtitle.split('_')
        fig_title = sep_figtitle[:len(sep_figtitle) - 1]
        ax1.set_title(fig_title, fontsize=26)
    ax2 = ax1.twinx()
    Draw_RTWSs_TD0_ax(ax2, pi_list, x_axis)
    Draw_AVGTpt_ax(ax1, pi_list, x_axis)

def Draw_RTWSs_TD0_TailLatency_2ax(ax1, pi_list, x_axis,figtitle, addtitle=False):
    if addtitle:
        sep_figtitle = figtitle.split('_')
        fig_title = sep_figtitle[:len(sep_figtitle) - 1]
        ax1.set_title(fig_title, fontsize=26)
    ax2 = ax1.twinx()
    Draw_RTWSs_TD0_ax(ax2, pi_list, x_axis)
    Draw_TailLatency_ax(ax1, pi_list, x_axis)

def Draw_Tpt_RTWSs_SlowStop_2ax(ax1, LOG, report, tpt, addtitle=False, figtitle=None, addylable=True, addxlable=True, addylable2=False, ylable2=None):
    Draw_Throughput_withAVG_TailLatency_ax(ax1,report,tpt, addtitle, addylable, addxlable)
    # if addxlable == False:
    #     ax1.set_xticklabels([])
    #     ax1.set_xticks([])
    # ax1.set_xlim((0,4500))
    if addtitle:
        if figtitle!=None:
            ax1.set_title(figtitle, fontsize=30)
        else:
            sep_path = report.split('/')
            sep_filename = sep_path[len(sep_path) - 1].split('_')
            fig_title = sep_filename[:len(sep_filename) - 1]
            ax1.set_title(fig_title, fontsize=26)

    ax2 = ax1.twinx()
    Draw_RTWSs_SlowStop_ax(ax2, LOG,report)
    ax2.set_yticklabels([])
    ax2.set_yticks([])
    ax2.set_ylim((0, 5))
    if addylable2:
        ax2.set_ylabel(ylable2, fontsize=30)

def Draw_TptYCSB_RTWSs_SlowStop_2ax(ax1, LOG, report, addtitle=False, figtitle=None, addylable=True, addxlable=True, addylable2=False, ylable2=None, legend=True):
    Draw_ThroughputYCSB_withAVG_TailLatency_ax(ax1,report,addtitle, addylable, addxlable, legend)
    if addtitle:
        if figtitle!=None:
            ax1.set_title(figtitle, fontsize=TITLE_SIZE)

    # ax2 = ax1.twinx()
    # Draw_YCSB_RTWSs_SlowStop_ax(ax2, LOG,report)
    # ax2.set_yticklabels([])
    # ax2.set_yticks([])
    # ax2.set_ylim((0, 5))
    # if addylable2:
    #     ax2.set_ylabel(ylable2, fontsize=30)

def Draw_ProcessLatencyYCSB_RTWSs_SlowStop_2ax(ax1, LOG, report, addtitle=False, figtitle=None, addylable=True, addxlable=True, addylable2=False, ylable2=None):
    Draw_RealTime_ProcessLatency_YCSB_ax(ax1,report,addtitle, addylable, addxlable)
    if addtitle:
        if figtitle!=None:
            ax1.set_title(figtitle, fontsize=30)

    ax2 = ax1.twinx()
    Draw_YCSB_RTWSs_SlowStop_ax(ax2, LOG,report)
    ax2.set_yticklabels([])
    ax2.set_yticks([])
    ax2.set_ylim((0, 5))
    if addylable2:
        ax2.set_ylabel(ylable2, fontsize=30)


def Draw_Tpt_Cmp_2ax(ax1, LOG, report, tpt, addtitle=False, figtitle=None, addylable=True, addxlable=True, addylable2=False, ylable2=None):
    Draw_Throughput_withAVG_TailLatency_ax(ax1,report,tpt, addtitle, addylable, addxlable)
    if addtitle:
        if figtitle!=None:
            ax1.set_title(figtitle, fontsize=30)
        else:
            sep_path = report.split('/')
            sep_filename = sep_path[len(sep_path) - 1].split('_')
            fig_title = sep_filename[:len(sep_filename) - 1]
            ax1.set_title(fig_title, fontsize=26)

    ax2 = ax1.twinx()
    Draw_Cmp_ax(ax2, LOG)
    if addylable2==False:
        ax2.set_yticklabels([])
        ax2.set_yticks([])
    if addylable2:
        ax2.set_ylabel(ylable2, fontsize=30)


def Draw_Tpt_Flush_2ax(ax1, LOG, report, tpt, addtitle=False):
    Draw_Throughput_withAVG_TailLatency_ax(ax1, report,tpt)
    if addtitle:
        sep_path = report.split('/')
        sep_filename = sep_path[len(sep_path) - 1].split('_')
        fig_title = sep_filename[:len(sep_filename) - 1]
        ax1.set_title(fig_title, fontsize=26)

    ax2 = ax1.twinx()
    Draw_Flush_ax(ax2, LOG)


def Draw_Tpt_L0fnum_2ax(ax1, LOG, report, addtitle=False):
    Draw_Throughput_ax(ax1, report)
    if addtitle:
        sep_path = report.split('/')
        sep_filename = sep_path[len(sep_path) - 1].split('_')
        fig_title = sep_filename[:len(sep_filename) - 1]
        ax1.set_title(fig_title, fontsize=26)

    ax2 = ax1.twinx()
    Draw_L0fnum_ax(ax2, LOG)


def Draw_Tpt_Threadnum_2ax(ax1, LOG, report, addtitle=False):
    Draw_Throughput_ax(ax1, report)
    if addtitle:
        sep_path = report.split('/')
        sep_filename = sep_path[len(sep_path) - 1].split('_')
        fig_title = sep_filename[:len(sep_filename) - 1]
        ax1.set_title(fig_title, fontsize=26)

    ax2 = ax1.twinx()
    Draw_Threadnum_ax(ax2, LOG)


def Draw_Threadnum_Batchsize_2ax(ax1, report, addtitle=False, figtitle=None, addylabel=True, addylabel2=True, addxlabel=False):
    Draw_Threadnum_ax(ax1, report, addylabel)
    if addtitle:
        if figtitle!=None:
            ax1.set_title(figtitle, fontsize=25)
        else:
            sep_path = report.split('/')
            sep_filename = sep_path[len(sep_path) - 1].split('_')
            fig_title = sep_filename[:len(sep_filename) - 1]
            ax1.set_title(fig_title, fontsize=26)
    if addxlabel:
        ax1.set_xlabel('time elapsed(s)', fontsize=XYLABEL_FONTSIZE)
    ax2 = ax1.twinx()
    Draw_Batchsize_ax(ax2, report,addylabel2)
    if addylabel2==False:
        ax2.set_yticklabels([])
        ax2.set_yticks([])

def Draw_L0fnum_PCSize_2ax(ax1, LOG, addtitle=False, figtitle=None, addylabel=False, addxlabel=False, addylabel2=False):
    Draw_L0fnum_ax(ax1,LOG,addtitle,figtitle,addxlabel,addylabel)
    if addtitle:
        ax1.set_title(figtitle, fontsize=26)
    ax2 = ax1.twinx()
    Draw_PCsize_ax(ax2,LOG,addtitle,figtitle,addxlabel,addylabel2)
    if addylabel2==False:
        ax2.set_yticklabels([])
        ax2.set_yticks([])

def Draw_ADOC_L0fnum_PCSize_2ax(ax1, LOG, addtitle=False, figtitle=None, addylabel=False, addxlabel=False, addylabel2=False):
    Draw_L0fnum_ax(ax1,LOG,addtitle,figtitle,addxlabel,addylabel)
    if addtitle:
        ax1.set_title(figtitle, fontsize=26)
    ax2 = ax1.twinx()
    Draw_ADOC_PCsize_ax(ax2,LOG,addtitle,figtitle,addxlabel,addylabel2)
    if addylabel2==False:
        ax2.set_yticklabels([])
        ax2.set_yticks([])






