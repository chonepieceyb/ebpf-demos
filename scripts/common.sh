#!/bin/bash

LINUX=linux

SCRIPT_DIR=$(cd "$(dirname "$0")"; pwd)"/"

PROJECT_DIR=$(cd "$(dirname "$SCRIPT_DIR")"; pwd)"/"

BPF_KERN_DIR=$PROJECT_DIR"src/bpf_kern/"

BPF_TOOL_PATH=$PROJECT_DIR$LINUX"/tools/bpf/bpftool/bpftool"
