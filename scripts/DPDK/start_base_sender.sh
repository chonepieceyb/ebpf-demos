#!/bin/zsh

source color.sh
source common.sh 

#CPUMAP=$(make_cpu_map 0 "10-19" "30-35")
MAINCORE=0
CPULIST="10-19 30-25"
CPUMAP=$(make_cpu_map $MAINCORE $(echo $CPULIST))
echo $CPUMAP
NB_CORE=16
TXQ=16
TXPKTS=64
TXD=512
BURST=64

#RUN_CPUMAP=$(make_cpu_map "10-19" "30-35")
RUN_CPUMAP=$(make_cpu_map $(echo $CPULIST))
PORT_MASK=0x1
CURRENT_PATH=$(cd "$(dirname "$0")"; pwd)

#CPUMAP=0x6A400A0801

cmd=$(echo "sudo dpdk-testpmd -c ${CPUMAP} --main-lcore ${MAINCORE} -- -i \
    --forward-mode=txonly --stats-period=1 --coremask=${RUN_CPUMAP} --portmask=${PORT_MASK} \
    --nb-cores=${NB_CORE} --txq=${TXQ} --txd=${TXD} --burst=${BURST} --numa --txpkts=${TXPKTS} --eth-peers-configfile=${CURRENT_PATH}/eth_peers.config")
echo $cmd
eval $cmd