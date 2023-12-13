from exp_common import *
import coloredlogs
import ctypes as ct 

DEV_NAME = "ens4np0"
DEBUG=False
############## EXP for lookup BPF_MAP_TYPE_ARRAY

exp_gen_random_num = '''
int xdp_main(struct xdp_md *ctx) {
    __u32 key = bpf_get_prandom_u32();
    key = bpf_get_prandom_u32();
    key = bpf_get_prandom_u32();
    key = bpf_get_prandom_u32();
    key = bpf_get_prandom_u32();
    return DEFAULT_ACTION;
}
'''

exp_lookup_hash_base = '''
BPF_HASH(map, __u32, __u64, 4096);
int xdp_main(struct xdp_md *ctx) {
    __u32 key = 0;
    __u64 *val = map.lookup(&key);
    return DEFAULT_ACTION;
}
'''
        
skb_kw = {
    "default_action": "XDP_DROP",
    "debug" : DEBUG
}

hw_kw = {
    "default_action": "XDP_PASS",
    "debug" : DEBUG
}

drv_kw = {
    "default_action": "XDP_DROP",
    "debug" : DEBUG
}

stats_filters = ["bpf_pass_pkts", "dev_rx_pkts", "mac.rx_pkts"]

class pkt_5_tuple(ct.Structure):
    _fields_  = [\
        ("src_ip", ct.c_uint32),\
        ("dst_ip", ct.c_uint32),\
        ("src_port", ct.c_uint16),\
        ("dst_port", ct.c_uint16),\
        ("proto", ct.c_uint8),\
    ]
    _pack_ = 1

def __config_printer(exp_defines, exp_configs):
    print(exp_defines["exp_configuration_base"]%exp_configs)

def config_printer(exp_defines, exp_name):
    __config_printer(sscanf(exp_defines["format"], exp_name))

###################### ARRAY LOOKUP EXP ####################

class exp_array_lookup_class:
    name = "array_lookup"
    format = "%s:%d:%d:%d"
    exp_configuration_base = '''%s configuration:
value_size: %d
max_entries: %d
lookup_times: %d'''
    exp_prog_base = '''
struct value_type {
    char data[VALUE_SIZE];
};

//BPF_ARRAY(map, struct value_type, MAX_ENTRIES);
MAP_DEFINE

int xdp_main(struct xdp_md *ctx) {
    int key = 0;
    struct value_type *val;
    MAP_LOOKUP
    return DEFAULT_ACTION;
}   
'''
    
    @classmethod
    def print_config(cls, exp_configs):
        print(cls.exp_configuration_base%exp_configs)
        
    @classmethod
    def printer(cls, exp_full_name):
        cls.print_config(sscanf(cls.format, exp_full_name))
        pass 
    
    @classmethod
    def exp(cls, times = list(range(1, 11))):
        #test array lookup times to performance
        #exp configuration 
        value_size = 56   
        max_entries = 1
        exp_name = cls.name
        exp_configs = [(exp_name, value_size, max_entries, t) for t in times]
        for exp_config in exp_configs:
            exp_full_name = cls.format%exp_config
            lookup_time = exp_config[-1]
            map_define = '\n'.join(["BPF_ARRAY(map%d, struct value_type, MAX_ENTRIES);"%i for i in range(lookup_time)])
            map_lookup = '\n'.join(["val = map%d.lookup(&key);"%i for i in range(lookup_time)])
            exp_prog = cls.exp_prog_base\
                .replace("VALUE_SIZE", str(exp_config[1]))\
                .replace("MAP_DEFINE", map_define)\
                .replace("MAX_ENTRIES", str(exp_config[2]))\
                .replace("MAP_LOOKUP", map_lookup)\
            
            logging.info("Exp %s:", exp_full_name)   
            cls.print_config(exp_config)
            logging.info("Prog under test:")
            print(exp_prog)
            baseline_exp(exp_full_name, exp_prog, DEV_NAME, show_filters= stats_filters, skb_kw=skb_kw, drv_kw=drv_kw, hw_kw=hw_kw)

###################### HASH LOOKUP EXP ####################

def hash_pre_prog_load(bpf, user_context):
    key_size = user_context["key_size"]
    value_size = user_context["value_size"]
    me = user_context["me"]
    time = user_context["time"]
    class key_type(ct.Structure):
        _fields_  = [\
            ("data", ct.c_char * key_size)
        ]
    class value_type(ct.Structure):
        _fields_  = [\
            ("data", ct.c_char * value_size)
        ]
    for t in range(time):
        map = bpf.get_table("map%d"%t)
        val = value_type()
        ct.memset(ct.byref(val), 0, value_size)
        for i in range(me):
            key = key_type()
            ct.memset(ct.byref(val), 0, key_size)
            pkt = ct.cast(ct.byref(key), ct.POINTER(pkt_5_tuple))
            pkt.src_ip = i 
            map[key] = val
    return ["xdp_main"]
        
hash_lookup_hooks_fn = {
    "pre_prog_load" : hash_pre_prog_load
}

hash_hw_kw = {
    "default_action": "XDP_PASS",
    "debug" : DEBUG,
    "hook_fns": hash_lookup_hooks_fn
}

hash_drv_kw = {
    "default_action": "XDP_DROP",
    "debug" : DEBUG,
    "hook_fns": hash_lookup_hooks_fn
}

class exp_hash_lookup_class:
    name = "hash_lookup"
    format = "%s:%d:%d:%d:%d"
    exp_configuration_base = '''%s configuration:
key_size: %d
value_size: %d
max_entries: %d
lookup_times: %d'''
    exp_prog_base = '''
    
struct key_type {
    char data[KEY_SIZE];
};
struct value_type {
    char data[VALUE_SIZE];
};
//BPF_HASH(map, struct key_type, struct value_type, MAX_ENTRIES);

MAP_DEFINE

int xdp_main(struct xdp_md *ctx) {
    struct key_type key;
    __builtin_memset(&key, 0, sizeof(key));
    struct value_type *val;
    MAP_LOOKUP
    return DEFAULT_ACTION;
}
'''
    
    @classmethod
    def print_config(cls, exp_configs):
        print(cls.exp_configuration_base%exp_configs)
        
    @classmethod
    def printer(cls, exp_full_name):
        cls.print_config(sscanf(cls.format, exp_full_name))
        pass 

    @classmethod
    def exp(cls, times = list(range(1, 11)), max_entries = [1]):
        #test hash lookup times to performance
        #exp configuration 
        
        key_size = ct.sizeof(pkt_5_tuple) # 13 
        value_size = 48   
        exp_name = cls.name
        exp_configs = []
        for t in times:
            for me in max_entries:
                exp_configs.append((exp_name, key_size, value_size, me, t))
        for exp_config in exp_configs:
            exp_full_name = cls.format%exp_config
            me = exp_config[3]
            lookup_time = exp_config[4]
            map_define = '\n'.join(["BPF_HASH(map%d, struct key_type, struct value_type, MAX_ENTRIES);"%i for i in range(lookup_time)])
            map_lookup = '\n'.join(["val = map%d.lookup(&key);"%i for i in range(lookup_time)])
            exp_prog = cls.exp_prog_base\
                .replace("KEY_SIZE", str(exp_config[1]))\
                .replace("VALUE_SIZE", str(exp_config[2]))\
                .replace("MAP_DEFINE", map_define)\
                .replace("MAX_ENTRIES", str(exp_config[3]))\
                .replace("MAP_LOOKUP", map_lookup)
            
            context = {
                "time" : lookup_time,
                "key_size": key_size,
                "value_size":value_size,
                "me": me 
            }
            hash_drv_kw["user_context"] = context
            hash_hw_kw["user_context"] = context
            logging.info("Exp %s:", exp_full_name)
            cls.print_config(exp_config)
            logging.info("Prog under test:")
            print(exp_prog)
            baseline_exp(exp_full_name, exp_prog, DEV_NAME, show_filters= stats_filters, drv_kw=hash_drv_kw, hw_kw=hash_hw_kw)


###################### RANDOM GEN EXP ####################

class exp_random_gen_class:
    name = "gen_random"
    format = "%s:%d"
    exp_configuration_base = '''%s configuration:
times: %d'''
    exp_prog_base = '''
    
int xdp_main(struct xdp_md *ctx) {
    __u32 val;
    //val = bpf_get_prandom_u32();
    GEN_RANDOM
    return DEFAULT_ACTION;
}

'''
    
    @classmethod
    def print_config(cls, exp_configs):
        print(cls.exp_configuration_base%exp_configs)
        
    @classmethod
    def printer(cls, exp_full_name):
        cls.print_config(sscanf(cls.format, exp_full_name))
        pass 

    @classmethod
    def exp(cls, times = list(range(1, 11))):
        #test random generation
        #exp configuration 
        exp_name = cls.name
        exp_configs = [(exp_name, t) for t in times]
        for exp_config in exp_configs:
            exp_full_name = cls.format%exp_config 
            gen_time = exp_config[1]
            gen_random= '\n'.join(["val = bpf_get_prandom_u32();" for i in range(gen_time)])
            exp_prog = cls.exp_prog_base.replace("GEN_RANDOM", gen_random)
            logging.info("Exp %s:", exp_full_name)
            cls.print_config(exp_config)
            logging.info("Prog under test:")
            print(exp_prog)
            baseline_exp(exp_full_name, exp_prog, DEV_NAME, show_filters= stats_filters, skb_kw=skb_kw, drv_kw=drv_kw, hw_kw=hw_kw)

###################### EXP ADJUEST HEAD ####################
class exp_adjust_head_class:
    name = "adjust_head"
    format = "%s:%s:%d"
    exp_configuration_base = '''%s configuration:
mode: %s
size: %d'''
    exp_prog_base = '''
    
int xdp_main(struct xdp_md *ctx) {
    int res;
    res = bpf_xdp_adjust_head(ctx, %d);
    if (res < 0) {
        return XDP_DROP;
    }
    return DEFAULT_ACTION;
}

'''
    
    @classmethod
    def print_config(cls, exp_configs):
        print(cls.exp_configuration_base%exp_configs)
        
    @classmethod
    def printer(cls, exp_full_name):
        cls.print_config(sscanf(cls.format, exp_full_name))
        pass 

    @classmethod   
    def exp(cls, sizes = [-64, -48, -32, -16, -8]):
        #test random generation
        #exp configuration 
        exp_name = cls.name
        exp_configs = []
        for s in sizes:
            if s > 0: 
                exp_configs.append((exp_name, "shrink", abs(s)))
            elif s < 0:
                exp_configs.append((exp_name, "grow", abs(s)))
            else:
                continue
            
        for exp_config in exp_configs:
            exp_full_name = cls.format%exp_config
            if exp_config[1] == 'shrink':
                offset = exp_config[2]
            else:
                offset = -exp_config[2]
            exp_prog = cls.exp_prog_base%offset
            logging.info("Exp %s configuration:", exp_full_name)
            cls.print_config(exp_config)
            logging.info("Prog under test:")
            print(exp_prog)
            baseline_exp(exp_full_name, exp_prog, DEV_NAME, show_filters= stats_filters, skb_kw=skb_kw, drv_kw=drv_kw, hw_kw=hw_kw)
    
 
######################EXP DYNAMIC PTR####################
class exp_adjust_head_class:
    name = "adjust_head"
    format = "%s:%s:%d"
    exp_configuration_base = '''%s configuration:
mode: %s
size: %d'''
    exp_prog_base = '''
    
int xdp_main(struct xdp_md *ctx) {
    int res;
    res = bpf_xdp_adjust_head(ctx, %d);
    if (res < 0) {
        return XDP_DROP;
    }
    return DEFAULT_ACTION;
}

'''
    
    @classmethod
    def print_config(cls, exp_configs):
        print(cls.exp_configuration_base%exp_configs)
        
    @classmethod
    def printer(cls, exp_full_name):
        cls.print_config(sscanf(cls.format, exp_full_name))
        pass 

    @classmethod   
    def exp(cls, sizes = [-64, -48, -32, -16, -8]):
        #test random generation
        #exp configuration 
        exp_name = cls.name
        exp_configs = []
        for s in sizes:
            if s > 0: 
                exp_configs.append((exp_name, "shrink", abs(s)))
            elif s < 0:
                exp_configs.append((exp_name, "grow", abs(s)))
            else:
                continue
            
        for exp_config in exp_configs:
            exp_full_name = cls.format%exp_config
            if exp_config[1] == 'shrink':
                offset = exp_config[2]
            else:
                offset = -exp_config[2]
            exp_prog = cls.exp_prog_base%offset
            logging.info("Exp %s configuration:", exp_full_name)
            cls.print_config(exp_config)
            logging.info("Prog under test:")
            print(exp_prog)
            baseline_exp(exp_full_name, exp_prog, DEV_NAME, show_filters= stats_filters, skb_kw=skb_kw, drv_kw=drv_kw, hw_kw=hw_kw) 
    
    
    
#exps =  [exp_adjust_head_class, exp_random_gen_class, exp_array_lookup_class, exp_hash_lookup_class]

exps = [exp_hash_lookup_class]

if __name__ == '__main__': 
    import sys
    
    coloredlogs.install(level='INFO')
    #logging.basicConfig(level=logging.INFO)
    
    if len(sys.argv) == 1:
        for exp in exps:
            exp.exp()
    else:
        print_baseline_latest(stats_filters,\
           exps)
    
    