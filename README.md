# molextract
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.7700454.svg)](https://doi.org/10.5281/zenodo.7700454)
[![PyPI version](https://img.shields.io/pypi/v/molextract.svg)](https://pypi.python.org/pypi/molextract)

A rule-based parser for Molcas/OpenMolcas log files to extract and transform any data
found in a log file.

Molextract provides a more modular approach to extracting information from log files and
abstracts out similar control flow seen in many scripts. The initial motivation to develop
molextract came from wanting to centralize multiple bash scripts that used `grep`, `awk` and `sed`
into one Python API.

Molextract is abstract enough that it really isn't specific to Molcas/OpenMolcas log files.
Any file that has certain start / end markers would be suitable to use the same infrastructure.

## High Level Overview
Some information is easily extracted from OpenMolcas log files. For example the `Total SCF energy`
in the log file is always printed prefixed as `::    Total SCF energy <energy>`. Other information
is prefixed by various different "tags" or markers of this information.

The goal of `molextract` is to create a standard and modular way to extract this information so
as to avoid many scripts that extract different information each in slightly different ways.

Furthermore, `molextract` is designed to simply extract information, so that any application can
modify / change / transform this data in any way fit.

### Rules
The design of `molextract` is meant to mimic that of [Lex](https://en.wikipedia.org/wiki/Lex_(software)), a lexical analyzer. So, `molextract`
is built to allow lexing to be easy for the user, but all the parsing or giving meaning to the
data is all on the user.

A core concept in `Lex` is that of "Rules". A Rule is simply something that associates a regular
expression with some code to execute.

Back to the `SCF` example before, we could make a Rule that matches the RegEx `:: Total SCF energy`.
Once that rule matches that line in the Python code we now have access to the String `"::    Total SCF energy <energy>"`
and then we can do... anything. Most likely we want the energy as a float so we can do something like
`energy = float(line.split()[4])`. In this example we can say this Rule's `start_tag` is the RegEx `:: Total SCF energy`.

Sometimes data in OpenMolcas log files span multiple lines so our `start_tag` may be on line 1, but all our data is on lines 2-10.
So we also need a mechanism to know when a rule no longer applies or an `end_tag`. This is yet another RegEx that once we
match a `start_tag` is constantly checked to see if our Rule is complete.

Let's see this high level overview in some of the code. Ignore the method names for now and focus
on the `START_TAG` and `END_TAG` class variables. This is the `RASSCFOrbSpec` rule found [here](https://github.com/sdonglab/molextract/blob/main/molextract/rules/molcas/rasscf.py#L84).
It's goal is the take the following information
```
++    Orbital specifications:
      -----------------------
 
      Symmetry species                           1
                                                 a
      Frozen orbitals                            0
      Inactive orbitals                         27
      Active orbitals                           10
      RAS1 orbitals                              0
      RAS2 orbitals                             10
      RAS3 orbitals                              0
      Secondary orbitals                       148
      Deleted orbitals                           0
      Number of basis functions                185
--
```
and convert it to the following Python dictionary
```python
{
    "active_orbs": 10,
    "num_basis_funcs": 185
}
```

The code for to that looks like this
```python
class RASSCFOrbSpec(Rule):
    START_TAG = r"\+\+    Orbital specifications:"
    END_TAG = "--"

    def __init__(self):
        super().__init__(self.START_TAG, self.END_TAG)
        self.state = {"active_orbs": None, "num_basis_funcs": None}

    def process_lines(self, start_line):
        # Don't care about next two lines
        self.skip(2)
        for line in self:
            last = line.split()[-1]
            if "Active orbitals" in line:
                self.state["active_orbs"] = int(last)
            elif "Number of basis functions" in line:
                self.state["num_basis_funcs"] = int(last)

    def reset(self):
        tmp = self.state.copy()
        self.state = {"active_orbs": None, "num_basis_funcs": None}
        return tmp
```
First notice how the data itself has very obvious start / end tags. Namely the data starts
with `++    Orbital specifications:` and ends with `--`. These are then precisely our RegExs
we define for our Rule, see the `START_TAG` and `END_TAG` variables.

The `process_lines` method will handle the actual extraction of data. See the [Parse](#parser)
section to understand when and where this method is executed. For now you can assume that
`process_lines` is only called when we are reading a log file and we find a line that matches
`START_TAG`.

Once `process_lines` is called we are given access to the line that matches the `START_TAG` namely
the argument `start_line`. We are now also able to iterate through the rest of the log file until
we see a line that matches the `END_TAG`. This iteration is encapsulated in the python code
`for line in self`, i.e. the for loop will end once we reach a line matching `END_TAG`. Based on
these control flows, within the for loop we know exactly where we are in the log file and are free
to parse as we please. In our case we want some specific number so we write some standard python string
manipulation code.

The `reset` method is a mechanism to allow the re-use of a Rule between multiple files as there
may be some state that needs to be reset. Understanding this mechanism is ancillary to the core
concept of Rules in `molextract`.

This was a simple rule. `molextract` allows us to nest rules so we can build complex rules that
describe an entire module or an entire calculation. See [examples/excited_state.py](https://github.com/sdonglab/molextract/blob/main/examples/excited_state.py)
and try to follow the chain as described below.
```
- LogRule
  > RASSCFModule
    * RASSCFEnergy
    * RASSCFCiCoeff
    * RASSCFOccupation
    * RASSCFOrbSpec
    * RASSCFCIExpansionSpec
  > MCPDFTModule
    * MCPDFTRefEnergy
    * MCPDFTEnergy
  > RASSIModule
    * RASSIDipoleStrengths
```

## Parser
In the [Rules](#rules) section we made some assumptions about when and where `process_lines` is called. The [Parser](https://github.com/sdonglab/molextract/blob/main/molextract/parser.py)
class explicitly defines these mechanism.

In the `Parser` class we have a method `feed`
```python
    def feed(self, data, delim='\n'):
        split = data.split(delim)
        split_iter = iter(split)
        self.rule.set_iter(split_iter)

        for line in split_iter:
            if self.rule.start_tag_matches(line):
                self.rule.process_lines(line)
                return self.rule.reset()
```
We do the following in this method
1. Setup the internal iterator for the rule by splitting the data
2. Iterate through the same iterator and only when we find the line that matches `start_tag`
do we execute `process_lines`
3. Once the rule is finished executing we immediately return with the data as returned in
`reset`

Here we have explicitly defined when and where to call `process_lines`. It is up to the user
to manage when and where to execute this method, but the `Parser` class should suffice for almost
all use cases.

## Installation
### Manual Installation
`molextract` has no external dependencies. You can simply clone this repository and add that location
to your `$PYTHONPATH`

For example if you want to put this in `/home/$USER/python-packages` do the following.

```bash
mkdir -p /home/$USER/python-packages
cd /home/$USER/python-packages
git clone https://github.com/sdonglab/molextract.git
```

Then in your `~/.bashrc` or other runtime configuration file, add the following line
```bash
export PYTHONPATH=$PYTHONPATH:/home/$USER/python-packages/molextract
```


### Local `pip install`
You may also install `molextract` locally via `setuptools`. Clone the repository and run within it
```bash
pip install .
```

### Remote `pip install`
You can install the latest official release on PyPi with 
```
pip install molextract
```

## Examples
See the `examples/` directory. You can run these scripts with the files found in the
`test/test_files` directory.

## Testing
To run the unit tests you will need `pytest` installed in your current python environment. Then
simply run `pytest` within this repository.
