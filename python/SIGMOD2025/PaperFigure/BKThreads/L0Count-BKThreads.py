import matplotlib.pyplot as plt
import os,re
from globalvalues import PATH
from common import FIGPATH, Draw_Tpt_RTWSs_SlowStop_2ax,Draw_IOCPU_ax,Draw_Threadnum_Batchsize_2ax, Draw_Cmp_ax, Draw_LatencyDistribution_ax
from common import Draw_TptYCSB_RTWSs_SlowStop_2ax,Draw_YCSB_IOCPU_ax,Draw_ProcessLatencyYCSB_RTWSs_SlowStop_2ax,Draw_L0fnum_PCSize_2ax,Draw_L0fnum_ax,Draw_PCsize_ax
from common import ReadInsertLatency_YCSB, Draw_ReadInsertLatency_YCSB_ax,Draw_YCSB_BandwidthUsage_ax,Draw_YCSB_CPU_ax
from common import Draw_YCSB_BandwidthUtil_ax,Draw_YCSB_BandwidthAwait_ax,Draw_YCSB_CPUUtil_ax, Draw_ReadInsert_ProcessLatency_YCSB_ax,Draw_ReadInsert_QueueLatency_YCSB_ax
# -------------------------------------------------------Draw multiple plots of the same db in one fig and show-------------------------------------------------------#

def Draw_Throughput_CCs(LOG_list, report_list, iostat_list,cpustat_list, path_list,figpath, figname ):
    figtitle_list = ["BT = 4", "BT = 128"]
    plt.rcParams["font.family"] = "Times New Roman"
    col = 1
    row = len(figtitle_list)
    fig, axes = plt.subplots(row, col, sharex='col', sharey='row', figsize=(30 * col, 12 * row))
    # fig.suptitle("Setting: [BackgroundThreads-{}, BlockCache-{}]  Workload: [{}-Zipfian, ArrivalRate-{}K ops/s] Hardware: [SSD]".format(bkthreads, cache,workload,arrivalrate), fontsize=80, fontweight='bold')
    for i in range(len(figtitle_list)):
        addxlabel = False
        addylabel = False
        addylabel2 = False
        legend = False
        if i == 0:
            addylabel = True
            # legend = True
        if i == (row-1):
            addxlabel = True
            legend = True
        path = path_list[i]
        LOG = path + LOG_list[i]
        report = path + report_list[i]
        iostat = path + iostat_list[i]
        cpustat = path + cpustat_list[i]
        figtitle = figtitle_list[i]
        # Draw_TptYCSB_RTWSs_SlowStop_2ax(axes[0][i], LOG, report, True, figtitle, addylabel, False, False, None, legend)
        # Draw_YCSB_CPUUtil_ax(axes[1][i], LOG, report, cpustat, False, None, addylabel, False, legend)
        # Draw_YCSB_BandwidthUsage_ax(axes[2][i], LOG, report, iostat, False, None, addylabel, True, legend)
        Draw_L0fnum_ax(axes[i], LOG, True, figtitle, addxlabel, True, legend)

    for ax in axes.flat:
        for spine in ax.spines.values():
            spine.set_linewidth(10)
    plt.subplots_adjust(wspace=0.05, hspace=0.05)
    plt.savefig(figpath + figname + ".pdf", bbox_inches='tight', dpi=fig.dpi, pad_inches=0.0)
    plt.show()

if __name__ == '__main__':
    rd = "r1"
    ip = 236
    cache = "256MB"
    arrivalrate = 150
    cores = 128
    dir = "cores{}_ip{}".format(cores, ip)
    workloads = ["90w10r"]
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
        figname = "L0Count-BKThreads".format(workload)
        Draw_Throughput_CCs(LOG_list, report_list, iostat_list,cpustat_list, path_list, figpath, figname)
