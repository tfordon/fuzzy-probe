#!/usr/bin/env python
import struct
import sys

if __name__ == '__main__':
  input_vals = raw_input()
  float_vals = map(float,input_vals.split(','))
  sys.stdout.write(struct.pack('f'*len(float_vals), *float_vals))



