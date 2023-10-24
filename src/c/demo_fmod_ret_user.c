
#include "common.h" 
#include <stdio.h>
#include <assert.h> 
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include "bpf_skel/demo_fmod_ret.skel.h"

#define TEST_FILE_NAME "demo_fmod_ret_test_file"
const char buf[4] = {'0'};

#define ERR_RES -120

int main(int argc, char **argv) {
    /* create a test file */
    struct demo_fmod_ret* skel; 
    int res; 
    int fd; 
   
    fd = open("demo_fmod_ret_test_file", O_CREAT);
    if (fd == -1) {
        printf("create file error, err: %d\n", errno);
        goto clean;
    }
    
    skel = demo_fmod_ret__open();
    if (!skel)
        goto clean;
    skel->bss->filter_fd = fd;
    skel->bss->err_res = ERR_RES;
    res = demo_fmod_ret__load(skel);
    if (res)
        goto clean;
    res = demo_fmod_ret__attach(skel);
    if (res)
        goto clean;

    res = write(fd, buf, sizeof(buf));
    assert(res == ERR_RES && "when attach res != ERR_RES");
clean:
    close(fd);
    demo_fmod_ret__destroy(skel);
}



