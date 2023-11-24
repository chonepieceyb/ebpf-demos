#!/bin/bash
#setup base DPDK configuration 

source color.sh

set -e 

PAGE_SIZE="1G"
TOTAL_PAGE_SIZE="10G"

function echo_help() {
    echo "usage: $0 [numa_node]"
    exit -1
}

if (( $# > 1 )); then
    echo_help
fi 

function numa_num() {
    lscpu | grep NUMA | awk 'END{print NR -1}'
}

function check_dpdkhugepages() {
    set +e 
    sudo dpdk-hugepages.py -s | awk '/^'"$1"'/{if($3 ~ /'"$PAGE_SIZE"'/ && $4 ~ /'"$TOTAL_PAGE_SIZE"'/) {print "yes"}}' | grep yes > /dev/null
}

function check_dpdkhugepages_all() {
    numa_node_num=$(numa_num)
    set +e 
    sudo dpdk-hugepages.py -s | awk 'BEGIN {count=0} /^[0-9]/{if($3 !~ /'"$PAGE_SIZE"'/ || $4 !~ /'"$TOTAL_PAGE_SIZE"'/) {exit -1}; count+=1} END {print count}' | grep "${numa_node_num}" > /dev/null
}

#test if huge pages have been set
if (( $# ==1 )); then 
    check_dpdkhugepages $1
else 
    check_dpdkhugepages_all
fi
if (( $? == 0 )); then 
    echo -e "${COLOR_GREEN} [INFO] hugepage has been set${COLOR_OFF}"
    sudo dpdk-hugepages.py -s
    exit 0 
fi 
set -e 

#clear dpdk-hugeapages configuration 
sudo dpdk-hugepages.py -u
sudo dpdk-hugepages.py -c

#setup dpdk-hugepages 

if (( $# ==1 )); then 
    sudo dpdk-hugepages.py -n $1 -p ${PAGE_SIZE} --setup ${TOTAL_PAGE_SIZE}
else 
    sudo dpdk-hugepages.py  -p ${PAGE_SIZE} --setup ${TOTAL_PAGE_SIZE}
fi 

echo -e "${COLOR_GREEN} [INFO] configure huge pages for node $1 success${COLOR_OFF}"
sudo dpdk-hugepages.py -s