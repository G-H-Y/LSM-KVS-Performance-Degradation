import matplotlib.pyplot as plt
import os,re
from globalvalues import PATH
from common import FIGPATH, Draw_Tpt_RTWSs_SlowStop_2ax,Draw_IOCPU_ax,Draw_Threadnum_Batchsize_2ax, Draw_Cmp_ax, Draw_LatencyDistribution_ax
from common import Draw_TptYCSB_RTWSs_SlowStop_2ax,Draw_YCSB_IOCPU_ax,Draw_ProcessLatencyYCSB_RTWSs_SlowStop_2ax,Draw_L0fnum_PCSize_2ax,Draw_L0fnum_ax,Draw_PCsize_ax
from common import ReadInsertLatency_YCSB, Draw_ReadInsertLatency_YCSB_ax,Draw_YCSB_BandwidthUsage_ax,Draw_YCSB_CPU_ax
from common import Draw_YCSB_BandwidthUtil_ax,Draw_YCSB_BandwidthAwait_ax,Draw_YCSB_CPUUtil_ax, Draw_ReadInsert_ProcessLatency_YCSB_ax,Draw_ReadInsert_QueueLatency_YCSB_ax
# -------------------------------------------------------Draw multiple plots of the same db in one fig and show-------------------------------------------------------#

def Draw_Throughput_CCs(LOG_list, report_list, iostat_list, cpustat_list, path_list, figpath, figname, workload, cache, core, arrivalrate, bkthreads):
    plt.rcParams["font.family"] = "Times New Roman"
    figtitle_list = ["DelayedWriteRate = 8MB/s", "DelayedWriteRate = 16MB/s", "DelayedWriteRate = 20MB/s", "DelayedWriteRate = 24MB/s"]
    rate = [8000, 16000, 20000, 24000]

    # Assuming 'col' is the number of columns, and 'row' is the number of rows for subplots
    col = 1
    row = 4
    fig, axes = plt.subplots(row, col, sharex='col', sharey='row', figsize=(60 * col, 10 * row))

    for i in range(len(figtitle_list)):
        legend = False
        addxlabel = (i == row - 1)  # Add x-label only on the last subplot
        path = path_list[i]
        LOG = path + LOG_list[i]
        report = path + report_list[i]
        iostat = path + iostat_list[i]
        cpustat = path + cpustat_list[i]
        figtitle = figtitle_list[i]

        # Determine when to add the legend
        if i == 0:
            legend = True

        Draw_TptYCSB_RTWSs_SlowStop_2ax(axes[i], LOG, report, True, figtitle, True, addxlabel, False, None, legend, rate[i])

    # Adjust spine width
    for ax in axes.flat:
        for spine in ax.spines.values():
            spine.set_linewidth(20)

    # Adjust layout for spacing and save the figure
    plt.subplots_adjust(wspace=0.05, hspace=0.15)
    plt.savefig(figpath + figname + ".pdf", bbox_inches='tight', dpi=fig.dpi, pad_inches=0.5)
    plt.show()

if __name__ == '__main__':
    rd = "r1"
    ip = 248
    cache = "256MB"
    arrivalrate = 150
    cores = 128
    bkthreads = "F1C3"
    dir = "{}_ip{}".format(bkthreads, ip)
    workloads = ["90w10r"]
    EXP_PATH = PATH + "DelayedWriteRate/{}/".format(dir)
    figpath = PATH + "DelayedWriteRate/fig/"
    LOG_list = []
    report_list = []
    iostat_list = []
    cpustat_list = []
    for workload in workloads:
        print(workload)
        path_list = [
            # EXP_PATH + "DWR4MB_{}_cores128_workloada-{}-zipfian_r1/".format(bkthreads, workload),
            EXP_PATH + "DWR8MB_{}_cores128_workloada-{}-zipfian_r1/".format(bkthreads, workload),
            # EXP_PATH + "DWR12MB_{}_cores128_workloada-{}-zipfian_r1/".format(bkthreads, workload),
            EXP_PATH + "DWR16MB_{}_cores128_workloada-{}-zipfian_r1/".format(bkthreads, workload),
            EXP_PATH + "DWR20MB_{}_cores128_workloada-{}-zipfian_r1/".format(bkthreads, workload),
            EXP_PATH + "DWR24MB_{}_cores128_workloada-{}-zipfian_r1/".format(bkthreads, workload),
        ]
        LOG_list.clear()
        report_list.clear()
        iostat_list.clear()
        cpustat_list.clear()
        for path in path_list:
            LOG = [f for f in os.listdir(path) if f.endswith('LOG')][0]
            report = [f for f in os.listdir(path) if f.endswith('report')][0]
            iostat = [f for f in os.listdir(path) if f.endswith('iostat')][0]
            cpustat = [f for f in os.listdir(path) if f.endswith('cpustat')][0]
            LOG_list.append(LOG)
            report_list.append(report)
            iostat_list.append(iostat)
            cpustat_list.append(cpustat)
        figname = "{}-{}-DelayedWriteRate".format(bkthreads, workload)
        Draw_Throughput_CCs(LOG_list, report_list, iostat_list,cpustat_list, path_list, figpath, figname, workload, cache, cores, arrivalrate, bkthreads)
