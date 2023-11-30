#!/bin/bash

source color.sh


source $CURRENT_PATH/config/bzwxnic_info.sh

set -e 
./setup_dpdk_hugepage.sh

set -e
sudo modprobe vfio
sudo modprobe vfio-pci

set +e
#sudo ip link set dev $NICNAME0 down > /dev/null
#sudo ip link set dev $NICNAME1 down > /dev/null
sudo ip link set dev ${NICNAME0} down 

set -e
sudo dpdk-devbind.py --bind=vfio-pci ${NICNAME0}

echo -e "${COLOR_GREEN} [INFO] bind nic $NICNAME0 to dpdk${COLOR_OFF}"
sudo dpdk-devbind.py -s
