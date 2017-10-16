#include <iostream>
#include <string.h>

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
