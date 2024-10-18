import matplotlib.pyplot as plt
import os,re
from globalvalues import PATH
from common import FIGPATH, Draw_Tpt_RTWSs_SlowStop_2ax,Draw_IOCPU_ax,Draw_Threadnum_Batchsize_2ax, Draw_Cmp_ax, Draw_LatencyDistribution_ax
from common import Draw_TptYCSB_RTWSs_SlowStop_2ax,Draw_YCSB_IOCPU_ax,Draw_ProcessLatencyYCSB_RTWSs_SlowStop_2ax,Draw_L0fnum_PCSize_2ax,Draw_L0fnum_ax,Draw_PCsize_ax
from common import ReadInsertLatency_YCSB, Draw_ReadInsertLatency_YCSB_ax,Draw_YCSB_BandwidthUsage_ax,Draw_YCSB_CPU_ax
from common import Draw_YCSB_BandwidthUtil_ax,Draw_YCSB_BandwidthAwait_ax,Draw_YCSB_CPUUtil_ax, Draw_ReadInsert_ProcessLatency_YCSB_ax,Draw_ReadInsert_QueueLatency_YCSB_ax
# -------------------------------------------------------Draw multiple plots of the same db in one fig and show-------------------------------------------------------#

def Draw_Throughput_CCs(LOG_list, report_list, iostat_list,cpustat_list, path_list,figpath, figname,workload, cache,core, arrivalrate, bkthreads):
    plt.rcParams["font.family"] = "Times New Roman"
    figtitle_list = ["CT = 1", "CT = 10", "CT = 50"]
    col = len(figtitle_list)
    row = 1
    fig, axes = plt.subplots(row, col, sharex='col', sharey='row', figsize=(15 * col, 6 * row))
    for i in range(len(figtitle_list)):
        addylabel = False
        addylabel2 = False
        legend = False
        if i == 0:
            addylabel = True
            legend = True
        if i == (col - 1):
            addylabel2 = True
        path = path_list[i]
        LOG = path + LOG_list[i]
        report = path + report_list[i]
        iostat = path + iostat_list[i]
        cpustat = path + cpustat_list[i]
        figtitle = figtitle_list[i]
        Draw_TptYCSB_RTWSs_SlowStop_2ax(axes[i], LOG, report, True, figtitle, addylabel, True, False, None, legend)

    for ax in axes.flat:
        for spine in ax.spines.values():
            spine.set_linewidth(10)
    plt.subplots_adjust(wspace=0.05, hspace=0.05)
    plt.subplots_adjust(top=0.9, bottom=0.2)
    plt.subplots_adjust(left=0.06, right=0.99)
    plt.savefig(figpath + figname + ".jpg", dpi=fig.dpi, pad_inches=0.0)
    plt.show()

if __name__ == '__main__':
    rd = "r1"
    ip = 153
    cache = "256MB"
    arrivalrate = 30
    cores = 128
    bkthreads = "F1C3"
    dir = "{}_cores{}_ip{}".format(bkthreads, cores, ip)
    workloads = ["100w0r", "90w10r", "70w30r", "50w50r", "30w70r", "10w90r", "0w100r"]
    # workloads = ["100w0r"]
    EXP_PATH = PATH + "ClientThreads/{}/".format(dir)
    figpath = PATH + "ClientThreads/fig/"
    LOG_list = []
    report_list = []
    iostat_list = []
    cpustat_list = []
    for workload in workloads:
        print(workload)
        path_list = [
            EXP_PATH + "CT1_{}_MT2_cores128_workloada-{}-zipfian_r1/".format(bkthreads, workload),
            EXP_PATH + "CT10_{}_MT2_cores128_workloada-{}-zipfian_r1/".format(bkthreads, workload),
            # EXP_PATH + "CT30_{}_MT2_cores128_workloada-{}-zipfian_r1/".format(bkthreads, workload),
            EXP_PATH + "CT50_{}_MT2_cores128_workloada-{}-zipfian_r1/".format(bkthreads, workload),
            # EXP_PATH + "CT100_{}_MT2_cores128_workloada-{}-zipfian_r1/".format(bkthreads, workload),
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
        figname = "{}-{}-ClientThreads".format(bkthreads, workload)
        Draw_Throughput_CCs(LOG_list, report_list, iostat_list,cpustat_list, path_list, figpath, figname, workload, cache, cores, arrivalrate, bkthreads)
