import matplotlib.pyplot as plt
import os,re
from globalvalues import PATH
from common import Draw_TptYCSB_RTWSs_SlowStop_2ax
from common import Draw_YCSB_BandwidthUsage_ax, Draw_YCSB_RTWSs_SlowStop_ax
# -------------------------------------------------------Draw multiple plots of the same db in one fig and show-------------------------------------------------------#

def Draw_Throughput_CCs(LOG_list, report_list, iostat_list,cpustat_list, path_list,figpath, figname,workload, cores, arrivalrate, bkthreads, cache, distribution):
    plt.rcParams["font.family"] = "Times New Roman"
    figtitle_list = ["BlockCache = 256MB", "BlockCache = 10GB", "OSCache"]
    plt.rcParams["font.family"] = "Times New Roman"
    col = len(figtitle_list)
    row = 2
    fig, axes = plt.subplots(row, col, sharex='col', sharey='row', figsize=(16 * col, 6 * row))
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
        Draw_TptYCSB_RTWSs_SlowStop_2ax(axes[0][i], LOG, report, True, figtitle, addylabel, False, False, None, legend)
        Draw_YCSB_BandwidthUsage_ax(axes[1][i], LOG, report, iostat, False, None, addylabel, True, legend)

    for ax in axes.flat:
        for spine in ax.spines.values():
            spine.set_linewidth(10)
    plt.subplots_adjust(wspace=0.05, hspace=0.1)
    plt.subplots_adjust(top=0.9, bottom=0.2)
    plt.subplots_adjust(left=0.06, right=0.99)
    plt.savefig(figpath + figname + ".pdf", dpi=fig.dpi, pad_inches=0.0)
    plt.show()

if __name__ == '__main__':
    rd = "r1"
    ip = 236
    # cache = "CachePinL0"
    cache = ""
    arrivalrate = 30
    bkthreads = "F2C6"
    cores = 128
    distribution = "zipfian"
    dir = "{}_aa300k_{}_ip{}".format(distribution, bkthreads, ip)
    workloads = ["90w10r", "70w30r", "50w50r", "30w70r"]
    workloads = ["10w90r"]
    EXP_PATH = PATH + "BlockCache/{}/".format(dir)
    figpath = PATH + "BlockCache/fig/"
    LOG_list = []
    report_list = []
    iostat_list = []
    cpustat_list = []
    for workload in workloads:
        path_list = [
            # EXP_PATH + "BlockCache8MB_{}_MT2_cores{}_AA300K_workloada-{}-{}_r1/".format(bkthreads, cores, workload, distribution),
            EXP_PATH + "BlockCache256MB_{}_MT2_cores{}_AA300K_workloada-{}-{}_r1/".format(bkthreads,cores, workload, distribution),
            # EXP_PATH + "BlockCache1GB_{}_MT2_cores{}_AA300K_workloada-{}-{}_r1/".format(bkthreads,cores, workload, distribution),
            EXP_PATH + "BlockCache10GB_{}_MT2_cores{}_AA300K_workloada-{}-{}_r1/".format(bkthreads,cores, workload, distribution),
            # EXP_PATH + "BlockCache50GB_{}_MT2_cores{}_AA300K_workloada-{}-{}_r1/".format(bkthreads,cores, workload, distribution),
            # EXP_PATH + "BlockCache100GB_{}_MT2_cores{}_AA300K_workloada-{}-{}_r1/".format(bkthreads,cores, workload, distribution),
            EXP_PATH + "OSCache_{}_MT2_cores{}_AA300K_workloada-{}-{}_r1/".format(bkthreads,cores, workload, distribution),
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
        figname = "{}-{}-{}-BlockCache".format(dir, workload,rd)
        Draw_Throughput_CCs(LOG_list, report_list, iostat_list,cpustat_list, path_list, figpath, figname, workload, cores, arrivalrate, bkthreads,cache, distribution)
