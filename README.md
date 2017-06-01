# fuzzy-probe
A tool to enable in memory fuzzing of ELF binaries.  Currently in development and not working.

![fuzzy-probe](/images/fuzzy-probe.png?raw=true)

Sometimes you want to fuzz a small portion of a process.  With this tool you will be able to run a piece of a program in a specific process state and mutate a portion of the memory.  This tool modifies a given binary so it will only run the specified portion.  It will mutate the section of memory based on a file it reads from stdin.  This can be useful for file based fuzzing tools like American Fuzzy Lop.

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
