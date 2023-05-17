#ifndef EBPF_DEMO_COMMON_H
#define EBPF_DEMO_COMMON_H

#include "vmlinux.h"
#include <bpf/bpf_helpers.h>

#define bpfprintk(fmt, ...)                    \
({                                              \
    	char ____fmt[] = fmt;                       \
    	bpf_trace_printk(____fmt, sizeof(____fmt),  \
             ##__VA_ARGS__);                    \
})
#endif 
