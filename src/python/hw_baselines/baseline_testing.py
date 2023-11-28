from exp_common import *
import coloredlogs

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

def exp_array(times = list(range(1, 11))):
    #test array lookup times to performance
    #exp configuration 
    value_size = 56   
    max_entries = 1
    
    exp_configuration_base = '''
value_size: %d
max_entries: %d
lookup_times: %d
'''
    exp_name_base = "array_%d_%d_%d"   #value_size max_entries lookup_times
    exp_lookup_array_base = '''
struct value_type {
    char data[VALUE_SIZE];
};
BPF_ARRAY(map, struct value_type, MAX_ENTRIES);

int xdp_main(struct xdp_md *ctx) {
    int key = 0;
    struct value_type *val;
    MAP_LOOKUP
    return DEFAULT_ACTION;
}
    '''
    
    exp_configs = [(value_size, max_entries, t) for t in times]
    for exp_config in exp_configs:
        exp_configuration = exp_configuration_base%exp_config 
        exp_name = exp_name_base%exp_config 
        lookup_time = exp_config[2]
        map_lookups = '\n'.join(["val = map.lookup(&key);" for i in range(lookup_time)])
        exp_lookup_array = exp_lookup_array_base.replace("VALUE_SIZE", str(exp_config[0])).replace("MAX_ENTRIES", str(exp_config[1])).replace("MAP_LOOKUP", map_lookups)
        logging.info("Exp %s configuration:", exp_name)
        print(exp_configuration)
        baseline_exp(exp_name, exp_lookup_array, DEV_NAME, show_filters= stats_filters, skb_wk=skb_kw, drv_kw=drv_kw, hw_kw=hw_kw)

def exp_random(times = list(range(1, 11))):
    #test random generation
    #exp configuration 
    
    exp_configuration_base = '''
gen_random_times: %d
'''
    exp_name_base = "gen_random_%d"   #value_size max_entries lookup_times
    exp_lookup_array_base = '''
int xdp_main(struct xdp_md *ctx) {
    __u32 val;
    val = bpf_get_prandom_u32();
    GEN_RANDOM
    return DEFAULT_ACTION;
}
    '''
    
    exp_configs = times
    for exp_config in exp_configs:
        exp_configuration = exp_configuration_base%exp_config 
        exp_name = exp_name_base%exp_config 
        gen_time = exp_config
        gen_random= '\n'.join(["val = bpf_get_prandom_u32();" for i in range(gen_time)])
        exp_gen_random = exp_lookup_array_base.replace("GEN_RANDOM", gen_random)
        logging.info("Exp %s configuration:", exp_name)
        print(exp_configuration)
        baseline_exp(exp_name, exp_gen_random, DEV_NAME, show_filters= stats_filters, skb_wk=skb_kw, drv_kw=drv_kw, hw_kw=hw_kw)

if __name__ == '__main__': 
    coloredlogs.install(level='INFO')
    #logging.basicConfig(level=logging.INFO)
    
    #baseline_exp("lookup_hash_base", exp_lookup_hash_base, DEV_NAME, skb_wk=skb_kw, drv_kw=drv_kw, hw_kw=hw_kw)

    exp_array()
    exp_random()
    