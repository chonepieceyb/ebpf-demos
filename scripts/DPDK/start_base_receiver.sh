#!/bin/zsh

source color.sh
source common.sh 

CPUMAP=$(make_cpu_map 0 "10-19" "30-35")
NB_CORE=16
RXQ=16
TXPKTS=64
RUN_CPUMAP=$(make_cpu_map "10-19" "30-35")
PORT_MASK=0x1
CURRENT_PATH=$(cd "$(dirname "$0")"; pwd)

#CPUMAP=0x6A400A0801

set -v
eval $(echo "sudo dpdk-testpmd -c ${CPUMAP} --main-lcore 0 -- -a 
    --forward-mode=rxonly --stats-period=1 --coremask=${RUN_CPUMAP} --portmask=${PORT_MASK}
    --nb-cores=${NB_CORE} --rxq=${RXQ} --numa")