cmake_minimum_required(VERSION 3.10)

project(ebpf_demo_user VERSION 1.0)

set(EXECUTABLE_OUTPUT_PATH "${BIN_TARGETS}")

if (EXISTS "${LINUX_PATH}")
    set(LIBBPF_SEARCH_PATH "${LINUX_PATH}/tools/lib/bpf")
else()
    set(LIBBPF_SEARCH_PATH "${LIBBPF_PATH}/src")
endif()

find_library(LIBBPF NAMES bpf HINTS "${LIBBPF_SEARCH_PATH}" REQUIRED)

file(GLOB BLACK_LIST "${C_FILES}/*.black")
file(GLOB TARGET_LIST "${C_FILES}/*_user.c")

aux_source_directory(${PROJECT_SOURCE_DIR} SRC_LIST)

list(REMOVE_ITEM SRC_LIST ${TARGET_LIST})
list(REMOVE_ITEM SRC_LIST ${BLACK_LIST})

foreach(TF ${TARGET_LIST})
    get_filename_component(TN ${TF} NAME_WE)
    add_executable(${TN} ${SRC_LIST} ${TF})
    if (EXISTS "${LINUX_PATH}")
        target_include_directories(${TN} PUBLIC "${LINUX_PATH}/tools/include/uapi")
        target_include_directories(${TN} PUBLIC "${LINUX_PATH}/tools/lib")
    endif()
    target_link_libraries(${TN} ${LIBBPF})
endforeach()

set(CMAKE_C_FLAGS
    "${CMAKE_C_FLAGS} -O2"
)
