Random Looper
===============

A simple program to test the fuzzing tool.

This program reads an input to get: lat, long, and secretCode.  To make things easier, I will read from stdin.

If the lat/long are too far off from the previous value, the program exits with a non-zero code.

If the lat/long are "near" Wright State, our program will print something to stdout.
If the lat/long are "near" Wright State and we get a secretCode='password', our program will crash.
