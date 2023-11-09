catch {config_array_partition -maximum_size 4096}
config_compile -name_max_length 60
set_part $part
create_clock -period $clock_period -name default
#set_clock_uncertainty 30% {get_clocks default}
