#!/bin/sh
#source ~/.profile
workdir=$1
tdstr=$(date -d "1 day ago" +%Y%m%d)
#logfile="/bigdata/hydra_log/flow/stat/"$tdstr".log"
cd $workdir
python $workdir/rules/check_log.py $workdir
