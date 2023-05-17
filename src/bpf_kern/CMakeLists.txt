cmake_minimum_required(VERSION 3.10)

project(ebpf_demos VERSION 0.1)

file(GLOB BLACK_LIST "${BPF_KERN_SRC_FILES}/*.black")

aux_source_directory("${BPF_KERN_SRC_FILES}" BPF_SRC_LIST)

list(REMOVE_ITEM BPF_SRC_LIST ${BLACK_LIST})

#compile all .o files
add_library(ebpf_demo OBJECT ${BPF_SRC_LIST})

target_include_directories(ebpf_demo PUBLIC "${LINUX_PATH}/tools/lib")

install(FILES $<TARGET_OBJECTS:ebpf_demo> DESTINATION "${BPF_KERN_TARGETS}")

set(CMAKE_C_FLAGS
    "${CMAKE_CXX_FLAGS} -Werror -g -O2 -target bpf"
)
