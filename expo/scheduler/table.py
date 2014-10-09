class table:
    """A table datatype class for Python.

    It accepts rows and column, and return the data object stored in
    that location.  Currently, it is just a list of dictionaries, and
    has code to check that each dictionary has each 'column' defined
    in it, but will (eventually) be replaced with something more useful.
    May eventually support things like slice or range notations.  
    Eventually....
    """

    coltypes=(type([]), type(()), type(""))
    

    def __init__(self, rows=type(None), columns=type(None)):
        """Initalizes a table, add creates the default list of columns in the table, which must have at
        least something in it.  Also the defailt list of rows, which can be empty."""

        if columns == type(None):
          self._col_list=[]
        elif type(columns) == type(""):
          self._col_list=[columns]
        elif type(columns) in table.coltypes:
          self._col_list=columns
        else:
          """Error condition"""

        if rows == type(None):
          self._row_list=[]
        elif type(rows) == type(""):
          self._row_list=[rows]
        elif type(rows) in table.coltypes:
          self._row_list=rows
        else:
          """Error condition"""

        self.row0={}
        self.col0={}

        if type(rows) != type(type):
          for rownum in range(len(rows)):
            exec "self.row"+str(rownum+1)+"={'0': '"+rows[rownum]+"'}"
        if type(columns) != type(type):
          for colnum in range(len(columns)):
            self.col0[columns[colnum]]=str(colnum+1)
        
        if type(rows) != type(type):
          for rownum in range(len(rows)):
            exec "self.row"+str(rownum+1)+"={}"
            self.row0[rows[rownum]]=str(rownum+1)
            if type(columns) != type(type):
              for colnum in range(len(columns)):
                exec "self.row"+str(rownum+1)+"["+str(colnum+1)+"]=type(None)"

    def __call__(self, row, column):
        """Returns object (or value) stores in the table cell located at (row, column).
        Duplicate method that is called by a different batch of things then __getitem__.
        """

        colnum=self.col0[column]
        rownum=self.row0[row]
        exec "tmp=self.row"+str(rownum)+"["+str(colnum)+"]"
        return tmp
 
    def __getitem__(self, location, item=type(None)):
        """Returns object (or value) stores in thetable cell located at (row, column).
        Duplicate method that is called by a different batch of things then __call__.
        """

        row=location[0]
        column=location[1]
        colnum=self.col0[column]
        rownum=self.row0[row]
        exec "tmp=self.row"+str(rownum)+"["+str(colnum)+"]"
        return tmp

    def __setitem__(self, location, item=type(None)):
        """Sets table cell located at location to object or value passed in as item.
        """

        row=location[0]
        column=location[1]
        colnum=self.col0[column]
        rownum=self.row0[row]
        exec "self.row"+str(rownum)+"["+str(colnum)+"]=item"

    def addcol(self, column, item=type(None)):
        """Adds an empty column to the table.  Recurses through list of rows, and add empty
        column entry to the row dictionary.
        """

        if column not in self._col_list:
          self._col_list.append(column)
          self.col0[column]=str(len(self.col0)+1)
          for rownum in range(len(self._row_list)):
            exec "self.row"+str(rownum+1)+"["+str(self.col0[column])+"]=type(None)"
            

    def addrow(self, rowdata, settings=type(None)):
        """Adds a row to the table.  Can take either just the row name and creates an empty row,
        or a dictionary of the values to be set.
        """

        if type(rowdata)==type(""):
          row=rowdata
        elif type(rowdata) in (type([]), type(())):
          row=rowdata[0]
          if type(settings)==type(None):
            settings=rowdata[1]

        if row not in self._row_list:
          self._row_list.append(row)
          self.row0[row]=len(self.row0)
        rownum=int(self.row0[row])+1
        exec "self.row"+str(rownum)+"={}"
        if type(settings)==type({}):
          for colnum in range(len(self._col_list)):
            if self._col_list[colnum] in settings.keys():
              exec "self.row"+str(rownum)+"["+str(colnum+1)+"]=settings[self._col_list[colnum]]"
            else:
              exec "self.row"+str(rownum)+"["+str(colnum+1)+"]=type(None)"
        elif type(settings) in table.coltypes or settings==type(None): 
          for colnum in range(len(self._col_list)):
            exec "self.row"+str(rownum)+"["+str(colnum+1)+"]=type(None)"             

