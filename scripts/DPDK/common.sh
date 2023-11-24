#!/bin/zsh

function make_cpu_map() {
    cpumap=0
    for cpu in "$@"
    do
        if [[ $cpu =~ "^[0-9]+-[0-9]+$" ]]; then 
            #this is a cpu list， =～ （only support in zsh) 
            for subcpu in $(eval "echo {$(echo $cpu | sed 's/-/../g')}")
            do 
                cpuflag=$(( 1 << $subcpu ))
                cpumap=$(( $cpumap | $cpuflag ))
            done 
        elif [[  $cpu =~ "^[0-9]+$" ]]; then 
            cpuflag=$(( 1 << $cpu ))
            cpumap=$(( $cpumap | $cpuflag ))
        else
            echo "invald $cpu"
            exit -1
        fi 
    done 
    echo $(echo "obase = 16 ; ibase = 10 ; $cpumap "|bc)
}