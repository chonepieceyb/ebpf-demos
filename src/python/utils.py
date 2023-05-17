class ArgWrapper:
    def __init__(self, arg_parse_func, *, use_res_args = False):
        self.arg_parse_func = arg_parse_func
        self.use_res_args = use_res_args

    def __call__(self, func):
        def new_func(*args, **kw):
            kw_args = {}
            if "arg_list" in kw:
                if self.use_res_args: 
                    kw_args, res_args = self.arg_parse_func(kw.pop("arg_list"))
                    if res_args == None: 
                        res_args = []
                    kw_args["res_args"] = res_args
                else:
                    kw_args = self.arg_parse_func(kw.pop("arg_list"))
            else:
                kw_args = kw 
            return func(*args, **kw_args)
        return new_func 
    
def _read_cpu_range(path):
    cpus = []
    with open(path, 'r') as f:
        cpus_range_str = f.read()
        for cpu_range in cpus_range_str.split(','):
            rangeop = cpu_range.find('-')
            if rangeop == -1:
                cpus.append(int(cpu_range))
            else:
                start = int(cpu_range[:rangeop])
                end = int(cpu_range[rangeop+1:])
                cpus.extend(range(start, end+1))
    return cpus

def get_online_cpus():
    return _read_cpu_range('/sys/devices/system/cpu/online')

def get_possible_cpus():
    return _read_cpu_range('/sys/devices/system/cpu/possible')

total_cpu = len(get_possible_cpus())

ip_str_to_int = lambda x: sum([256**j*int(i) for j,i in enumerate(x.split('.')[::-1])])