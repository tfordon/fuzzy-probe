#include <array>
#include <iostream>
#include <string>

#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>


static bool checkMessage(char* password){
    if (
        password[0] == 'p' &&
        password[1] == 'a' &&
        password[2] == 's' &&
        password[3] == 's' &&
        password[4] == 'w' &&
        password[5] == 'o' &&
        password[6] == 'r' &&
        password[7] == 'd'
    ){
       return true;
    }

    return false;
}

static void getMessage(char* input){
  std::string notRight("not right");
  notRight.copy(input, 10);
}









char message[10];

int main(int argc, char **argv){

  getMessage(message);
 
  //this is where the injection jumps to 
  bool isMessageBad = checkMessage(message);

  if(isMessageBad){
    //force a fault if the message is good.  Easier to detect with afl 
    int i = 1/0;
  }

  //this is where the injector will exit
  std::cout << isMessageBad << std::endl;

  return 0;
}















/*
int dummy(){
  read(0,0,0);
  printf("hello");
  printf("hello%i", 1);
  exit(0);
  return 0;
}
*/
