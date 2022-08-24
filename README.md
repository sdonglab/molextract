# molextract
A rule-based parser for Molcas/OpenMolcas log files to extract and transform any data
found in a log file.

Molextract provides a more modular approach to extracting information from log files and
abstracts out similar control flow seen in many scripts.

Molextract is abstract enough that it really isn't specific to Molcas/OpenMolcas log files.
Any file that has certain start / end markers can use the same infrastructure.

## High Level Overview
Some information is easily extracted from OpenMolcas log files. For example the `Total SCF energy`
in the log file is always printed prefixed as `::    Total SCF energy <energy>`. Other information
is prefixed by various different "tags" or markers of this information.

The goal of `molextract` is to create a standard and modular way to extract this information so
as to avoid many scripts that extract different information each in slightly different ways.

Furthermore, `molextract` is designed to simply extract information, so that any application can
modify / change / transform this data in any way fit.

### Rules
The design of `molextract` is meant to mimic that of `Lex`, a lexical analyzer. So, `molextract`
is built to allow lexing to be easy for the user, but all the parsing or giving meaning to the
data is all on the user.

A core concept in `Lex` is that of "Rules". A Rule is simply something that associates a regular
expression with some code to execute.

Back the the `SCF` example before, we could make a Rule that matches the RegEx `:: Total SCF energy`.
Once that rule matches that line in the Python code we now have access to the String `"::    Total SCF energy <energy>"`
and then we can do... anything. Most likely we want the energy as an float so we can do something like
`energy = float(line.split()[4])`. In this example we can say this Rule is `TRIGGERED` by the RegEx `:: Total SCF energy`.

Sometimes data in OpenMolcas log files span multiple lines so our trigger may be on line 1, but all our data is on line 2-10.
So we also need a mechanism to know when a rule no longer applies or an `END` tag. This is yet another RegEx that once we
match a `TRIGGERED` RegEx is constantly checked to see if our Rule is complete.

Let's see this high level overview in some of the code. Ignore the method names for now and focus
on the `TRIGGER` and `END` aspects. This is the `RASSCFOrbSpec` Rule in `rules/rasscf.py`. It's goal is the take the following information
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
and make the following dictionary
```python
{
    "active_orbs": 10,
    "num_basis_funcs": 185
}
```

The code for to that looks like this
```python
class RASSCFOrbSpec(me.Rule):
    TRIGGER = r"\+\+    Orbital specifications:"
    END = r"--"

    def __init__(self):
        super().__init__(self.TRIGGER, self.END)
        self.state = {
            "active_orbs": None,
            "num_basis_funcs": None
        }

    def feed(self, line):
        # Don't care about next two lines
        self.skip(2)
        for line in self:
            last = line.split()[-1]
            if "Active orbitals" in line:
                self.state["active_orbs"] = int(last)
            elif "Number of basis functions" in line:
                self.state["num_basis_funcs"] = int(last)


    def clear(self):
        tmp = self.state.copy()
        self.state.clear()
        return tmp

```
First notice how the data itself has very obvious start / end "tags". Namely the data starts
with `++    Orbital specifications:` and ends with `--`. These are then percisely our RegExs
we define for our Rule, see the `TRIGGER` and `END` variables.

The `feed` method will only execute when a line matches `TRIGGER`. Once we
are executing this code we can iteratre through each line following the `TRIGGER` until we
reach `END`. This is encapsulated in `for line in self`. At this point we know exactly at which
point in the file we are in and we can proceed to do what we want. In our case we want some
specific number so we write some standard python string maniuplation code.

The `clear` method is a mechanism to allow the re-use of Rule between multiple files as there
may be some state that needs to be reset. Understandiing this mechanism is ancillary to the core
conept of Rules in `molextract`.

This was a simple rule. `molextract` allows us to nest rules so we can build complex rules that
describe an entire module or an entire calculation. See `examples/excited_state.py` and try to
follow the chain as described below.
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


## Installation
`molextract` has no external dependencies. Simply clone this repository and add that location
to your `$PYTHONPATH`

For example if you want to put this in `/home/$USER/python-packages` do the following.

```bash
mkdir -p /home/$USER/python-packages
cd /home/$USER/python-packages
git clone https://github.com/sdonglab/molextract.git
```

Then in your `~/.bashrc` or other runtime configuration file, add the following line
```bash
export PYTHONPATH=$PYTHONPATH:/home/$USER/python-packages
```

You are free to put this package anywhere you would like simply just replace `/home/$USER/python-packages`
with any other path you want.

## Examples
See the `examples/` directory

## In Progress Development
- Extracting information from an `END` Tag. See https://github.com/sdonglab/molextract/issues/1
- Right now internally rules can only be based on single lines. I don't anticipate changing this
so there wouldn't be an easy way to make a multi-line trigger, though it could be done with some
overhead logic.

