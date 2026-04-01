"""
DottedDict - Dictionary con accesso tramite attributi (dot notation).

Combina:
- Accesso dict: config['key']
- Accesso attributo: config.key
- __repr__ bellissimo come dict standard Python
- Parsing ricorsivo automatico di dict e liste annidati
"""


class JsonParser(dict):
    """
    Un dict che supporta accesso sia dict['key'] che dict.key
    Converte automaticamente dict innestati in oggetto JsonParser.
    
    Esempio:
        data = JsonParser({'name': 'Mario', 'metadata': {'doc': 'VDD'}})
        data.name                  # 'Mario' 
        data['name']               # 'Mario' 
        data.metadata.doc          # 'VDD'  (metadata è JsonParser, non dict)
        print(data)                # {'name': 'Mario', ...} 
    """

    def __init__(self, *args, **kwargs): # per essere generici conviene usare *args e **kwargs, così è compatibile con qualsiasi input che dict accetterebbe (es. dict(a=1, b=2) o dict({'a': 1, 'b': 2}))
        super().__init__() # inizializza dict vuoto
        data = dict(*args, **kwargs)   # preparo input

        """ versione senza __setitem__ (parsing ricorsivo senza passare per __setitem__)
        #data = self._parse(data)       
        #super().__init__(data)         # inizializzo il dict base con i dati finali
        """

        #self.update(dict(*args, **kwargs))   # aggiorno il dict con i dati finali (ridondante, ma garantisce che tutti i dati siano presenti)
        for k, v in data.items(): #alternativa ad update, cosi sono sicuro che passa per __setitem__ e quindi fa il parsing ricorsivo anche dei dict innestati
            self[k] = v  # assicuro che tutti i dati siano presenti come chiavi del dict (ridondante, ma garantisce che tutti i dati siano presenti)
    
    def __getattr__(self, name):
        """Accesso tramite attributo: obj.key"""

        try:
            return self[name]
        except KeyError as e:
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'") from e
    
    def __setattr__(self, name, value):
        """Impostazione tramite attributo: obj.key = value"""

        if name.startswith("_"):
            object.__setattr__(self, name, value)
        else:
            self[name] = value  # !!!! passa da __setitem__ !!!!
    
    def __delattr__(self, name):
        """Cancellazione tramite attributo: del obj.key"""

        if name.startswith("_"):
            object.__delattr__(self, name)
            return
        
        try:
            del self[name]
        except KeyError as e:
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'") from e
    

    def __setitem__(self, key, value):
        super().__setitem__(key, self._parse(value)) # passa tutto a __setitem__ che fa il parsing ricorsivo, così è garantito che anche i dict innestati vengano convertiti in DottedDict

    def __str__(self):
        # Rappresentazione per far capire all'utilizatore il contenuto in modo chiaro, senza mostrare i dettagli tecnici di DottedDict
        printable_dict = {k: v for k, v in self.items()} # converto in dict standard per una rappresentazione più pulita
        return str(printable_dict)

    #deprecato - non serve più, ora il parsing ricorsivo viene fatto direttamente in __setitem__
    """def _parse(self, elem):
        if isinstance(elem, dict):
            parsed = {} 
            
            for k, v in elem.items():
                parsed[k] = self._parse(v)

            # alternativa con comprehension (versione più compatta e senza dizionario intermedio):
            # return DottedDict({k: self._parse(v) for k, v in elem.items()})

            return DottedDict(parsed) #ERRORE: CHIAMAREBBE IL COSTRUTTORE RICORSIVAMENTE, CAUSANDO UN LOOP INFINITO. SOLUZIONE: USARE SUPER() PER EVITARE DI RICHIAMARE IL COSTRUTTORE DI DottedDict
        
        elif isinstance(elem, list):
            return [self._parse(x) for x in elem]
        
        else:
            return elem"""
        
    #deprecato - non serve più, ora il parsing ricorsivo viene fatto direttamente in __setitem__
    """def _parse(self, elem):
        if isinstance(elem, dict):
            parsed = {} 
            
            for k, v in elem.items():
                parsed[k] = self._parse(v)

            # alternativa con comprehension (versione più compatta e senza dizionario intermedio):
            # return {k: self._parse(v) for k, v in elem.items()}

            return parsed
                
        elif isinstance(elem, list):
            return [self._parse(x) for x in elem]
        
        
        return elem"""
    
    def _parse(self, value):
        """Converte ricorsivamente dict e liste"""

        if isinstance(value, DottedDict): # se è già un DottedDict, lo ritorna così com'è (evita di riconvertire un DottedDict già creato)
            return value
        
        if isinstance(value, dict): # and not isinstance(value, DottedDict):
            return DottedDict(value)
            #alternativa se non voglio chiamare `DottedDict`
            #parsed = DottedDict() # creo un DottedDict vuoto
            #for k, v in value.items():
                #parsed[k] = v # non c'e' bisogno di fare _parse(v) perché quando assegno parsed[k] = v, passa per __setitem__ che fa già il parsing ricorsivo di tutti i dict innestati
            #return parsed

        elif isinstance(value, list):
            return [self._parse(x) for x in value]
        
        return value
    
