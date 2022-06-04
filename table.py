
from PySimpleGUI import PySimpleGUI as sg
from functools import partial

class Table(object):
    # Not including column header - maybe set automatically if not supplied
    visible_rows = 0
    num_rows = 0
    # maybe set automatically if not supplied
    visible_cols = 0
    num_cols = 0

    # name, widths, colors, justification
    cols_specs = list()
    n_cols = 0
    # specify the config of table data
    data = list()
    # Columns that do not scroll horizontally
    leftColLock = 0
    # color of header table
    headerBG = 'green'
    # padding of columns
    gap = 2
    
    # Changed when data analyzed (setData())
    scroll_x = True
    minimum_scroll_x = 0
    key_scroll_x = ''
    # Modified when scrolling
    topDataRow = 0

    # Changed when data analyzed (setData())
    scroll_y = True
    minimum_scroll_y = 0
    key_scroll_y = ''
    # Adjusted when scroling horizontally
    leftDataCol = 0
    
    # Set in initialize()
    window = None
    Wcolumn = None

    # function that can be replaced
    drawCell = lambda self, table, element, dataRow, dataColumn: element.update(table.data[dataRow][dataColumn])

    # events
    on_cell_press = lambda self, table, dataRow, dataColumn: None
    on_scroll_y = lambda self, table, value: None
    on_scroll_x = lambda self, table, value: None

    def __init__(self, ID, **kwargs):
        """
        Args:
            `ID` (str): the table id, must be unique.
            `visible_rows` (int): number of rows that will be visible.
            `visible_cols` (int): number of cols that will be visible.
            `cols_specs` (list[dict]): list representing the table header, contains column specifications.
            `data` (list[list]): table data, all column values.
        """

        self.ID = ID
        # clear the varibles
        self.cols_specs = list(dict())
        self.data = list()

        # faz todas as atribuições necessárias
        set(map(lambda x: setattr(self, x, kwargs[x]), kwargs))
        
        # Set table rows and columns (visible) if not specified, from the data rows and the number of columns
        if self.visible_rows == 0:
            self.visible_rows = len(self.data)
        if self.visible_cols == 0:
            self.visible_cols = len(self.cols_specs)
        
        self.setData()

    def setData(self, data=None):
        '''
        Install data matrix and associated variables.
        So it can be used after the object is instantiated.

        Args:
            `data` (list, optional): set the rows and cols of table,
            if None don't replace data, only update other varibles.
        '''

        if data is not None:
            self.data = data

        self.num_rows = len(self.data)
        # In case of sparse data, find the longest row
        self.num_cols = len(self.cols_specs)# 0 if not self.data else max(map(lambda row: len(row), self.data))
        self.topDataRow = 0
        self.leftDataCol = 0

        # Disable scroll if needed
        # if self.num_rows <= self.visible_rows:
        #     self.scroll_y = False
        # if self.num_cols <= self.visible_cols:
        #     self.scroll_x = False
        
        self.minimum_scroll_y = (self.num_rows - self.visible_rows + 1)
        self.minimum_scroll_x = (self.num_cols - self.visible_cols)

        if self.Wcolumn is not None:
            self.window[self.key_scroll_y].update(range=(self.minimum_scroll_y, 0))
            self.window[self.key_scroll_y].update(value=self.minimum_scroll_y)

            self.window[self.key_scroll_x].update(range=(0, self.minimum_scroll_x))
            self.window[self.key_scroll_x].update(value=0)

            self.window.refresh()

    def layout(self):
        """
        Below we provide the vertical range, but we might not know this when layout created
        Without the data we do not know how many columns of data there is

        Returns:
            list: layout that can be used in your window.
        """ 

        layout = [[]]

        if self.scroll_y:
            # Calculate vertical height for scroll bar - initial value set, cannot be changed when horizontally scrolling
            height_slider = (self.visible_rows*1.15)
            self.key_scroll_y = f'{self.ID}_scroll_y'
            slider_y = sg.Slider(
                key = self.key_scroll_y,
                range = (0, self.minimum_scroll_y),
                resolution = 1, pad = (0, 0), enable_events = True,
                visible = True, disable_number_display = True,
                size = (height_slider, 24), orientation = 'v',
            )
            layout[0].append(slider_y)
        if self.scroll_x:
            # Calculate horizontal width for scroll bar - initial value set, cannot be changed when horizontally scrolling
            cols = self.cols_specs[:self.visible_cols]
            width_slider = sum(map(lambda col: col.get('width') or 0, cols)) * 0.950
            self.key_scroll_x = f'{self.ID}_scroll_x'
            slider_x = sg.Slider(
                key = self.key_scroll_x,
                range = (0, self.minimum_scroll_x),
                resolution = 1, pad = (0, 0), enable_events = True,
                visible = True, disable_number_display = True,
                size = (width_slider, 25), orientation = 'h',
            )
            layout.append([slider_x])
        
        self.Wcolumn = sg.Column(self.cellLayout(), background_color='black', pad=(0, 0), key='Table')
        layout[0].append(self.Wcolumn)
        
        return layout

    def cellLayout(self):
        """
        Generate table cell and header 

        Returns:
            list: layout to sg.Colunm widget
        """

        rows = list()
        cols = list()

        # create table header
        for i in range(min(self.visible_cols,  self.num_cols)):
            specs = self.cols_specs[i]
            text = sg.Text(
                text = specs['text'], key = f'{self.ID}_cell_{i}',
                size = (specs['width'], 1), pad = (self.gap, 1),
                justification = specs.get('align', 'left'),
                background_color = self.headerBG
            )
            cols.append(text)
        rows.append(cols)
        
        # create table cells
        for row in range(self.visible_rows):
            cols = list()
            for col in range(min(self.visible_cols,  self.num_cols)):
                spec = self.cols_specs[col]
                text = sg.Text(
                    text = ' ', pad = (self.gap, 1),
                    key = f'{self.ID}({row}, {col})',
                    size = (spec['width'], 1),
                    justification = spec.get('align', 'left'),
                    text_color = spec['fg'], background_color = spec['bg'],
                )
                cols.append(text)
            rows.append(cols)
        
        return rows

    def update_cells(self):
        '''
        updade values and sizes of table
        '''
        if not self.data:
            return None
        # Get columns that need to be displayed
        visible_cols = self.displayColumns()
        # Text box column
        count = 0

        # update table header
        for col in visible_cols:
            spec = self.cols_specs[col]
            element = self.window[f'{self.ID}_cell_{count}']

            element.update(spec['text'])
            element.set_size((spec['width'], 1))
            count += 1
        
        # update table cells
        for row in range(self.visible_rows):
            # The text box column
            colCount = 0
            for dataColumn in visible_cols:
                element = self.window[f'{self.ID}({row}, {colCount})']
                element.set_size((self.cols_specs[dataColumn]['width'], 1))
                
                dataRow = (row + self.topDataRow)
                if dataRow < self.num_rows and dataRow > -1:
                    if dataColumn < len(self.data[dataRow]):
                        # Draw data
                        self.drawCell(self, element, dataRow, dataColumn)
                    else: # Blank cell
                        element.update(' ')
                else: # Blank row
                    element.update(' ')
                colCount += 1
        self.window.refresh()

    def displayColumns(self):
        '''
        Returns:
            list: index of visible columns
        '''
        left = (self.leftColLock + self.leftDataCol)  
        right = (self.visible_cols + self.leftDataCol)
        
        indices = list(range(self.num_cols))
        return tuple(indices[:self.leftColLock] + indices[left:right])

    def y_scroll(self, event):
        '''
        Callback of events to update scroll_y
        '''
        if not self.scroll_y:
            return None
        
        # Using scroll bar
        if isinstance(event, float):
            self.topDataRow = self.minimum_scroll_y - int(event)
        else: # Using mouse wheel
            delta = round(event.delta/120)
            self.topDataRow = min(max(0, self.topDataRow-delta), self.minimum_scroll_y)
        if self.topDataRow < 0:
            self.topDataRow = 0
        
        self.update_cells()
        value = (self.minimum_scroll_y - self.topDataRow)
        self.window[self.key_scroll_y].update(value=value)
        self.window.refresh()

        self.on_scroll_y(self, self.topDataRow)

    def x_scroll(self, event):
        '''
        Callback of events to update scroll_x
        '''
        if not self.scroll_x:
            return None
        
        # Using scroll bar
        if isinstance(event, float):
            self.leftDataCol = int(event)
        else:
            delta = round(event.delta/120)
            self.leftDataCol = min(max(0, self.leftDataCol-delta), self.minimum_scroll_x)
        
        self.update_cells()
        self.window[self.key_scroll_x].update(value=self.leftDataCol)
        self.window.refresh()

        self.on_scroll_x(self, self.leftDataCol)

    def events(self, event, values):
        if event == self.key_scroll_y:
            self.y_scroll(values[self.key_scroll_y])
        
        elif event == self.key_scroll_x:
            self.x_scroll(values[self.key_scroll_x])

    def clicked(self, row, col, *args):
        """
        used to dispatch on_cell_press, indicates which cell was pressed.

        Args:
            `row` (int): row of cellula
            `col` (int): col of cellula
        """
        if not self.data:
            return None
        # Row and column are the textbox row and column, not the data
        dataRow = self.topDataRow + row
        if dataRow >= self.num_rows:
            return None

        dataColumn = self.displayColumns()[col]
        if dataColumn >= len(self.data[dataRow]):
            return None
        
        # This appears in main window loop as an event
        self.on_cell_press(self, dataRow, dataColumn)

    def bind_events(self, window):
        """
        Complete the linking of events to mousewheel, scroll bars

        Args:
            window (sg.Window): window containing the table
        """
        for row in range(self.visible_rows):
            for col in range(min(self.visible_cols,  self.num_cols)):
                text_key = f'{self.ID}({row}, {col})'
                element = window[text_key]
                
                element.Widget.configure(takefocus=0)
                element.Widget.bind('<MouseWheel>', self.y_scroll)
                element.Widget.bind('<Shift-MouseWheel>', self.x_scroll)
                element.Widget.bind('<Button-1>', partial(self.clicked, row, col))
        
        # 0 is at the bottom of the slider!
        if self.scroll_y:
            window[self.key_scroll_y].update(value = self.minimum_scroll_y)
        
        # 0 is at the bottom of the slider!
        if self.scroll_x:    
            window[self.key_scroll_x].update(value = 0)
        
        self.window = window
        self.update_cells()
        window.refresh()

if __name__ == '__main__':
    """
    Try to set the table in a class
    Need to handle fixed columns on left
    """
    sg.theme('Darkgrey')
    
    columns = (
        {'text':'ID', 'width': 6, 'bg':'blue', 'fg':'white'},
        {'text':'Name', 'width': 20, 'bg':'blue', 'fg':'white'},
        {'text':'nickname', 'width': 10, 'bg':'blue', 'fg':'white', 'align':'center'},
        {'text':'Level', 'width': 5, 'bg':'blue', 'fg':'white', 'align':'center'},
        {'text':'Priority', 'width': 5, 'bg':'blue', 'fg':'white', 'align':'center'},
        {'text':'No Files', 'width': 6, 'bg':'blue', 'fg':'white', 'align':'center'},
        {'text':'Pages', 'width': 5, 'bg':'blue', 'fg':'white', 'align':'center'},
        *({'text':f'Col {x}', 'width': 15, 'bg':'blue', 'fg':'white', 'align':'center'} for x in range(1, 8)),
    )

    def on_cell_press(table, dataRow, dataCol, **kwargs):
        if dataRow != None and dataCol != None:
            if table.data[dataRow][dataCol] == 'ONE':
                c = 'TWO'
            else:
                c = 'ONE'
            table.data[dataRow][dataCol] = c
            table.update_cells()

    table = Table(
        ID='table1', visible_rows=10, visible_cols=10, cols_specs=columns,
        data=[[f'({row}, {col})' for col in range(len(columns))] for row in range(12)],
        leftColLock=0, on_cell_press=on_cell_press
    )

    layout = [[sg.Text(text='Sample Text')], [sg.Frame('', table.layout())], [sg.Button('Add'), sg.Button('Exit')]]
    window = sg.Window(
        title='Simulate Table 3', layout=layout, use_default_focus=False,
        return_keyboard_events=True, finalize=True,
    )
    # need initialize table
    table.bind_events(window)

    while True:
        event, values = window.read()
        if event in {sg.WINDOW_CLOSED, 'Exit'}:
            window.close()
            break

        elif event == 'Add':
            print('Update')
            table.data.insert(0, list(map(str, range(1, 15))))
            table.setData()
            table.update_cells()
        table.events(event, values)
