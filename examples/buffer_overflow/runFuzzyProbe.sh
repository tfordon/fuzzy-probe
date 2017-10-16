#!/usr/bin/env python

from fuzzyprobe import Fuzzyprobe

start_address = 0x08048691
end_address = 0x080486c6
static_location = "ebp-0x3e"
static_size = 100

if __name__ == '__main__':
    fp = Fuzzyprobe('./simple_overflow', start_address, end_address)
    fp.stack_size = 0x58
    str_loc = fp.dynamically_allocate(100)
    fp.set_fixed_address("ebp-0x3e", str_loc);
    fp.read_raw(str_loc, static_size)
    fp.instrument()
