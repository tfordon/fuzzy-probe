Fuzzy-Probe
=======================================

What is it?
---------------

![fuzzy-probe](/images/fuzzy-probe.png?raw=true)

Fuzzy Probe modifies an existing binary so you can test a portion of it.
Fuzzy probe allows you to test assumption you have made while reverse engineering a program.
You do this by providing a list of pre-conditions and post-conditions to the piece of code that you are exercising.
How these conditions are arrived upon are not important for the moment, but these conditions are what you are testing.
In addition to the stated conditions, we will also be testing for crashes and hangs.

Why is it useful?
--------------------

Fuzzy probe allows us to test binaries in finer detail.
This is particularly useful for reverse engineering.
In the process of reverse engineering, analysts attempt to determine the design of a given binary as well as potential attacks.
During this process, they determine what assumptions are being made at a certain part of the program as well as what is actually possible.
As an example, consider the design assumption that an input will be no longer than 100 bytes while the reverse engineer knows they can pass input longer than 100 bytes.  This leads to undefined behavior (like buffer overflows) that can be interesting from security persepective.

Using fuzzy probe, you can test these assumptions at an extremely small scale in order to develop better mental models.
I expect that this will be an iterative process.  An analyst will describe the constraints on a piece of code and test them.
If there is a violation of those constraints, they will reexamine the code and their mental models of the constraints.  If there
was a problem with the code (it was out of spec), this will be noted as a bug and potential vulnerability.
If there is a problem with the percieved constraints, the analyst can update the constraints and try again.

The eventual goal is for fuzzy probe to also have mocking functions that will allow the test to shunt difficult to emulate portions of the test.
This can be done in a manner similar to function mocking for unit tests.  When performing a unit test, some functions are difficult to
test since you don't have access to the entire system (e.g. database calls).  These functions are replaced with mock functions for the duration of a unit test.  Are usually simplified versions with fixed results.

# Getting started

Install the following pre-requisites:

* eresi/elfsh
* python
* radare2

Setup the python environment:

<pre>source env/activate</pre>

How does it work?
---------------------

Fuzzy probe starts with the assumed pre-condition that all memory is set to zero before executing a section of code.  In order for values to be anything else, we must specify what data is being modified and what conditions there are on it.  By basing the conditions on the values in memory we can effectively fuzz the state of a process when a given section of code is executed (ignoring call stack state).

Once we have specified the constraints on memory, we modify the binary to create a new program.  This program will perform the following steps:

1. Initialize any constant memory
2. Set mutable memory by reading from stdin
3. jump to the section under test
4. run to the end of the section under test
5. jump to a end_check function that verifies any post-conditions

By instrumenting the binary in this way, we can instrument our binary for fuzzing in a way that is not specific to any particular fuzzing engine.


ELF details
--------------------

Fuzzy probe is an ELF only tool.  When instrumenting the binary, the goal is to modify as little as possible to avoid interfering with the test.  Fuzzy probe uses elfsh to perform the actual code injection; This section describes what is injected and how eflsh achieves this.

First, we create a new object file that will contain our new_main function and an end_check function.  The new_main function will initialize memory and jump to the section under test.  To create this object file, fuzzy-probe reads a config file and produces a new c++ source file.  This is compiled to a shared object file.

TODO: describe phrack etrel method.


How about an example?
----------------------

Here is a simple example program that we will attempt to fuzz a portion of:

<pre>

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
</pre>

The input/output for this piece of code are not important, but lets pretend they are difficult to emulate functions.  Perhaps they read from a proprietery I/O, or are so slow that testing is impractical, or maybe we are just not interested in them at the moment.

Regardless, we have decided that the Compute portion of the for loop is the interesting section.  Normally, we would attempt to determine the assumptions that the code makes through reverse engineering; since we have the source code, we can easily see what the assumptions are going in.

Normally, this would be an exercise of reverse engineering, but since we have the source code this is a little easier.
For our example, we can see that several variables are expected to be set:

* prevLatitude - static float
* prevLongitude - static float
* secret - static char[]
* latitude - local variable float
* longitude - local variable float


We will specifiy the locations and sizes of these variables by creating a config file.
We can determine the locations of these variables with a tool like IDA or radare2.
Here are some screenshots of the relevant variables.  I did not strip the binaries to allow for easier debugging

![radare_analysis_1](/images/radare_analysis_1.png?raw=true)
![radare_analysis_2](/images/radare_analysis_2.png?raw=true)
![radare_analysis_3](/images/radare_analysis_3.png?raw=true)

Using the locations determined from radare we can construct a configuration file that describes our pre-conditions.

![fuzzy_config](/images/fuzzy_config.png?raw=true)

In the config file we specify all the portions of memory that we would like to have fixed and what can mutate between iterations.  What values will go into the mutable sections is determined at runtime by reading from stdin.  This allows the program to be fuzzed by standard fuzzing tools.

We call fuzzy-probe with the binary and a config file.  This produces an instrumented binary and a default input file.  This is just a small file filled with zeros, but it will be the seed file for AFL (or similar fuzzers).

<pre>./fuzzy-probe.py examples/random_looper/random_looper examples/random_looper/config.xml</pre>

Now we call AFL against our instrumented binary and seed input file.

![afl_no_crash](/images/afl_no_crash.png?raw=true)

As you can see, AFL was able to exercise most of the potential code paths, but was not able to find our secret key.  To find this, a tool like Driller is more appropriate.  To call Driller, we can use the same instrumented binary and seed input.

TODO: information on calling with Driller
