#include "common.h"
#include "vmlinux.h"

char _license[] SEC("license") = "GPL";


SEC("xdp")
int xdp_main(struct xdp_md *ctx) {
        log_debug("xdp_empty %d", 1);
        return XDP_PASS;
}
