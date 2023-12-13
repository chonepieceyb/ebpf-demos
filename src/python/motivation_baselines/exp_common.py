from bcc import BPF 
import sys
import logging
sys.path.append("..")
from utils import *
from datetime import datetime
from common import *
import copy

RESULT_DATA_FORMAT="%Y-%m-%d-%H-%M"

default_bcc_args = {
    "cflags" : ['-g'],
    #"debug" : 0x8,
}

def default_map_create(bpf, user_context = None):
    logging.debug("empty map_creating action")

def default_pre_prog_load(bpf, user_context = None):
    funcs = ["xdp_main"]
    funcs_info = " ".join(funcs)
    logging.debug("default loading %s", funcs_info)
    return funcs

def default_pre_prog_attach(bpf, funcs, user_context = None):
    func_name = "xdp_main"
    fn = funcs["xdp_main"]
    logging.debug("default attaching %s", func_name)
    return func_name, fn
    
def default_post_prog_attach(bpf, funcs, user_context = None):
    logging.debug("empty post_attach action")

# default_hook_fns = {
#     "map_create" : default_map_create,
#     "pre_prog_load" : default_pre_prog_load,
#     "pre_prog_attach": default_pre_prog_attach,
#     "post_prog_attach": default_post_prog_attach
# }

def dettach_xdp_all(devname):
    os.system("%s %s all"%(XDP_CLEAR_SCRIPT_PATH, devname))

def __attach_xdp(mode, text, devname, default_action, *, hook_fns = {}, bcc_args = default_bcc_args, user_context = None, debug):
    mode_dict = {
        "hw": BPF.XDP_FLAGS_HW_MODE,
        "skb": BPF.XDP_FLAGS_SKB_MODE,
        "drv": BPF.XDP_FLAGS_DRV_MODE
    }
    
    assert mode in mode_dict and "mode not in [\"hw\", \"skb\", \"drv\"]"
    map_create_fn = hook_fns.get("map_create", default_map_create)
    pre_prog_load_fn = hook_fns.get("pre_prog_load", default_pre_prog_load)
    pre_prog_attach_fn = hook_fns.get("pre_prog_attach", default_pre_prog_attach)
    post_prog_attach_fn = hook_fns.get("post_prog_attach", default_post_prog_attach)
    __bcc_args = copy.deepcopy(bcc_args)
    cflags = __bcc_args.get("cflags", ["-g"])
    cflags.append("-DDEFAULT_ACTION=%s"%default_action)
    debug_flags = __bcc_args.get("debug", 0)
    if debug:
        debug_flags |= 0x8
    __bcc_args["cflags"] = cflags
    __bcc_args["debug"] = debug_flags
    
    if pre_prog_load_fn == None: 
        logging.error("[%s] pre_prog_load_fn is None", mode)
        raise RuntimeError("[%s] pre_prog_load_fn is None", mode)
    if pre_prog_attach_fn == None: 
        logging.error("[%s] pre_prog_attach_fn is None", mode)
        raise RuntimeError("[%s] pre_prog_attach_fn is None", mode)
    
    device = devname.encode(encoding = "utf-8") 
    if mode == "hw": 
        bpf = BPF(text=text, device = device, **__bcc_args)
    else:
        bpf = BPF(text=text, **__bcc_args)
    
    if map_create_fn != None:
        map_create_fn(bpf, user_context)
        
    func_names = pre_prog_load_fn(bpf, user_context)
    funcs = {}
    for func_name in func_names:
        logging.debug("[%s] loading bpf xdp prog %s ...", mode, func_name)
        if mode == "hw":
            fn = bpf.load_func(func_name, BPF.XDP, device = device)
        else:
            fn = bpf.load_func(func_name, BPF.XDP)
        funcs[func_name] = fn
    
    #attach 
    attach_funcname, attach_fn = pre_prog_attach_fn(bpf, funcs, user_context)
    logging.debug("[%s] attaching bpf xdp prog %s ...", mode, attach_funcname)
    bpf.attach_xdp(devname, fn = attach_fn, flags = mode_dict[mode]) 
    if post_prog_attach_fn != None: 
        post_prog_attach_fn(bpf, funcs, user_context)

def attach_xdp_hw(text, devname, *, hook_fns = {}, \
                default_action = "XDP_PASS", bcc_args = default_bcc_args, user_context = None, debug = False):
    __attach_xdp("hw", text, devname, default_action, hook_fns = hook_fns, bcc_args=bcc_args, user_context=user_context, debug = debug)

def attach_xdp_skb(text, devname, *, hook_fns = {}, \
                default_action = "XDP_DROP", bcc_args = default_bcc_args, user_context = None, debug = False):
    __attach_xdp("skb", text, devname, default_action, hook_fns = hook_fns, bcc_args=bcc_args, user_context=user_context, debug = debug)

def attach_xdp_drv(text, devname, *, hook_fns = {}, \
                default_action = "XDP_DROP", bcc_args = default_bcc_args, user_context = None, debug = False):
    __attach_xdp("drv", text, devname, default_action, hook_fns = hook_fns, bcc_args=bcc_args, user_context=user_context, debug = debug)

def attach_empty_xdp_drv(devname, default_action = "XDP_DROP"):
    prog_text = '''
int xdp_main(struct xdp_md *ctx) {
    return %s;
}
    '''%(default_action)
    attach_xdp_drv(prog_text, devname, bcc_args = default_bcc_args)

BASE_RESULT_DIR = os.path.join(RESULTS_DIR, "baseline")

def exp_common(mode, exp_name, prog_under_test, devname, *, catch_filters = [], show_filters = default_stats_filters, attach_kw = {}):
    assert mode in ["drv", "hw"] and "mode must in drv,hw"
    try:
        exp_dir= os.path.join(BASE_RESULT_DIR, exp_name)
        if not os.path.exists(exp_dir):
            os.mkdir(exp_dir)
        exp_dir_mode =  os.path.join(exp_dir, mode)
            
        time_str = datetime.now().strftime(RESULT_DATA_FORMAT)
        result_file_mode =  os.path.join(exp_dir_mode, time_str)
     
        os.system("touch %s && chmod 666 %s"%(result_file_mode, result_file_mode))
        
        #running skb two slow compared with drv and hw
        # dettach_xdp_all(devname)
        # attach_xdp_skb(prog_under_test, devname, **skb_wk)
        # stats_watching(devname, result_file_skb, 7)
        # logging.info("Exp %s skb results: "%exp_name)
        # show_stats_result(result_file_skb)
        
        #running drv 
        dettach_xdp_all(devname)
        if mode == "hw":
            attach_empty_xdp_drv(devname)
            attach_xdp_hw(prog_under_test, devname, **attach_kw)
        elif mode == "drv":
            attach_xdp_drv(prog_under_test, devname, **attach_kw)
  
        stats_watching(devname, result_file_mode, 7, filters=catch_filters)
        logging.info("Exp %s %s results: "%(exp_name, mode))
        show_stats_result(result_file_mode, filters=show_filters)
        dettach_xdp_all(devname)

    except Exception as e: 
        os.system("rm -rf %s"%(result_file_mode))
        dettach_xdp_all(devname)
        raise e

def baseline_exp(exp_name, prog_under_test, devname, *, catch_filters = [], show_filters = default_stats_filters, skb_kw = {}, drv_kw = {}, hw_kw = {}):
    '''
        baseline experiment scripts
    '''
    try:
        exp_dir= os.path.join(BASE_RESULT_DIR, exp_name)
        if not os.path.exists(exp_dir):
            os.mkdir(exp_dir)
            
        exp_dir_skb = os.path.join(exp_dir, "skb")
        if not os.path.exists(exp_dir_skb):
            os.mkdir(exp_dir_skb)
        exp_dir_drv = os.path.join(exp_dir, "drv")
        if not os.path.exists(exp_dir_drv):
            os.mkdir(exp_dir_drv)
        exp_dir_hw = os.path.join(exp_dir, "hw")
        if not os.path.exists(exp_dir_hw):
            os.mkdir(exp_dir_hw)
            
        time_str = datetime.now().strftime(RESULT_DATA_FORMAT)
        result_file_skb =  os.path.join(exp_dir_skb, time_str)
        result_file_drv  =  os.path.join(exp_dir_drv, time_str)
        result_file_hw  =  os.path.join(exp_dir_hw, time_str)
        os.system("touch %s && chmod 666 %s"%(result_file_skb, result_file_skb))
        os.system("touch %s && chmod 666 %s"%(result_file_drv, result_file_drv))
        os.system("touch %s && chmod 666 %s"%(result_file_hw, result_file_hw))
        
        #running skb two slow compared with drv and hw
        # dettach_xdp_all(devname)
        # attach_xdp_skb(prog_under_test, devname, **skb_wk)
        # stats_watching(devname, result_file_skb, 7)
        # logging.info("Exp %s skb results: "%exp_name)
        # show_stats_result(result_file_skb)
        
        #running drv 
        dettach_xdp_all(devname)
        attach_xdp_drv(prog_under_test, devname, **drv_kw)
        stats_watching(devname, result_file_drv, 7, filters=catch_filters)
        logging.info("Exp %s drv results: "%exp_name)
        show_stats_result(result_file_drv, filters=show_filters)
        
        #running hw 
        dettach_xdp_all(devname)
        attach_empty_xdp_drv(devname, drv_kw.get("default_action", "XDP_DROP"))
        attach_xdp_hw(prog_under_test, devname, **hw_kw)
        stats_watching(devname, result_file_hw, 7, filters=catch_filters)
        logging.info("Exp %s hw results: "%exp_name)
        show_stats_result(result_file_hw, filters=show_filters)
        dettach_xdp_all(devname)
    except Exception as e: 
        os.system("rm -rf %s"%(result_file_hw))
        os.system("rm -rf %s"%(result_file_skb))
        dettach_xdp_all(devname)
        raise e
    #running skb

def get_latest_result(result_dir):
    results = os.listdir(result_dir)
    if len(results) == 0:
        return 
    resultdates = [datetime.strptime(date, RESULT_DATA_FORMAT) for date in results]
    resultdates = sorted(resultdates, reverse=True)
    return datetime.strftime(resultdates[0], RESULT_DATA_FORMAT)

def print_latest_exp(exp_dir, exp_config_printer, result_filter):
    _, exp_full_name = os.path.split(exp_dir)
    print("###EXP: %s###"%exp_full_name)
    exp_config_printer(exp_full_name)
    
    for m in ["drv", "hw"]:
        print("%s:"%m)
        latest_result = get_latest_result(os.path.join(exp_dir, m))
        show_stats_result(os.path.join(exp_dir, m, latest_result), result_filter)    
    print()
    
def print_baseline_latest(result_filter, exp_classes):
    all_exps = os.listdir(BASE_RESULT_DIR)
    #filter
    #exp_filter
    for exp in all_exps:
        for exp_class in exp_classes:
            if exp.startswith(exp_class.name):
               #print drv
               print_latest_exp(os.path.join(BASE_RESULT_DIR, exp), exp_class.printer, result_filter)
    