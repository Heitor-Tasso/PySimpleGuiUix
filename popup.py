from PySimpleGUI import PySimpleGUI as sg
from tkinter.font import Font
from tkinter import Toplevel

from PySimpleGuiUix.window import WindowBase
from PySimpleGuiUix.utils import space

class PopupBase(WindowBase):
    # todas variaveis que são usadas em sg.Window
    title = 'Popup'
    non_blocking = False
    theme = None
    size = (None, None)
    resizable = True

    PopupButton = None
    _root_running_mainloop = None
    state = ''

    def __init__(self, **kwargs):
        self._root_running_mainloop = sg.Window._root_running_mainloop
        # garantir que o layout vai estar vazio
        kwargs['layout'] = [[]]

        # faz todas as atribuições necessárias
        set(map(lambda x: setattr(self, x, kwargs[x]), kwargs))
        if not isinstance(self.text_font, tuple):
            raise TypeError(f"the font property must be a tuple not {type(self.text_font)}")
    
        # important to use or else button will close other windows too!
        self.PopupButton = sg.DummyButton if self.non_blocking else sg.Button

        # dispatch event
        self.on_set_varibles()
        self.set_layout()

    def run(self, _call_window=None):
        '''
        Cria o layout e inicializa a janela

        Args:
            `_call_window` (WindowBase, optional):
                deve ser a window que iniciou essa janela, para que a outra janela não "morra".\n
                caso seja a primeira janela, não tem problema.\n
        Exemplo:
            PopupBase.run(self)
        '''
        if _call_window is not None:
            self._call_window = _call_window
        elif isinstance(self._root_running_mainloop, Toplevel):
            # ja existe uma window e não foi passada como argumento
            print(f"[ Warning ]: _call_window from PopupBase.run must be a WindowBase!! not {type(_call_window)}")

        self.create_window()
        self.close()
        return self
    
    def create_window(self):
        super().create_window()
        while self._running:
            if self.non_blocking:
                self.event, self.values = self.window.read(timeout=0)
            else:
                self.event, self.values = self.window.read()
            self.on_events(self.event, self.values)

    def on_events(self, event, values):
        self.state = event
        self.close()


class PopupTextButtonBase(PopupBase):
    text = ' '
    text_color = '#ffffff'
    text_font = ('Arial', 15)
    halign = 'center'
    fnt = None
    max_width_text = 0
    n_btn = 2

    button_text = 'Button'
    button_color = ('#ffffff', '#000000') # text_color, background_color

    title = "Popup Base Text"
    theme = 'LightGray1'
    
    def on_set_varibles(self):
        # necessário para saber a largura do texto maior e centralizar as coisas depois
        self.fnt = Font(family=self.text_font[0], size=self.text_font[1], weight='normal')
        biggest_line = ''
        for line in self.text.splitlines():
            if len(line) > len(biggest_line):
                biggest_line = line
        self.max_width_text = self.fnt.measure(biggest_line) / 8

    def on_layout(self):
        '''
        Cria o layout e inicializa a janela.
        '''
        if self.halign == 'center':
            width_space = lambda message: round((self.max_width_text - 3 - (self.fnt.measure(message) / 8))/2)
        elif self.halign == 'left':
            width_space = lambda message: 0
        elif self.halign == 'right':
            width_space = lambda message: 0
        else:
            raise TypeError(f"incorrect halign option, must be 'center', 'left' or 'right' not {self.halign}")

        for message in self.text.splitlines():
            text = sg.Text(
                text = message, auto_size_text = self.auto_size_text, text_color = self.text_color,
                background_color = self.background_color, font = self.text_font,
            )
            self.layout += [[space(width_space(message), 1), text]]
        
        btn_erro = self.PopupButton(
            self.button_text, button_color = self.button_color,
            focus = True, bind_return_key = True, size = (8, 1)
        )
        self.layout += [[space(round((self.max_width_text + 2)/self.n_btn - 6), 1), btn_erro]]

class PopupError(PopupTextButtonBase):
    text_color = '#ff0000'
    text_font = ('Arial', 25)

    button_text = 'ERRO'
    button_color = ('#ff0000', '#211b15') # text_color, background_color

    title = "Popup Error"

class PopupOk(PopupTextButtonBase):
    text_color = '#000000'
    text_font = ('Arial', 25)

    button_text = 'OK'
    button_color = ('#ffffff', '#0b6321') # text_color, background_color

    title = "Popup OK"

class PopupConfirm(PopupTextButtonBase):
    text_color = '#000000'
    text_font = ('Arial', 25)

    button_text = 'Cancel'
    button_color = ('#ffffff', '#0b6321') # text_color, background_color
    button2_text = 'Confirm'
    button2_color = ('#ffffff', '#0b6321') # text_color, background_color
    n_btn = 2.4
    title = "Popup Confirm"

    def on_layout(self):
        '''
        Cria o layout e inicializa a janela.
        '''
        super(PopupConfirm, self).on_layout()

        btn_confirm = self.PopupButton(
            self.button2_text, button_color = self.button2_color,
            focus = True, bind_return_key = True, size = (8, 1)
        )
        self.layout[-1].append(btn_confirm)

if __name__ == '__main__':
    sg.theme('LightGray1')
    win = WindowBase()
    cmf = PopupConfirm(text=" \nTap confirm to continue.\n"+(' '*70)).run(win)
    print(cmf.state)
    PopupError(text=' \nIncorrect parameters\n'+(' '*70)).run(win)
    PopupOk(text=" \nTou can'y continue\n"+(' '*70), halign='left').run(win)
