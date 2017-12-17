class: center, middle

# Binary Patching for Section Fuzzing #

<i> MS Cyber Security Capstone Project </i>

------------------------

Thomas Fordon

<i>tom.fordon@gmail.com</i>

---

## Who I am ##

Thomas Fordon

* Persuing Master's degree in cybersecurity
* Contractor working with avionics for the Air Force Research Lab.

---

## Outline ##

* Problem 
* Demonstration
* Promblem Discussion
* Background
    * Fuzzing
    * Constraint Solving
* Approach
* Results
* Future Development
* Conclusion

---

# Problem #

Discovering vulnerabilities in avionics embedded systems is hard.

* No source code
* Special hardware
    * Expensive
    * Difficult to emulate

---

## Traditional Approach is lacking ##

* Traditional approach is to fuzz a real system.
    * Throw "random" data at it and check for crashes/hangs
* This does not scale well
* This cannot find meaningful errors.
    * Only crashes and "obviously" bad behavior

---

## Emulating a system is a good, but not enough ##

Pros:

* Scales out well
* Cheaper

Cons:

* Still doesn't find meaningful errors
* Emulation still difficult
* Black Box Fuzzing

---

## What the solution looks like ##

* Emulated environment
    * Avoids difficult custom I/O emulation
* Works with advanced fuzzing tools like evolutionary fuzzing and symbolic constraint solving engines. (Discussed later)
* Fuzzes inputs and system state
    * Allows testing for deep code paths quickly
    * Tests assumptions of the reverse engineer too

---

# Example #

Let's jump in with a quick demo.  Here's what I'll be showing:

* Expose a section of the program under test
* Also expose the process state
* Instrumentaion should be agnostic to the testing methodology
    * Works with fuzzing and constraint solving

---

class: center, middle

<img src="/images/process_overview.png"  height="400">

---

# Demonstration #

* Show c++ code of target
* Reverse engineer target binary in radare2
* Show script to instrument the binary
* Create instrumented binary
* Run program with custom inputs
* Fuzz program with AFL

---

class: center, middle

# Problem Discussion#

---

## What is a vulnerability ##

A bug that can be exploited to achive a security related goal.

* A bug is a variation from the expected behavior.
    * Hopefully there is a formal specification, but this is not usually the case.
    * At the very least, we can say: "the program shouldn't crash"
* Security concerns will vary based on application and system.
* Malware triggers are particularly important to discover.

---

## Finding vulnerabilities ##

* First need to define the specification.
    * pre/post conditions are an obvious format.
    * invariants are also important, but not addressed in this project.
* To find a vulnerability, you need to find a bug.
    * Not all bugs are vulnerabilities
* The bug often is on the edge of the specification
    * Could be poorly tested.
    * The designers assumptions may not be correct.
    * Designer may not consider inputs from an aggresive posture

---

## Finding vulnerabilities 2 ##

* Find "interesting" inputs and do post-fuzzing analysis
    * Inputs that cause crashes
    * Inputs that cause new code paths to be exercised
* Define constraints that have security implications and search for violations
    * e.g. the return pointer should not be overwritten
    * e.g. a specific variable should not change.

---

class: center, middle

# Fuzzing #

'''
... an automated software testing technique that involves providing invalid, unexpected, or random data as inputs to a computer program.
'''

<i>https://en.wikipedia.org/wiki/Fuzzing</i>

---

## Types of Fuzzing ##

* Black Box - no knowlege of program internals.
* White Box - total knowlege of program intenternals.
    * Used for symbolic execution constraint solving
* Grey Box - Coverage/Execution knowledge
    * Used in evolutionary fuzzing 

------------------------------

* Smart/Dumb - Does/Doesn't know about the underlying data structure
* Mutational/Generative - Does the fuzzer modify an existing template, or generate the input whole cloth 
* Evolutionary - Uses genetic algorithms an a set of inputs to search the solution space
* In memory - Modifies a running process

---

## Fuzzing the system state ##

Don't just fuzz the inputs.  Fuzz valid system states.

* Similar to in-memory.
* Should expose deeper, more interesting bugs.
* Find the effect of system states on code paths.
* Requires a better understanding of the underlying system

---

## Section Fuzzing ##

Testing a portion of the total binary.  Useful when:

* Surrounding code makes the entire program difficult to fuzz
    * Network code with limited connection.
    * Custom memory mapped I/O for embedded binaries.
* Process need to be long running to expose the issue
    * Also need to expose state for this.

---

## Section Fuzzing 2 ##

Potentially useful when performing the RE itself.
I have not done a great deal of RE, so this is speculative.
I think it would allow the analyst to:

* Work with smaller sections of the code
* Explicitly write their assumptions in a concrete and testable format
* Iteratively test these assumptions
    * Run a fuzz test using the pre/post conditions.
    * If the test fails, either the assumptions were bad, or a bug exists.


---

## AFL ##


* State of the art
* Works with QEMU
* Evolutionary
* Symbolic constraint solver integration
* Scales out
* This is the target fuzzer my tool uses

---

## AFL - How does it work

<img src="/images/afl_edge_counts.png"  height="500">

---

## AFL code ##

```
location = <compiler_time_random>;
shared_mem[location^prev_location]++;
prev_location = location << 1;
```

---

## Constraint Solving ##

* Solves constraints to execute a specific path (see below)
* Has issues with path explosion
    * concrete symbolic (concolic) execution addresses this by symbolically executing one concrete execution path.
* Works well to discover specific inputs that fuzzing has difficulty with
    * e.g) if (x==0xDEADBEEF)
* Useful for discovering malware triggers.
* Often combined with evolutionary fuzzing to discover new inputs when the fuzzer is "stuck"
    * Driller uses AFL and Unicorn


```
int a, b;
b = a + 10;
if(b > 20){
  // what are the constraints are need to get here?
}
```

---


# Instrumentation #

* Decided to start with ELF32 executables.
    * Many tools for ELF32
* Created new object and injected it into the existing binary
    * Used method layed out by ERESI [@citationNeeded]
* Had issues injecting new symbols/dependencies due to ELF32 constraints
    * symbols like glibc:read and glibc:malloc are required.
    * Not easily resolved.  The code needs to be relocated which requires data flow analysis.
* Future work should assume raw-binary inputs and create instrumented ELF files

---

## Code to Inject ##

<img src="/images/instrumented_segments.png"  height="300">

* New main()
    * Set up the stack frame
    * initialized memory based on our constraints and input file.
* end\_check()
    * checks any end constraints (not implemented)
    * returns 0 if all constraints are valid

---

## Injection Method ##

* Compile the new code to a relocatable object file (ET\_REL ELF32)
* Use elfsh to load target binary and inject the object file
    * Leave most of the extend the code segment and the data segment.
    * Add new sections to the target.
        * text and data sections from the ET\_REL object.
    * Inject new code/data into the extended areas
* Use elfsh to redirect main to new\_main()
* Use radare2 script to overwrite end of section with a jump to end\_check()

---

class: center, middle

## ELF Section Mapping ##

<img src="/images/elf_section_mapping.png"  height="400">

---

class: center, middle

## ELF Injection ##

<img src="/images/elf_injection.png"  height="400">

---

class: center, middle

## New ELF File ##

<img src="/images/instrumented_segments.png"  height="400">

---

# Results #

* Successfully fuzzed several example programs
    * accessed static, stack and heap variables.
* Got hung up on ET\_REL injection
    * Too many issues, and it is not my ultimate target raw binary anyway.
    * Going to build an ET\_EXEC ELF file based on the raw binary plus generated code.
* Could not use Driller due to time.

---

# Future Steps

* Will use shortly with avionics binary for AFRL
* Custom built ELF32 from raw binary target
    * No need to relocate code section to accomodate updated .dynamic section
    * Removes elfsh dependency
* Add pre/post conditions as needed.
    * RPC style generative pre-conditions
* Get Driller to work or use another constraint solver to work with AFL
* Expose variable changes mid-execution to test race conditions.
    * Everything is single threaded, so these conditions cannot be fuzzed as it is instrumented.
    * Instrument the binary to perform memory changes after N instructions, where N is a fuzzable value.
    * Greatly complicates the instrumentation and reduces speed.

---

# Conclusion #

* I presented a tool that enables section fuzzing
* Enabled through binary patching
* Presented tool is agnostic to the tool used for fuzzing or constraint solving 
* Injecting into an ELF executable is problematic

---

# Questions? # 

---

---

# Demo of report and slide creation #

* Report and slides are all represented in markdown
* Markdown is a markup language that is intentionally easy to read
    * I found it easier to work with than LaTeX
* Report does markdown -> LaTeX -> pdf
* Slideshow uses reveal.js to load into a webpage


