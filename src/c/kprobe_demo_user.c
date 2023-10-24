
#include "common.h" 
#include <stdio.h>
#include <assert.h> 

int main(int argc, char **argv) {
        
    assert(argc == 3 && "usage ./kprobe_demo_user path_of_bpf_oject program_name");

    const char *object_path = argv[1];
    const char *program_name = argv[2];
    struct bpf_object *obj;
    struct bpf_program *prog;
    struct bpf_link *link;
    int res = 0; 

    obj = bpf_object__open(object_path);

    if (obj == NULL) {
        printf("faild to open BPF object %s", object_path);
        res = -1;
        goto exit;
    }
    
    res = bpf_object__load(obj);

    if (res < 0) {
        printf("faild to load BPF object %s", object_path);
        goto close_obj;
    }

    prog = bpf_object__find_program_by_name(obj, program_name);

    if (prog == NULL) {
        printf("faild to find BPF program %s", program_name);
        goto close_obj;
    }
    
    link = bpf_program__attach_kprobe(prog, false, "__sys_connect");
    
    if (link == NULL) {
        printf("faild to find attach kprobe");
        goto close_obj;
    }

    //pin link to vfs
    res = bpf_link__pin(link, "/sys/fs/bpf/kprobe_demo_link");

    if (res < 0) {
        printf("faild to pin link");
    } else {
        bpf_link__disconnect(link);
    }

    res = bpf_link__destroy(link);

close_obj:
    bpf_object__close(obj);
    
exit:
    return res;
}



