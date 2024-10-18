import matplotlib.pyplot as plt
import os,re
from globalvalues import PATH
from common import Draw_TptYCSB_RTWSs_SlowStop_2ax, Draw_PCsize_ax
from common import Draw_YCSB_RTWSs_SlowStop_ax, Draw_Cmp_ax, Draw_L0fnum_ax
from common import Draw_ReadInsert_ProcessLatency_YCSB_ax,Draw_ReadInsert_QueueLatency_YCSB_ax
# -------------------------------------------------------Draw multiple plots of the same db in one fig and show-------------------------------------------------------#

def Draw_Throughput_CCs(LOG_list, report_list, iostat_list,cpustat_list, path_list,figpath, figname,workload, cache,core, arrivalrate):
    plt.rcParams["font.family"] = "Times New Roman"
    figtitle_list = ["SubCompaction OFF", "SubCompaction ON"]
    col = len(figtitle_list)
    row = 4
    fig, axes = plt.subplots(row, col, sharex='col', sharey='row', figsize=(30 * col, 8 * row))
    # fig.suptitle("Setting: [BlockCache-{}GB]  Workload: [{}-Zipfian, ArrivalRate-{}K ops/s] Hardware: [SSD, {}Core]".format(cache,workload,arrivalrate, core), fontsize=80, fontweight='bold')
    for i in range(len(figtitle_list)):
        addylabel = False
        addylabel2 = False
        legend = False
        if i == 0:
            addylabel = True
            legend = True
        if i == (col-1):
            addylabel2 = True
        path = path_list[i]
        LOG = path + LOG_list[i]
        report = path + report_list[i]
        iostat = path + iostat_list[i]
        cpustat = path + cpustat_list[i]
        figtitle = figtitle_list[i]
        Draw_TptYCSB_RTWSs_SlowStop_2ax(axes[0][i], LOG, report, True, figtitle, addylabel, False, False, None, legend)
        # Draw_YCSB_RTWSs_SlowStop_ax(axes[1][i], LOG, addylabel, legend)
        Draw_Cmp_ax(axes[1][i], LOG, addylabel, False, legend)
        Draw_L0fnum_ax(axes[2][i], LOG, False, None, False, addylabel, legend)
        Draw_PCsize_ax(axes[3][i], LOG, False, None, True, addylabel, legend)
        # Draw_ReadInsert_ProcessLatency_YCSB_ax(axes[3][i], report, LOG, addylabel, False, legend)
        # Draw_ReadInsert_QueueLatency_YCSB_ax(axes[4][i], report, LOG, addylabel, True, legend)

    for ax in axes.flat:
        for spine in ax.spines.values():
            spine.set_linewidth(10)
    plt.subplots_adjust(wspace=0.05, hspace=0.2)
    plt.savefig(figpath + figname + ".pdf", bbox_inches='tight', dpi=fig.dpi, pad_inches=0.5)
    plt.show()

if __name__ == '__main__':
    rd = "r1"
    ip = 236
    cache = "256MB"
    arrivalrate = 150
    cores = 128
    bkthreads = "F2C6"
    dir = "{}_cores{}_ip{}".format(bkthreads, cores, ip)
    workloads = ["90w10r"]
    # workloads = ["10w90r"]
    EXP_PATH = PATH + "SubCompaction/{}/".format(dir)
    figpath = PATH + "SubCompaction/fig/"
    LOG_list = []
    report_list = []
    iostat_list = []
    cpustat_list = []
    for workload in workloads:
        path_list = [
            EXP_PATH + "{}_MT2_cores{}_workloada-{}-zipfian_{}/".format(bkthreads, cores, workload, rd),
            EXP_PATH + "SubCmp_{}_MT2_cores{}_workloada-{}-zipfian_{}/".format(bkthreads, cores, workload, rd),
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
        figname = "{}-{}-SubCompaction".format(bkthreads, workload)
        Draw_Throughput_CCs(LOG_list, report_list, iostat_list,cpustat_list, path_list, figpath, figname, workload, cache, cores, arrivalrate)
