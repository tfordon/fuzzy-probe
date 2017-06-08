# fuzzy-probe
A tool to enable in memory fuzzing of ELF binaries.  Currently in development and not working.

![fuzzy-probe](/images/fuzzy-probe.png?raw=true)

Fuzzy-probe will be a tool to enable in memory fuzzing of a binary.  This will allow a user to specify a section of code that they wish to run as if were in the middle of a running process.  This will be useful for testing software where the source code is not available, and emulation is difficult. As an example, many embedded programs get in a processing loop where information is continously read off a bus and the processed.  With fuzzy probe, the user could jump into the process right after the message was read off the bus and fuzz the messages and the potential states of the process. The user will specify the initial state, mutable memory, and the section to fuzz.  With this, fuzzy probe will create a new program that sets up  the process and jumps to the section under test.  After executing the section, post-conditions can be tested.  There are other similar tools available, but Fuzzy-probe will have more features and be compatible with American Fuzzy Lop (an excellent open-source fuzzing library)


# Getting started

Install the following pre-requisites:

* eresi/elfsh
* python
* radare2

Setup the python environment:

<pre>source env/activate</pre>

# Usage:

fuzzy-probe <binary> <start_instruction_address> <end_instruction_address> <start_memory_to_fuzz_address> <memory_to_fuzz_size>

* start_instruction_address : the instruction on which you want to begin fuzzing
* end_instruction_address : the instruction on which you end fuzzing
* start_memory_to_fuzz_address : the location of the memory block you want to fuzz
* memory_to_fuzz_size : the size of the memory block you want to fuzz

# Goals:

* Add ability to fuzz stack and heap memory
* Multiple memory sections to fuzz
* Support processor memory initialization (non-mutable)
* Object serializiation into memory based on schema
* ELF64 support
* End conditions
