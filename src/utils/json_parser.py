"""
JsonParser - Dictionary with attribute access (dot notation).

Combines:
- Dict access: config['key']
- Attribute access: config.key
- A clean __repr__ like a standard Python dict
- Automatic recursive parsing of nested dicts and lists
"""


class JsonParser(dict):
    """
    A dict that supports both dict['key'] and dict.key access.
    Automatically converts nested dicts into JsonParser objects.
    
    Example:
        data = JsonParser({'name': 'Mario', 'metadata': {'doc': 'VDD'}})
        data.name                  # 'Mario'
        data['name']               # 'Mario'
        data.metadata.doc          # 'VDD'  (metadata is JsonParser, not dict)
        print(data)                # {'name': 'Mario', ...}
    """

    def __init__(self, *args, **kwargs): # *args and **kwargs keep this compatible with any input accepted by dict (e.g. dict(a=1, b=2) or dict({'a': 1, 'b': 2}))
        super().__init__() # initialize an empty dict
        data = dict(*args, **kwargs)   # normalize input

        """ version without __setitem__ (recursive parsing without going through __setitem__)
        #data = self._parse(data)       
        #super().__init__(data)         # initialize the base dict with the final data
        """

        #self.update(dict(*args, **kwargs))   # update the dict with the final data (redundant, but guarantees everything is present)
        for k, v in data.items(): # alternative to update, so it always goes through __setitem__ and recursively parses nested dicts too
            self[k] = v  # ensure all data is present as dict keys (redundant, but guarantees completeness)
    
    def __getattr__(self, name):
        """Attribute access: obj.key"""

        try:
            return self[name]
        except KeyError as e:
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'") from e
    
    def __setattr__(self, name, value):
        """Attribute assignment: obj.key = value"""

        if name.startswith("_"):
            object.__setattr__(self, name, value)
        else:
            self[name] = value  # !!!! passa da __setitem__ !!!!
    
    def __delattr__(self, name):
        """Attribute deletion: del obj.key"""

        if name.startswith("_"):
            object.__delattr__(self, name)
            return
        
        try:
            del self[name]
        except KeyError as e:
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'") from e
    

    def __setitem__(self, key, value):
        super().__setitem__(key, self._parse(value)) # route everything through __setitem__ so nested dicts are always converted into JsonParser

    def __str__(self):
        # Provide a clear representation without exposing JsonParser internals.
        printable_dict = {k: v for k, v in self.items()} # convert to a standard dict for a cleaner representation
        return str(printable_dict)

    # deprecated - no longer needed, recursive parsing now happens directly in __setitem__
    """def _parse(self, elem):
        if isinstance(elem, dict):
            parsed = {} 
            
            for k, v in elem.items():
                parsed[k] = self._parse(v)

            # alternative using a comprehension (more compact and without an intermediate dictionary):
            # return JsonParser({k: self._parse(v) for k, v in elem.items()})

            return JsonParser(parsed) # ERROR: this would call the constructor recursively and cause an infinite loop. FIX: use super() to avoid calling the JsonParser constructor again
        
        elif isinstance(elem, list):
            return [self._parse(x) for x in elem]
        
        else:
            return elem"""
        
    # deprecated - no longer needed, recursive parsing now happens directly in __setitem__
    """def _parse(self, elem):
        if isinstance(elem, dict):
            parsed = {} 
            
            for k, v in elem.items():
                parsed[k] = self._parse(v)

            # alternative using a comprehension (more compact and without an intermediate dictionary):
            # return {k: self._parse(v) for k, v in elem.items()}

            return parsed
                
        elif isinstance(elem, list):
            return [self._parse(x) for x in elem]
        
        
        return elem"""
    
    def _parse(self, value):
        """Recursively convert dicts and lists."""

        if isinstance(value, JsonParser): # if this is already a JsonParser, return it as-is and avoid converting it again
            return value
        
        if isinstance(value, dict): # and not isinstance(value, JsonParser):
            return JsonParser(value)
            # alternative if you do not want to call `JsonParser`
            #parsed = JsonParser() # create an empty JsonParser
            #for k, v in value.items():
                #parsed[k] = v # there is no need to call _parse(v) because parsed[k] = v already goes through __setitem__, which recursively parses nested dicts
            #return parsed

        elif isinstance(value, list):
            return [self._parse(x) for x in value]
        
        return value
    
