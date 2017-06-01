#!/usr/bin/env python

import argparse
import os
import string

parser = argparse.ArgumentParser(description='fuzzy-probe is a tool to enable in memory fuzzing of ELF files') 
parser.add_argument('binary_to_fuzz', type=str, help='the binary to fuzz')
parser.add_argument('section_start', type=int, help='the address of the start of the section to fuzz')
parser.add_argument('section_end', type=int, help='the address of the end of the section to fuzz')
parser.add_argument('mutable_start', type=int, help='the address of the start of memory to fuzz (this will be more complicated later)')
parser.add_argument('mutable_size', type=int, help='the length of the section of memory to fuzz in bytes')
parser.add_argument('--output', type=str, help='output file', default="a.out")

new_main_text = '''
#include <unistd.h>

void *section_start = $section_start;
char *mutable_start = $mutable_start;
size_t mutable_size = $mutable_size;

int new_main(int argc, char **argv){
  //read input file into mutable memory (test)
  read(STDIN_FILENO, mutable_start, mutable_size);
  printf("in_new");


  //gcc specific
  goto *section_start;
  return 0;
}
'''

elfsh_text = '''
load $binary_name
load newMain.o

reladd 1 2
reladd 1 2

redir main new_main
save $new_binary_name

exit
'''

def createNewMain(section_start, mutable_start, mutable_size):
  text = string.Template(new_main_text)
  with open('newMain.c', 'w') as text_file:
    text_file.write(text.substitute(section_start=section_start, mutable_start=mutable_start, mutable_size=mutable_size))

def compileNewMain():
  os.system('gcc -m32 -c -o newMain.o newMain.c')

def injectNewMain(binary_name, new_binary_name):
  text = string.Template(elfsh_text)
  with open('inject.esh', 'w') as text_file:
    text_file.write(text.substitute(binary_name=binary_name, new_binary_name=new_binary_name))
  os.system('elfsh < inject.esh')

def addJumpAtEndOfSection():
  #TODO
  pass

def cleanup():
  #TODO
  pass


def main():
  args = parser.parse_args()
  createNewMain(args.section_start, args.mutable_start, args.mutable_size)
  compileNewMain()
  injectNewMain(args.binary_to_fuzz, args.output)
  addJumpAtEndOfSection()

if __name__ == "__main__":
  main()
