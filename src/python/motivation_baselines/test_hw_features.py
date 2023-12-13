from bcc import BPF 
import ctypes as ct 
import sys
import os
sys.path.append("..")
from common import *

hw_offloading_map = '''

BPF_ARRAY(hw_map, __u64, 1);

int xdp_main(struct xdp_md *ctx) {
    int key = 0;
    __u64 *count;
    count = hw_map.lookup(&key);
    if (count == NULL) {
        return XDP_DROP;
    }
    __sync_fetch_and_add(count, 1);
    return XDP_PASS;
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
    bpf = BPF(text=hw_offloading_map, cflags=['-g'], device = DEVICE)
    hw_map = bpf.get_table("hw_map")
    hw_map[ct.c_int(0)] = ct.c_uint64(0)
    hw_fn = bpf.load_func("xdp_main", BPF.XDP, device = DEVICE)
    
    os.system("%s %s all"%(XDP_CLEAR_SCRIPT_PATH, DEV_NAME))
    bpf.attach_xdp(DEVICE, fn = hw_fn, flags = BPF.XDP_FLAGS_HW_MODE)