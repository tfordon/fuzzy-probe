#!/usr/bin/env python

from fuzzyprobe import Fuzzyprobe

start_address = 0x08048b43
end_address = 0x08048b6c
static_location = 0x0804a0f0
static_size = 10

if __name__ == '__main__':
    fp = Fuzzyprobe('./simple-test', start_address, end_address)
    fp.read_raw(static_location, static_size)
    fp.instrument()
