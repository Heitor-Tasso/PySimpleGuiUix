
from PySimpleGuiUix.popup import PopupError, PopupConfirm
from PySimpleGuiUix.window import WindowBase
from PySimpleGuiUix.table import Table
from PySimpleGuiUix.utils import space
from PySimpleGUI import PySimpleGUI as sg
from random import randint

class Manager(WindowBase):
    theme = 'LightGrey1'
    title = 'Manager DB'
    size = (900, 650)
    return_keyboard_events = True
    use_default_focus = False
    num_id = 0

    def on_layout(self):
        table_columns = [
            {'text' : 'ID', 'width' : 6, 'nmColum' : 'cdUser'},
            {'text' : 'Name', 'width' : 25, 'nmColum' : 'nameUser'},
            {'text' : 'Password', 'width' : 40, 'nmColum' : 'passwordUser'},
            {'text' : 'IP', 'width' : 20, 'nmColum' : 'ip'},
            {'text' : 'Status', 'width' : 10, 'nmColum' : 'statusUser'},
        ]
        # set apparence of cells table
        aparence_cell = {'bg':'white', 'fg':'black', 'align':'center'}
        for colum in table_columns:
            for name, value in aparence_cell.items():
                colum[name] = value
        
        data = [(self.num_id, f'User{self.num_id}', randint(0, 10000), '127.0.8', '1')]
        self.num_id += 1
        data = list(map(lambda x: list(map(str, x)), data))
        self.table = Table(
            ID='table', data=data, headerBG='LightBlue',
            visible_rows=21, visible_cols=5,
            cols_specs=table_columns, on_cell_press=self.on_cell_table_press,
        )

        self.layout = [
            [sg.Text(text='Edit Column  -'), sg.Input(key='input-values'), space(5, 1)],
            [sg.Frame('', self.table.layout())],
            [space(1, 1)],
            [space(35, 2), sg.Button('New User', size=(15, 2)), sg.Button('Cancel', size=(15, 2))],
            [space(1, 1)],
        ]

        # this return will be passed as a parameter in the self.on_window callback
        return False

    def on_window(self, connect_data_base):
        # need initialize table
        self.table.bind_events(self.window)

        # verifica se ele consegui conectar ao banco de dados
        # quando estava criando a janela
        if connect_data_base:
            return None
        PopupError(text=' \n Não foi possivel conectar ao banco de dados! \n ').run(self)

    def on_cell_table_press(self, table, dataRow, dataCol, **kwargs):
        if self.values is None:
            return None
        
        value = self.values['input-values']
        if value != '':
            if table.cols_specs[dataCol]['nmColum'] == 'cdUser':
                PopupError(text=f' \n Não é possivel mudar o ID do usuario \n ').run(self)
                return False
            # resetar valor texto do input e de values
            self.window['input-values'].update('')
            self.values['input-values'] = ''
            # mudar valor do widget tabela
            table.data[dataRow][dataCol] = value
        table.update_cells()

    def on_events(self, event, values):
        # fechar janela
        if event == 'Cancel':
            pop = PopupConfirm(text=" \n Really want continue? \n ").run(self)
            if pop.state == 'Confirm':
                self.close()
        
        elif event == 'New User':
            valueColumn = [self.num_id, f'User{self.num_id}', randint(0, 10000), '127.0.8', '1']
            self.num_id += 1
            self.table.data.append(list(map(str, valueColumn)))
            # atualizar tabela para aparecer o novo usuario
            self.table.setData()
            self.table.update_cells()
        
        # para a tabela receber os eventos e pegar o que for util
        self.table.events(event, values)

if __name__ == '__main__':
    Manager().run()
