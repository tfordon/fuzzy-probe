#include <iostream>
#include <string.h>

#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>


int foo(const char *input){
    char local_array[50];
    strcpy(local_array, input);
}

int main(int argc, char **argv){
    char inputBuffer[100];
    std::cin >> inputBuffer;
    foo(inputBuffer);
    return 0;
}










































//Having some trouble injecting.  Need some of these symbols in the target binary
//TODO: refactor to remove dependency
/*
int dummy(){
  read(0,0,0);
  printf("hello");
  printf("hello%i", 1);
  malloc(10);
  exit(0);
  return 0;
}
*/
