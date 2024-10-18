#!/bin/bash

load(){
sudo setsid iostat -x $DEVICE $report_interval_seconds > ${iostat_dir}/${4}_iostat &
IOPID=$!
sudo setsid $1 load rocksdb -s -P $2 -p rocksdb.optionsfile=$3 -p rocksdb.dir="${db_dir}/${4}" -p status.interval=$report_interval_seconds -threads $threads |& tee > ${report_dir}/${4}_report &
YCSB_PID=$!
wait "$YCSB_PID"
sudo pkill -9 iostat
wait "$IOPID"
}

run(){
sudo setsid mpstat -P 0-$(($cpucore-1)) $report_interval_seconds > ${iostat_dir}/${4}_cpustat &
CPUPID=$!
sudo setsid iostat -x $DEVICE $report_interval_seconds > ${iostat_dir}/${4}_iostat &
IOPID=$!
sudo setsid $1 run rocksdb -s -P $2 -p rocksdb.optionsfile=$3 -p rocksdb.dir="${db_dir}/${4}" -p status.interval=$report_interval_seconds -threads $threads -target $ops_per_sec |& tee > ${report_dir}/${4}_report &
YCSB_PID=$!
wait "$YCSB_PID"
sudo kill -9 "$IOPID"
sudo kill -9 "$CPUPID"
sudo pkill -9 mpstat
sudo pkill -9 iostat
wait "$IOPID" "$CPUPID"
}

run_cleanup(){
sudo setsid iostat -x $DEVICE $report_interval_seconds > ${iostat_dir}/${4}_iostat &
IOPID=$!
sudo setsid $1 run rocksdb -s -P $2 -p rocksdb.optionsfile=$3 -p rocksdb.dir="${db_dir}/${4}" -p status.interval=$report_interval_seconds -threads 1 |& tee > ${report_dir}/${4}_report &
YCSB_PID=$!
wait "$YCSB_PID"
sudo pkill -9 iostat
wait "$IOPID"
}

copy_res_load(){
	cures_dir=${expres_dir}/${2}

	if [ ! -d "$cures_dir" ]; then
  	sudo mkdir -p "$cures_dir"
	fi
	
	#space
	sudo du ${db_dir}/${1} -h > ${cures_dir}/${2}_load-space
	#LOG
	sudo mv ${db_dir}/${1}/LOG ${cures_dir}/${2}_load-LOG
	#report
	sudo mv ${report_dir}/${1}_report ${cures_dir}/${2}_load-report
	#iostat
	sudo mv ${iostat_dir}/${1}_iostat ${cures_dir}/${2}_load-iostat

	sudo tar -zcvf ${expres_dir}/${2}.tar.gz -C ${expres_dir} ${2}
}

copy_res_run(){
	cures_dir=${expres_dir}/${2}

	if [ ! -d "$cures_dir" ]; then
  	sudo mkdir -p "$cures_dir"
	fi
	
	#space
	sudo du ${db_dir}/${1} > ${cures_dir}/${2}_run-space
	#LOG
	sudo mv ${db_dir}/${1}/LOG ${cures_dir}/${2}_run-LOG
	#report
	sudo mv ${report_dir}/${1}_report ${cures_dir}/${2}_run-report
	#iostat
	sudo mv ${iostat_dir}/${1}_iostat ${cures_dir}/${2}_run-iostat
	#cpustat
	sudo mv ${iostat_dir}/${1}_cpustat ${cures_dir}/${2}_run-cpustat

	sudo tar -zcvf ${expres_dir}/${2}.tar.gz -C ${expres_dir} ${2}

}

finalize(){
	sudo rm -rf ${db_dir}/${1}
}

expname="ArrivalRate"

DISK="NVMeSSD" # or "SATAHDD"
if [ "$DISK" == "NVMeSSD" ]; then
    DEVICE="/dev/nvme0n1"
elif [ "$DISK" == "SATAHDD" ]; then
    DEVICE="/dev/sda3"
else
    echo "Unknown DISK value: $DISK"
    exit 1
fi

global_dir="/home/cc/Hannah"
YCSB="${global_dir}/YCSB/bin/ycsb.sh"
db_dir="${global_dir}/DBs"
report_dir="${global_dir}/Reports"
iostat_dir="${global_dir}/IOstat"
res_dir="${global_dir}/Res"
expres_dir="${res_dir}/${expname}"

workloads_dir="${global_dir}/Workloads/run/${expname}"
load_workloads_dir="${global_dir}/Workloads/load"
optionsfiles_dir="${global_dir}/OPTIONSfile/${expname}"

report_interval_seconds=1
ops_per_sec=150000
threads=100

cpucore=96
loaddata=100 #100GB

is_integer() {
    [[ $1 =~ ^-?[0-9]+$ ]]
}

# Parse arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --cpucore)
            if is_integer "$2"; then
                cpucore="$2" # Assign the value of the next parameter to cpucore
                shift 2 # Shift to the next pair of parameters
            else
                echo "Error: --cpucore requires an integer value"
                exit 1
            fi
            ;;
         --ops_per_sec)
            if is_integer "$2"; then
                ops_per_sec="$2" # Assign the value of the next parameter to ops_per_sec
                shift 2 # Shift to the next pair of parameters
            else
                echo "Error: --ops_per_sec requires an integer value"
                exit 1
            fi
            ;;
        --loaddata)
            if is_integer "$2"; then
                loaddata="$2" # Assign the value of the next parameter to loaddata
                shift 2 # Shift to the next pair of parameters
            else
                echo "Error: --loaddata requires an integer value"
                exit 1
            fi
            ;;
        *) 
            echo "Unknown parameter passed: $1"
            exit 1
            ;;
    esac
done

workloadsfiles=(
	"workloada-100w0r-zipfian"
	# "workloada-90w10r-zipfian"
	# "workloada-70w30r-zipfian"
	# "workloada-50w50r-zipfian"
	# "workloada-30w70r-zipfian"
	# "workloada-10w90r-zipfian"
	# "workloada-0w100r-zipfian"
	)

optionsfilenames=(
	"F1C3_MT2"
	# "F32C96_MT2"
	)

optionsfiles=(
	"F1C3_MT2.ini"
	# "F32C96_MT2.ini"
	)


clean_workload_dir="${workloads_dir}/clean-allread"

optionsfile_dir="${optionsfiles_dir}/${optionsfiles[1]}"
optionsfilename=${optionsfilenames[1]}
filename="RDB_${loaddata}G"

#load zipfian
workloadfile="load-${loaddata}GB-zipfian"
workload_dir="${load_workloads_dir}/${workloadfile}"
res_filename="${filename}-load-threads${threads}"
# echo $filename $res_filename
# echo "$(date '+%Y-%m-%d %H:%M:%S') Starting Load $res_filename" && load $YCSB $workload_dir $optionsfile_dir $filename && echo "$(date '+%Y-%m-%d %H:%M:%S') Finished Load $res_filename"
# wait
# echo "Starting copy load $res_filename" && copy_res_load $filename $res_filename && echo "Finished copy load $res_filename"
# wait 


echo "---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------"

for (( i=0; i<${#optionsfiles[@]}; i++ ))
do
	optionsfile_dir="${optionsfiles_dir}/${optionsfiles[$i]}"
	echo "-------------Optionsfile: ${optionsfiles[$i]} -------------"
	optionsfilename=${optionsfilenames[$i]}
	for (( j=0; j<${#workloadsfiles[@]}; j++ ))
  	do
  		workloadfile=${workloadsfiles[$j]}
  		workload_dir="${workloads_dir}/${workloadfile}"
  		ops_per_sec_k=$(($ops_per_sec / 1000))K
		res_filename="AA${ops_per_sec_k}_${optionsfilename}_cores${cpucore}_${workloadfile}_r1"

  		echo "$(date '+%Y-%m-%d %H:%M:%S') Starting clean" && run_cleanup $YCSB $clean_workload_dir $optionsfile_dir $filename && echo "$(date '+%Y-%m-%d %H:%M:%S') Finished clean"
  		wait
  	
  		echo "$(date '+%Y-%m-%d %H:%M:%S') Starting run $res_filename" && run $YCSB $workload_dir $optionsfile_dir $filename && echo "$(date '+%Y-%m-%d %H:%M:%S') Finished run $res_filename"
		wait
		echo "Starting copy run $res_filename" && copy_res_run $filename $res_filename && echo "Finished copy run $res_filename"
		wait
  	done
done

echo "---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------"
