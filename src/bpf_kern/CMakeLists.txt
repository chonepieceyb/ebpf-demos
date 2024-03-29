cmake_minimum_required(VERSION 3.10)

project(ebpf_demos VERSION 0.1)

file(GLOB BLACK_LIST "${BPF_KERN_SRC_FILES}/*.black")

aux_source_directory("${BPF_KERN_SRC_FILES}" BPF_SRC_LIST)

list(REMOVE_ITEM BPF_SRC_LIST ${BLACK_LIST})

#compile all .o files
add_library(ebpf_demo OBJECT ${BPF_SRC_LIST})

if (EXISTS "${LINUX_PATH}")
    target_include_directories(ebpf_demo PUBLIC "${LINUX_PATH}/tools/lib/bpf")
else()
    target_include_directories(ebpf_demo PUBLIC "${LIBBPF_PATH}/src")
endif()

#install(FILES $<TARGET_OBJECTS:ebpf_demo> DESTINATION "${BPF_KERN_TARGETS}")
add_custom_target(bpf_copy
    COMMAND "${CMAKE_COMMAND}"
          -DTARGET_OBJS="$<TARGET_OBJECTS:ebpf_demo>"
          -DTARGET_DEST="${BPF_KERN_TARGETS}"
          -P "${CMAKE_CURRENT_SOURCE_DIR}/copy_bpf_objs.cmake"
)

add_custom_target(bpf_skel
    COMMAND "${CMAKE_COMMAND}"
          -DTARGET_DEST="${BPF_KERN_TARGETS}"
          -DTARGET_SKEL_HEADER_DIR="${BPF_SKEL_HEADERS}"
          -P "${CMAKE_CURRENT_SOURCE_DIR}/skeleton.cmake"
)

add_custom_target(bpf_install ALL
    COMMAND "${CMAKE_COMMAND}"
          -DTARGET_OBJS="$<TARGET_OBJECTS:ebpf_demo>"
          -DTARGET_DEST="${BPF_KERN_TARGETS}"
          -P "${CMAKE_CURRENT_SOURCE_DIR}/copy_bpf_objs.cmake"
    COMMAND "${CMAKE_COMMAND}"
          -DTARGET_DEST="${BPF_KERN_TARGETS}"
          -DTARGET_SKEL_HEADER_DIR="${BPF_SKEL_HEADERS}"
          -P "${CMAKE_CURRENT_SOURCE_DIR}/skeleton.cmake"
)

add_dependencies(bpf_install ebpf_demo)

set(CMAKE_C_FLAGS
    "${CMAKE_C_FLAGS} -Werror -g -O2 -target bpf"
)
