import matplotlib.pyplot as plt
import os,re
from globalvalues import PATH
from common import Draw_TptYCSB_RTWSs_SlowStop_2ax, Draw_Cmp_ax
from common import Draw_YCSB_RTWSs_SlowStop_ax, Draw_YCSB_BandwidthAwait_ax
from common import Draw_ReadInsert_ProcessLatency_YCSB_ax,Draw_ReadInsert_QueueLatency_YCSB_ax
# -------------------------------------------------------Draw multiple plots of the same db in one fig and show-------------------------------------------------------#

def Draw_Throughput_CCs(LOG_list, report_list, iostat_list,cpustat_list, path_list,figpath, figname,workload, cache,core, arrivalrate):
    plt.rcParams["font.family"] = "Times New Roman"
    figtitle_list = ["Background Threads = 4", "Background Threads = 32", "Background Threads = 128"]
    figtitle_list = ["Background Threads = 4", "Background Threads = 128"]
    col = len(figtitle_list)
    row = 5
    fig, axes = plt.subplots(row, col, sharex='col', sharey='row', figsize=(100 * col, 20 * row))
    # fig.suptitle("Setting: [BlockCache-{}GB]  Workload: [{}-Zipfian, ArrivalRate-{}K ops/s] Hardware: [SSD, {}Core]".format(cache,workload,arrivalrate, core), fontsize=80, fontweight='bold')
    for i in range(len(figtitle_list)):
        addylabel = False
        addylabel2 = False
        legend = False
        if i == 0:
            addylabel = True
        if i==0:
            legend = True
        if i == (col-1):
            addylabel2 = True
        path = path_list[i]
        LOG = path + LOG_list[i]
        report = path + report_list[i]
        iostat = path + iostat_list[i]
        cpustat = path + cpustat_list[i]
        figtitle = figtitle_list[i]
        #100w
        Draw_TptYCSB_RTWSs_SlowStop_2ax(axes[0][i], LOG, report, True, figtitle, addylabel, False, False, None, legend)
        Draw_Cmp_ax(axes[1][i], LOG, addylabel, False, legend)
        Draw_YCSB_BandwidthAwait_ax(axes[2][i], LOG, report, iostat, False, None, addylabel, False, legend)
        Draw_ReadInsert_ProcessLatency_YCSB_ax(axes[3][i], report, LOG, addylabel, False, legend)
        Draw_ReadInsert_QueueLatency_YCSB_ax(axes[4][i], report, LOG, addylabel, True, legend)
        #90w10r
        # Draw_TptYCSB_RTWSs_SlowStop_2ax(axes[0][i], LOG, report, True, figtitle, addylabel, False, False, None, legend)
        # # Draw_YCSB_RTWSs_SlowStop_ax(axes[1][i], LOG, addylabel, legend)
        # # Draw_Cmp_ax(axes[2][i], LOG, addylabel, False, legend)
        # # Draw_YCSB_BandwidthAwait_ax(axes[3][i], LOG, report, iostat, False, None, addylabel, False, legend)
        # Draw_ReadInsert_ProcessLatency_YCSB_ax(axes[1][i], report, LOG, addylabel, False, legend)
        # Draw_ReadInsert_QueueLatency_YCSB_ax(axes[2][i], report, LOG, addylabel, True, legend)

    for ax in axes.flat:
        for spine in ax.spines.values():
            spine.set_linewidth(20)
    plt.subplots_adjust(wspace=0.015, hspace=0.3)
    plt.savefig(figpath + figname + ".pdf", bbox_inches='tight', dpi=fig.dpi, pad_inches=0.5)
    print(figpath + figname + ".jpg")
    plt.show()

if __name__ == '__main__':
    rd = "r1"
    ip = 236
    cache = "256MB"
    arrivalrate = 150
    cores = 128
    dir = "cores{}_ip{}".format(cores, ip)
    workloads = ["100w0r"]
    # workloads = ["90w10r"]
    EXP_PATH = PATH + "BKThreads/{}/".format(dir)
    figpath = PATH + "BKThreads/fig/"
    LOG_list = []
    report_list = []
    iostat_list = []
    cpustat_list = []
    for workload in workloads:
        print(workload)
        path_list = [
            EXP_PATH + "F1C3_MT2_cores{}_workloada-{}-zipfian_r1/".format(cores, workload),
            # EXP_PATH + "F2C6_MT2_cores{}_workloada-{}-zipfian_r1/".format(cores, workload),
            # EXP_PATH + "F4C12_MT2_cores{}_workloada-{}-zipfian_r1/".format(cores, workload),
            # EXP_PATH + "F6C18_MT2_cores{}_workloada-{}-zipfian_r1/".format(cores, workload),
            # EXP_PATH + "F8C24_MT2_cores{}_workloada-{}-zipfian_r1/".format(cores, workload),
            # EXP_PATH + "F12C36_MT2_cores{}_workloada-{}-zipfian_r1/".format(cores, workload),
            # EXP_PATH + "F16C48_MT2_cores{}_workloada-{}-zipfian_r1/".format(cores, workload),
            EXP_PATH + "F32C96_MT2_cores{}_workloada-{}-zipfian_r1/".format(cores, workload),
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
        figname = "{}-BKThreads".format( workload)
        Draw_Throughput_CCs(LOG_list, report_list, iostat_list,cpustat_list, path_list, figpath, figname, workload, cache, cores, arrivalrate)
