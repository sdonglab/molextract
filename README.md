# molextract

A rule-based parser for Molcas/OpenMolcas log files to extract and transform any data
found in a log file.

Molextract provides a more modular approach to extracting information from log files and
abstracts out similar control flow seen in many scripts.

Molextract is abstract enough that it really isn't specific to Molcas/OpenMolcas log files.
Any file that has certain start / end markers can use the same infrastructure.

## High Level Overview

## Installation

## Examples

## In Progress Development
There are some improvments I would like to make to the codebase. For starters, its clear that
there is a lot of room for abstraction. I think the following abstraction make sense

`ModuleRule`
- Abstract out the trigger / end
- Abstract out set_iter
- Abstract out feed

`LogRule`
- Abstract out the trigger / end
- Abstract out set_iter
- Abstract out feed

`TRIGGER / END`
These could possibly be used in `Rule` and not need to be passed in via the constructor. The
default values to the constructor could perhaps be these potentially overwridden constants.

`ModuleTimeRule`
Parse out the `Module scf spent 2 hours 29 minutes 57 seconds` stuff

