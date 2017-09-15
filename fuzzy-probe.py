#!/usr/bin/env python

import argparse
import os
import string

from xml.etree import ElementTree

from preconditionhandler import *

parser = argparse.ArgumentParser(description='fuzzy-probe is a tool to enable in memory fuzzing of ELF files') 
parser.add_argument('binary_to_fuzz', type=str, help='the binary to fuzz')
parser.add_argument('config_file', type=str, help='A config file describing the section to fuzz and the pre/post conditions', default='config.xml')
parser.add_argument('--output', type=str, help='output file', default="a.out")

# TODO: move this to a seperate file
new_main_text = '''
#include <unistd.h>

void *section_start = $section_start;
static void *working_pointer;

typedef struct{
  char someVar[1000];
} big_stack_struct;

void setupAndJump(big_stack_struct bigStruct){
  //we pass a large struct to the stack so we can work with most parameters

  char stack_base_minus13; //allocate a variable, so we can know our stack base.  This is a actually stack_base - 13 due to other values on the stack (ESI, ESX, EDI)

  $pre_conditions

  //gcc specific
  goto *section_start;
  exit(42); //this should never get called
}  


int new_main(int argc, char **argv){
  big_stack_struct bigStackStruct;
  setupAndJump(bigStackStruct);

  return 0;
}

int end_check(){
  $post_conditions
  
  exit(0);
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

radare_text = '''
aa
oo+
s $section_end
wa call `afl~end_check[0]`
'''

def  createNewMain(section_start, pre_conditions, post_conditions):
  text = string.Template(new_main_text)
  with open('newMain.c', 'w') as text_file:
    text_file.write(text.substitute(section_start=section_start, pre_conditions=pre_conditions, post_conditions=post_conditions))

def compileNewMain():
  os.system('gcc -m32 -c -O0 -o newMain.o newMain.c')

def injectNewMain(binary_name, new_binary_name):
  text = string.Template(elfsh_text)
  with open('inject.esh', 'w') as text_file:
    text_file.write(text.substitute(binary_name=binary_name, new_binary_name=new_binary_name))
  os.system('elfsh < inject.esh')

def addJumpAtEndOfSection(section_end):
  text = string.Template(radare_text)
  with open('radare_script', 'w') as text_file:
    text_file.write(text.substitute(section_end=section_end))
  os.system('radare2 -q -i radare_script w a.out')

def cleanup():
  #TODO remove temp files
  pass


def main():
  args = parser.parse_args()
 
  # TODO: nice errors for bad config file
  e = ElementTree.parse(args.config_file)
  section_start = e.find('./section_start').text
  section_end = e.find('./section_end').text

  pre_conditions = get_cpp_preconditions(e.find('./pre_conditions'))

  # post_conditions = createPostConditions(args.config_file)
  post_conditions = ""

  createNewMain(section_start, pre_conditions, post_conditions)
  compileNewMain()
  injectNewMain(args.binary_to_fuzz, args.output)
  addJumpAtEndOfSection(section_end)

if __name__ == "__main__":
  main()
