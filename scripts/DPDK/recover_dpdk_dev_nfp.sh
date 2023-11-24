#!/bin/bash

source color.sh
source nfpnic_info.sh
set -e

sudo dpdk-hugepages.py -u
sudo dpdk-hugepages.py -c
sudo dpdk-devbind.py --bind=nfp $PCI_BUSINFO_0

sudo ip link set dev $NICNAME0 up
sudo netplan apply

echo -e "${COLOR_GREEN} [INFO] unbind nic $NICNAME0 $NICNAME1 from dpdk${COLOR_OFF}"

