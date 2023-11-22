#!/bin/bash
source $(cd "$(dirname "$0")"; pwd)"/"common.sh 

set -e 

pushd $PROJECT_DIR > /dev/null

if [ ! -d ./build ]; then 
    cmake -B build ./
fi

cd ./build 

make -j $cpu ebpf_demo
make bpf_install

popd > /dev/null