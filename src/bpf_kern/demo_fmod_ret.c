#include "common.h"

#define __TARGET_ARCH_x86
#include <bpf/bpf_tracing.h>

char _license[] SEC("license") = "GPL";
char buf[256] = {0};

unsigned int filter_fd;
int err_res;

SEC("fmod_ret/__x64_sys_write")
int BPF_PROG(demo_fmod_ret, const struct pt_regs *regs) {
        unsigned int fd = PT_REGS_PARM1(regs);
        //bpf_get_current_comm(buf, sizeof(buf));
        // if (bpf_strncmp(buf, sizeof(buf), "python3") == 0) {
        //         bpf_printk("deny write write from python3, %u", fd);
        //         return -1;
        // }
        if (fd == filter_fd) {
                bpf_printk("deny write write to fd, %u", fd);
                return err_res;
        }
        return 0;
        /*normal*/
        //return 0;
}