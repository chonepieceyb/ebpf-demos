import os 

PYTHON_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.dirname(PYTHON_DIR)
PROJECT_ROOT_DIR =  os.path.dirname(SRC_DIR)
LINUX_SRC_DIR = os.path.join(PROJECT_ROOT_DIR, "linux")
LIBBPF_SO_PATH = os.path.join(LINUX_SRC_DIR, 'tools', 'lib', 'bpf', 'libbpf.so')
BPF_KERN_OBJ_DIR = os.path.join(PROJECT_ROOT_DIR, 'install', 'bpf_kern_objs')

