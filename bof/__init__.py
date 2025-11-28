from struct import pack, calcsize
from ._bof import run as bof_runner


class BeaconPack:
    def __init__(self):
        self.buffer = b''
        self.size = 0

    def getbuffer(self):
        return pack("<L", self.size) + self.buffer

    def addshort(self, short):
        self.buffer += pack("<h", short)
        self.size += 2

    def addint(self, dint):
        self.buffer += pack("<i", dint)
        self.size += 4

    def addstr(self, s):
        if isinstance(s, str):
            s = s.encode("utf-8")
        fmt = "<L{}s".format(len(s) + 1)
        self.buffer += pack(fmt, len(s)+1, s)
        self.size += calcsize(fmt)

    def addWstr(self, s):
        if isinstance(s, str):
            s = s.encode("utf-16_le")
        fmt = "<L{}s".format(len(s) + 2)
        self.buffer += pack(fmt, len(s)+2, s)
        self.size += calcsize(fmt)


def run(data: bytes, function: str="go", format: str=None, args: list=[], raw: bool=False):
    """ Returns Beacon Object File return value
    Args:
        data (bytes): data content of BOF file
        function (str): target BOF function to execute (defaults to "go")
        format (str): A string that defines the packing format of the supplied args (similar to struct.pack, only accepts 'Z' for wide, 'z' for string, 's' for short, 'b' for binary, and 'i' for int)
        args (list): A list of args to pass to the target BOF function
        raw (bool): Instructs bof.run to pass the args as a raw string instead of packing them (cannot be used with format arg) 
    Returns:
        str: The string output of the BOF target function
    """
    if format:
        valid_formats = ["Z","z","i","s","b"]
        # Verify no unexpected format types have been supplied
        if list(set(format).union(valid_formats).symmetric_difference(set(valid_formats))):
            raise ValueError("format contained invalid format types, only 'Z', 'z', 's', 'b', and 'i' are permitted")
    if format and raw:
        raise ValueError("raw cannot be set to True if a format is defined")
    if args and not raw:
        beaconPack = BeaconPack()
        # These must match for proper packing
        if format and len(format) != len(args):
            raise ValueError("format - args length mismatch")
        for index in range(0, len(args)):
            if format:
                # Pack each of the args based on it's corresponding format entry
                if format[index] == "s":
                    beaconPack.addshort(args[index])
                elif format[index] == "i":
                    beaconPack.addint(args[index])
                elif format[index] == "z" or format[index] == "b":
                    beaconPack.addstr(args[index])
                elif format[index] == "Z":
                    beaconPack.addWstr(args[index])
            else:
                # Default types to string and int if format isn't defined
                if isinstance(args[index], str) or isinstance(args[index], bytes) :
                    beaconPack.addstr(args[index])
                elif isinstance(args[index], int):
                    beaconPack.addint(args[index])
        packArgs = beaconPack.getbuffer()
    elif raw:
        # Join args into space delimited string and pass without packing
        packArgs = " ".join(args)
    else:
        # There were no args, so pass None
        packArgs = None
    try:
        return bof_runner(function, data, packArgs).decode()
    except UnicodeDecodeError:
        return bof_runner(function, data, packArgs).decode("cp1252")
