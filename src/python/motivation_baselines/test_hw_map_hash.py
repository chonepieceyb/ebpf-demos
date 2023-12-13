from bcc import BPF 
import ctypes as ct 
import sys
import os
sys.path.append("..")
from common import *

hw_offloading_map = '''
int xdp_main(struct xdp_md *ctx) {
    __u64 len = ctx->data_end - ctx->data;
    bpf_trace_printk("pkt len %lu", len);
    return XDP_DROP;
}
'''
DEV_NAME = "ens4np0"
DEVICE = DEV_NAME.encode(encoding = "utf-8") 


'''
result: 
baseline tested 
19.5M   19.5M
'''

if __name__ == '__main__': 
    bpf = BPF(text=hw_offloading_map, cflags=['-g'])
    # hw_map = bpf.get_table("hw_map")
    # hw_map[ct.c_int(0)] = ct.c_uint64(0)
    hw_fn = bpf.load_func("xdp_main", BPF.XDP)
    
    os.system("%s %s all"%(XDP_CLEAR_SCRIPT_PATH, DEV_NAME))
    bpf.attach_xdp(DEVICE, fn = hw_fn, flags=BPF.XDP_FLAGS_SKB_MODE)
    