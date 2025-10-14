class translate_dict(dict):
    """
    A dict that returns the key used if no translation was provided for it.
    """
    def __missing__(self,key):
        return key
    

def read_lines(path):
    """
    Read strings from file at `path` (str or Path) and 
    put each line into an element of a list.
    """
    with open(path, 'r') as file:
        lines = [line.rstrip() for line in file]
    return lines