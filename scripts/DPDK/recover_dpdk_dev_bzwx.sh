#!/bin/bash

source color.sh
source bzwxnic_info.sh
set -e

sudo dpdk-hugepages.py -u
sudo dpdk-hugepages.py -c
#sudo dpdk-devbind.py --bind=ncepf $PCI_BUSINFO_0
sudo dpdk-devbind.py --bind=ncevf $PCI_BUSINFO_0

sudo ip link set dev $NICNAME0 up
sudo netplan apply

echo -e "${COLOR_GREEN} [INFO] unbind nic $NICNAME0 from dpdk${COLOR_OFF}"