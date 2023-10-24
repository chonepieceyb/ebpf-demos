import sys
sys.path.append("..")
from bpftools import *

if __name__ == '__main__':
    from common import *
    import os 
    DEMO_FMOD_RET_OBJ_PATH = os.path.join(BPF_KERN_OBJ_DIR, 'demo_fmod_ret.c.o')
    with BPFObject(DEMO_FMOD_RET_OBJ_PATH) as bpf_obj:
        bpf_obj.load()
        bpf_prog = bpf_obj.get_prog("demo_fmod_ret")
        with BPFLink(bpf_program__attach_trace, bpf_prog) as link: 
            link.disconnect()
            try:
                while True:
                    pass
            except KeyboardInterrupt:
                pass