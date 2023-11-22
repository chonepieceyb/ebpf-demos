#!/bin/bash 
COLOR_RED='\033[0;31m'
COLOR_GREEN='\033[0;32m'
COLOR_YELLOW='\033[0;33m'
COLOR_OFF='\033[0m' # No Color
cpu=$(cat /proc/cpuinfo | grep processor | wc -l)




set -e

if [ -d "./linux" ]; then
    echo -e "${COLOR_GREEN} [INFO] using libbpf from ./linux source code${COLOR_OFF}"
    echo -e "${COLOR_GREEN} [INFO] builing ./linux/tools/lib/bpf (libbpf)${COLOR_OFF}"
    pushd "./linux/tools/lib/bpf" > /dev/null
    make clean 
    make -j $cpu 
    echo -e "${COLOR_GREEN} [INFO] builing ./linux/tools/bpf (bpftool)${COLOR_OFF}"
    cd ../bpf
    make clean 
    make -j $cpu 
    popd > /dev/null
else
    echo -e "${COLOR_GREEN} [INFO] using libbpf from https://github.com/libbpf/libbpf.git${COLOR_OFF}"
    echo -e "${COLOR_GREEN} [INFO] you may also using libbpf from linux source tree by create soft link of linux source code in ./linux${COLOR_OFF}"
    git submodule init 
    git submodule update 
    echo -e "${COLOR_GREEN} [INFO] builing ./deps/libbpf/${COLOR_OFF}"
    pushd "./deps/libbpf/src" > /dev/null
    make clean
    make -j $cpu
    popd > /dev/null
    set +e
    dpkg --list | grep linux-tools-$(uname -r)
    if (( $? != 0 )); then 
        echo -e "${COLOR_GREEN} [INFO] try to install linux-tools-$(uname -r)${COLOR_OFF}"
        set -e
        sudo apt-get install linux-tools-$(uname -r)
    else 
        echo -e "${COLOR_GREEN} [INFO] found linux-tools-$(uname -r)${COLOR_OFF}"
        set -e 
    fi     
fi 

echo -e "${COLOR_GREEN} [INFO] generate vmlinux.h${COLOR_OFF}"

./scripts/gen_vmlinux_h.sh

echo -e "${COLOR_GREEN} [INFO] building demo${COLOR_OFF}" 

rm -rf ./build
rm -rf ./install

cmake -B build ./
pushd build > /dev/null
make
pushd > /dev/null

echo -e "${COLOR_GREEN} [INFO] bpf objects install in ./install${COLOR_OFF}"
echo -e "${COLOR_GREEN} [INFO] demo bin install in ./bin${COLOR_OFF}" 