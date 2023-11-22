#!/bin/bash 
cpu=$(cat /proc/cpuinfo | grep processor | wc -l)

echo "using libbpf from https://github.com/libbpf/libbpf.git"
echo "you may also using libbpf from linux source tree by create soft link of linux source code in ./linux"

set -e

git submodule init 
git submodule update 

echo "builing ./deps/libbpf/"
pushd "./deps/libbpf/src" > /dev/null
make -j $cpu
popd > /dev/null

if [ -d "./linux"]; then
    echo "builing ./linux/tools/lib/bpf (libbpf)"
    pushd "./linux/tools/lib/bpf" > /dev/null
    make -j $cpu 
    echo "builing ./linux/tools/bpf (bpftool)"
    cd ../bpf
    make -j $cpu 
    popd > /dev/null
else
    set +e
    dpkg --list | grep linux-tools-$(uname -r)
    if (( $? != 0 )); then 
        echo "try to install linux-tools-$(uname -r)"
        set -e
        sudo apt-get install linux-tools-$(uname -r)
    else 
        echo "found linux-tools-$(uname -r)"
        set -e 
    fi 
fi 

echo "generate vmlinux.h"

./scripts/gen_vmlinux_h.sh

echo "building demo" 

cmake -B build ./
pushd build > /dev/null
make -j $cpu 
pushd > /dev/null

echo "bpf objects install in ./install"
echo "demo bin install in ./bin" 