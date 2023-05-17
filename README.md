# eBPF-demos 

为了能够更快速地编译eBPF内核态和用户态程序，同时用python封装了libbpf，能够用python进行快速地技术验证。

## How to use

1. 将linux源代码下载到根目录（或者建立软连接）

2. 编译libbpf 和 bpftool 

    ```sh
    #编译libbpf
    cd ./linux/tools/lib/bpf
    make 
    #编译bpftool
    cd ./linux/tools/bpf/bpftool
    make 
    ```

    ps : scripts里的 gen_vmlinux.h 依赖于bpftool 

    ​	   cmake中的编译选项依赖于libbpf

    ​       也可以自行修改相应的编译脚本

3. 将eBPF内核态程序放到 `src/bpf_kern` 下

4. 将C文件放到 `src/c` 下 （如果含有main函数需要 后缀为 _user.c) 

5. python封装的使用方式查看 bpftools.py 

6. 编译

    ```sh 
    #在根目录下
    cmake -B build .
    cd build 
    make 
    make install 
    ```

7. 被编译的eBPF字节码放在 `./install/bpf_kern_objs` 

8. bin文件放在 `./bin` 