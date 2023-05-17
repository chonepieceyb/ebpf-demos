#!/bin/bash

source $(cd "$(dirname "$0")"; pwd)"/"common.sh 

OUTPUT=$BPF_KERN_DIR"vmlinux.h" 

$BPF_TOOL_PATH btf dump file /sys/kernel/btf/vmlinux format c > $OUTPUT 
