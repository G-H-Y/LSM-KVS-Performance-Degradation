import matplotlib.pyplot as plt
import os,re
from globalvalues import PATH
from common import FIGPATH, Draw_Tpt_RTWSs_SlowStop_2ax,Draw_IOCPU_ax,Draw_Threadnum_Batchsize_2ax, Draw_Cmp_ax, Draw_LatencyDistribution_ax
from common import Draw_TptYCSB_RTWSs_SlowStop_2ax,Draw_YCSB_IOCPU_ax,Draw_ProcessLatencyYCSB_RTWSs_SlowStop_2ax,Draw_L0fnum_PCSize_2ax,Draw_L0fnum_ax,Draw_PCsize_ax
from common import ReadInsertLatency_YCSB, Draw_ReadInsertLatency_YCSB_ax,Draw_YCSB_BandwidthUsage_ax,Draw_YCSB_CPU_ax
from common import Draw_YCSB_BandwidthUtil_ax,Draw_YCSB_BandwidthAwait_ax,Draw_YCSB_CPUUtil_ax, Draw_ReadInsert_ProcessLatency_YCSB_ax,Draw_ReadInsert_QueueLatency_YCSB_ax
# -------------------------------------------------------Draw multiple plots of the same db in one fig and show-------------------------------------------------------#

def Draw_Throughput_CCs(LOG_list, report_list, iostat_list,cpustat_list, path_list,figpath, figname,workload, cache,core, arrivalrate):

    figtitle_list = ["SubCompaction OFF", "SubCompaction ON"]
    col = len(figtitle_list)
    row = 9
    fig, axes = plt.subplots(row, col, sharex='col', sharey='row', figsize=(50 * col, 6 * row))
    fig.suptitle("Setting: [BlockCache-{}GB]  Workload: [{}-Zipfian, ArrivalRate-{}K ops/s] Hardware: [SSD, {}Core]".format(cache,workload,arrivalrate, core), fontsize=80, fontweight='bold')
    for i in range(len(figtitle_list)):
        addylabel = False
        addylabel2 = False
        if i == 0:
            addylabel = True
        if i == (col-1):
            addylabel2 = True
        path = path_list[i]
        LOG = path + LOG_list[i]
        report = path + report_list[i]
        iostat = path + iostat_list[i]
        cpustat = path + cpustat_list[i]
        figtitle = figtitle_list[i]
        Draw_TptYCSB_RTWSs_SlowStop_2ax(axes[0][i], LOG, report, True, figtitle, addylabel, False, False, None)
        Draw_ReadInsert_ProcessLatency_YCSB_ax(axes[1][i], report, LOG, addylabel, False)
        Draw_Cmp_ax(axes[2][i], LOG, addylabel, False)
        Draw_L0fnum_ax(axes[3][i], LOG, False, None, False, addylabel)
        Draw_YCSB_BandwidthUsage_ax(axes[4][i], LOG, report, iostat, False, None, addylabel, False)
        Draw_YCSB_BandwidthAwait_ax(axes[5][i], LOG, report, iostat, False, None, addylabel, False)
        Draw_YCSB_CPUUtil_ax(axes[6][i], LOG, report, cpustat, False, None, addylabel, False)
        Draw_PCsize_ax(axes[7][i], LOG, False, None, False, addylabel)
        Draw_ReadInsert_QueueLatency_YCSB_ax(axes[8][i], report, LOG, addylabel, True)

    for ax in axes.flat:
        for spine in ax.spines.values():
            spine.set_linewidth(5)
    plt.subplots_adjust(wspace=0, hspace=0.05)
    plt.savefig(figpath + figname + ".jpg", bbox_inches='tight', dpi=fig.dpi, pad_inches=0.0)
    plt.show()

if __name__ == '__main__':
    rd = "r1"
    ip = 248
    cache = "256MB"
    arrivalrate = 150
    cores = 128
    bkthreads = "F4C12"
    dir = "{}_cores{}_ip{}".format(bkthreads, cores, ip)
    workloads = ["100w0r","90w10r", "70w30r", "50w50r", "30w70r", "10w90r"]
    EXP_PATH = PATH + "SubCompaction/{}/".format(dir)
    figpath = PATH + "SubCompaction/fig/"
    LOG_list = []
    report_list = []
    iostat_list = []
    cpustat_list = []
    for workload in workloads:
        path_list = [
            EXP_PATH + "{}_MT2_cores{}_workloada-{}-zipfian_{}/".format(bkthreads, cores, workload, rd),
            EXP_PATH + "SubCmp_{}_MT2_cores{}_workloada-{}-zipfian_{}/".format(bkthreads, cores,workload, rd),
        ]
        LOG_list.clear()
        report_list.clear()
        iostat_list.clear()
        cpustat_list.clear()
        for path in path_list:
            print(path)
            LOG = [f for f in os.listdir(path) if f.endswith('LOG')][0]
            report = [f for f in os.listdir(path) if f.endswith('report')][0]
            iostat = [f for f in os.listdir(path) if f.endswith('iostat')][0]
            cpustat = [f for f in os.listdir(path) if f.endswith('cpustat')][0]
            LOG_list.append(LOG)
            report_list.append(report)
            iostat_list.append(iostat)
            cpustat_list.append(cpustat)
        figname = "{}-{}-ip{}".format(dir, workload,ip)
        Draw_Throughput_CCs(LOG_list, report_list, iostat_list,cpustat_list, path_list, figpath, figname, workload, cache, cores, arrivalrate)
