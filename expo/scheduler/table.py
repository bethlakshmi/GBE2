class table:
    '''
    A table datatype class for Python.

    It accepts rows and columns, and returns the data object stored in
    that location.  Currently, it is just a list of dictionaries, and
    has code to check that each dictionary has each 'column' defined
    in it, but will (eventually) be replaced with something more useful.
    May eventually support things like slice or range notations.  
    Eventually....
    '''

    itemtypes=(type([]), type(()), type(''))
    

    def __init__(self, rows = None, columns = None):
        '''
    Initalizes a table, and creates the default list of columns in the table, 
    which must have at least something in it.
        '''

        if columns == None:
            self.collist=[]
        elif type(columns) == type(''):
            self.collist=[columns]
        elif type(columns) in self.itemtypes:
            self.collist = []
            for item in columns:
                self.collist.append(item)
        else:
            '''Error condition'''
            
        if rows == None:
            self.rowlist=[]
        elif type(rows) == type(''):
            self.rowlist=[rows]
        elif type(rows) in self.itemtypes:
            self.rowlist=[]
            for item in rows:
                self.rowlist.append(item)
        else:
          '''Error condition'''

        self.table = {}

        for column in columns:
            self.table[column] = {}
            for row in rows:
                self.table[column][row] = None

    def __call__(self, row, column):
        '''
    Returns object (or value) stores in the table cell located at (row, column).
    Duplicate method that is called by a different batch of things then 
    __getitem__.
        '''

        return self.table[column][row]
 
    def __getitem__(self, location, item=type(None)):
        '''
    Returns object (or value) stored in the table cell located at (row, column).
    Duplicate method that is called by a different batch of things then 
    __call__.
        '''

        row=location[0]
        column=location[1]
        return self.table[column][row]

    def __setitem__(self, location, item = None):
        '''
    Sets table cell located at location to object or value passed in as item.
        '''

        row=location[0]
        column=location[1]
        if column in self.collist and row in self.rowlist:
            self.table[column][row] = item
        else:
            '''Error Condition'''

    def addcol(self, column, item = None):
        '''
    Adds an empty column to the table.  Recurses through list of rows, and 
    add empty column entry to the row dictionary.
        '''

        if column not in self.collist:
            self.collist.append(column)
            self.table[column] = {}
            if item == None:
                for row in self.rowlist:
                    self.table[column][row] = None
            if type(item) == type(''):
                for row in self.rowlist:
                    self.table[column][row] = item                    
            elif type(item) == type({}):
                for row in self.rowlist:
                    if row in item.keys():
                        self.table[column][row] = item[row]
                    else:
                        self.table[column][row] = None

            #  This method of adding a column is not recommended, use
            #  a dictionary instead.
            elif type(item) in (type([]), type(())):
                for row in self.rowlist:
                    if len(item) >= 1:
                        self.table[column][row] = item.pop(0)
                    else:
                        self.table[column][row] = None

    def getrow(self, row):
        '''
    Return the specified row as a list. 
        '''

        returnlist = []
        for column in self.collist:
            returnlist.append(self.table[column][row])
        return returnlist

    def delrow(self, row):
        '''
    Deletes the specified row from the table.
        '''

        self.rowlist.remove(row)
        for column in self.collist:
            del self.table[column][row]

    def addrow(self, row, item = None):
        '''
    Adds a row to the table.  Can take either just the row name and creates 
    an empty row, or a dictionary of the values to be set.
        '''

        self.rowlist.append(row)
        for column in self.collist:
            if item == None:
                self.table[column][row] = None
            elif type(item) == type(''):
                self.table[column][row] = item
            elif type(item) == type({}):
                if column in item.keys():
                    self.table[column][row] = item[column]
                else:
                    self.table[column][row] = None

            #  This method of adding a row is not recommended.  Use a
            #  dictionary instead.
            elif type(item) in (type([]), type(())):
                if len(item) >= 1:
                    self.table[column][row] = item[0]
                    item = item[1:]
                else:
                    self.table[column][row] = None

    def getcol(self, col):
        '''
    Return the specified row as a list. 
        '''

        returnlist = []
        for row in self.rowlist:
            returnlist.append(self.table[col][row])
        return returnlist

    def delcol(self, column):
        '''
    Deletes the specified row from the table.
        '''

        self.collist.remove(column)
        del self.table[column]

    def listreturn(self, bias = 'row'):
        '''
        Return table as a list of rows or columns, each row or column being a list of cells. 
        bias parameter selects whether to return row or column. (options are ('row', 'column'))
        '''

        returnlist = []
        if bias == 'column':
            innerlist = self.rowlist
            outerlist = self.collist
        elif bias == 'row':
            innerlist = self.collist
            outerlist = self.rowlist
        for outer in outerlist:
            tmplist = []
            for inner in innerlist:
                if bias == 'row': column, row = outer, inner
                elif bias == 'column': column, row = inner, outer
                tmplist.append(self.table[column][row])
            returnlist.append(tmplist)
        return returnlist
