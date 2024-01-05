# sqlite-fuzzer

This repository is my solution to the first project in the Security
Testing course at Saarland University, W23. See `sheet.pdf` for
instructions, including the problem statement and how to run.

The assessment is carried out on the basis of 100,000 inputs fuzzed
by the fuzzer implemented here, or the inputs produced in 30 minutes
of running time, whichever occurs first.

I have tested this on an AWS EC2 t2.large instance, running the code
inside a Docker container. This container was built using the
`Dockerfile` included in this repository, and following the
instructions in `sheet.pdf`. On average, I was able to generate only
~50,000 inputs in 30 minutes, which led to a coverage of ~38% of
sqlite3.c.