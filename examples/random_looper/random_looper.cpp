#include <cmath>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <unistd.h>

struct Location{
  float latitude;
  float longitude;
  float elevation;
};

void setup();
Location input();
void compute(Location location);
void output();

struct Waypoint{
  char name[10];
  Location location;
};

static Waypoint nextWaypoint;
static float prevLatitude;
static float prevLongitude;

int main(){
  setup();
  while(true){
    Location location = input();
    compute(location);
    output();
  }
  return 0;
}

void setup(){
  strncpy(nextWaypoint.name, "Test", sizeof(nextWaypoint.name)-1);
  nextWaypoint.location.latitude=42.0;
  nextWaypoint.location.longitude=42.0;
  nextWaypoint.location.elevation=0.0;
}


Location input(){
  Location retValue;
  read(0, &retValue.latitude, sizeof(retValue.latitude));
  read(0, &retValue.longitude, sizeof(retValue.longitude));
  read(0, &retValue.elevation, sizeof(retValue.elevation));
  return retValue;
}


void compute(Location location){
  float latDiff = location.latitude - prevLatitude;
  float lonDiff = location.longitude - prevLongitude;


  printf("main_program:\n%p\n%p\n%p\n%p\n%p\ndone\n", nextWaypoint.name, &prevLatitude, &prevLongitude, &location.latitude, &location.longitude);
  if( std::fabs(latDiff) > .1 || std::fabs(lonDiff) > 0.1){
    //exit if we the lat/long are too far off
    exit(1);
  }

  std::cout << "not exiting" << std::endl;
  if( std::fabs(location.latitude-39.7794) < .1 && std::fabs(location.longitude-(-84.0655)) < .1){
    if(strncmp(nextWaypoint.name, "secret", 6)==0){
      location.latitude = 1/0;
    }
  }
  std::cout << "done" << std::endl;
}


void output(){
  printf("in_output");
}



