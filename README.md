# `PyBOF`
## Run Beacon Object files through python

in-memory loading and execution of BOFs

`PyBOF` enables Python3 to load Beacon Object Files via bytes and execute a target BOF function in a Python interpreter

## Basic Usage

### Run a simple BOF with no required arguments
```python
data = open(r'c:\path\to\example.o', 'rb').read()
bof.run(data)
```

### Pass a raw string argument into BOF
```python
data = open(r'c:\path\to\example.o', 'rb').read()
bof.run(data, args=["foo"], raw=True)
# Raw cannot be used with function kwarg
```

### Pass packed/formatted arguments into BOF
```python
data = open(r'c:\path\to\example.o', 'rb').read()
bof.run(data, args=[r"c:\users"], format="w")
```

## Practical example of execution
```python
import bof
from urllib.request import urlopen
data = urlopen("https://github.com/trustedsec/CS-Situational-Awareness-BOF/raw/master/SA/dir/dir.x64.o").read()
bof.run(data, args=[r"c:\users"], format="w")
```

## Args/Kwargs
There are several args that can be used with PyBOF, they are described in more detail below

### data
Mandatory first positional argument which must be a byte object which contains the raw contents of a BOF

### args
Optional keyword arg which is a list of arguments to pass into the target BOF function

### function
Optional keyword arg which is the string formatted name of target function to execute from the supplied BOF, this defaults to `go`

### format
Optional keyword arg is a string, which informs the BOF argument packer of the argument types as they are packed into the buffer. This is similar to the format arg from `struct.pack`. The only valid format options are as follows:\
`i` for integer\
`h` for short\
`s` for string\
`w` for wide

At least one format type must be supplied for each arg in the args list. This keyword arg cannot be used in conjunction with `raw`

### raw
Optional keyword arg which is a boolean that passes args as a space-joined string without packing it instead of attempting to pack formatted args for the BOF function. This keyword arg cannot be used in conjunction with `format`

## Building
Clone this repo

```cmd
git clone https://github.com/rkbennett/pybof.git
```

Build the _bof c extension
```cmd
cd pybof\src
python .\setup.py build
```

Copy the resulting pyd file into the bof directory
```cmd
copy build\lib.win-xxx-cpython-3xx\_bof.cp3xx-win_xxxx.pyd ..\bof\
```

Change directory to parent of bof directory, import and have fun
```cmd
cd ..\
python
>>> import bof
>>> from urllib.request import urlopen
>>> data = urlopen("https://github.com/trustedsec/CS-Situational-Awareness-BOF/raw/master/SA/dir/dir.x64.o").read()
>>> bof.run(data, args=[r"c:\users"], format="w")
```
