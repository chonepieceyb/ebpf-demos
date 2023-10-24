cmake_minimum_required(VERSION 3.15)

set (CMAKE_C_COMPILER "/usr/bin/clang")
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

project(ebpf_demos VERSION 0.1)

set(CMAKE_INSTALL_PREFIX "${PROJECT_SOURCE_DIR}/install")
set(BIN_TARGETS "${PROJECT_SOURCE_DIR}/bin")
set(LINUX_PATH "${PROJECT_SOURCE_DIR}/linux/")

#some custom vars 

set(BPF_KERN_SRC_FILES "${PROJECT_SOURCE_DIR}/src/bpf_kern")
set(BPF_KERN_TARGETS "${CMAKE_INSTALL_PREFIX}/bpf_kern_objs")
set(BPF_SKEL_HEADERS "${PROJECT_SOURCE_DIR}/src/c/bpf_skel")
set(BIN_TARGETS "${PROJECT_SOURCE_DIR}/bin")
set(C_FILES "${PROJECT_SOURCE_DIR}/src/c")

add_subdirectory("${BPF_KERN_SRC_FILES}")
add_subdirectory("${C_FILES}")

