#!/bin/bash

source color.sh
CURRENT_PATH=$(cd "$(dirname "$0")"; pwd)
source $CURRENT_PATH/config/nfpnic_info.sh

set -e 
./setup_dpdk_hugepage.sh

set -e 
./setup_dpdk_hugepage.sh

set +e
sudo rmmod vfio-pci
set -e
sudo modprobe vfio-pci disable_idle_d3=1

set +e
sudo ip link set dev $NICNAME0 down > /dev/null
sudo ip link set dev $NICNAME1 down > /dev/null

set -e
sudo dpdk-devbind.py --bind=vfio-pci $PCI_BUSINFO_0

echo -e "${COLOR_GREEN} [INFO] bind nic $NICNAME0 to dpdk${COLOR_OFF}"
sudo dpdk-devbind.py -s
