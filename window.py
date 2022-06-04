from PySimpleGUI import PySimpleGUI as sg
from tkinter import Toplevel

class WindowBase(object):
    _call_window = None
    _running = True
    theme = 'LightGray1'
    back_theme = ('#f2f2f2', '#f2f2f2')

    window, event, values = (None, None, None)

    # Window properties
    title = 'Window Base'
    layout = [[]]
    default_element_size = None
    default_button_element_size = (None, None)
    auto_size_text = True
    auto_size_buttons = None
    location = (None, None)
    relative_location = (None, None)
    size = (None, None)
    element_padding = None
    margins = (None, None)
    button_color = None
    font = None
    progress_bar_color = (None, None)
    background_color = None
    border_depth = None
    auto_close = False
    auto_close_duration = None
    icon = None
    force_toplevel = False
    alpha_channel = 1
    return_keyboard_events = False
    use_default_focus = False
    text_justification = None
    no_titlebar = False
    grab_anywhere = False
    grab_anywhere_using_control = True
    keep_on_top = None
    resizable = False
    disable_close = False
    disable_minimize = False
    right_click_menu = None
    transparent_color = None
    debugger_enabled = True
    right_click_menu_background_color = None
    right_click_menu_text_color = None
    right_click_menu_disabled_text_color = None
    right_click_menu_selected_colors = (None, None)
    right_click_menu_font = None
    right_click_menu_tearoff = False
    finalize = True
    element_justification = 'left'
    ttk_theme = None
    use_ttk_buttons = None
    modal = True
    enable_close_attempted_event = False
    titlebar_background_color = None
    titlebar_text_color = None
    titlebar_font = None
    titlebar_icon = None
    use_custom_titlebar = None
    scaling = None
    metadata = None

    _root_running_mainloop = None

    def __init__(self, **kwargs):
        self._root_running_mainloop = sg.Window._root_running_mainloop
        # garantir que o layout vai estar vazio
        kwargs['layout'] = [[]]
        # faz todas as atribuições necessárias
        set(map(lambda x: setattr(self, x, kwargs[x]), kwargs))

        logs = self.set_layout()
        self.create_window()
        self.on_window(logs)

    def on_window(self, *args):
        """
        Args:
            `args` (anything): the return of self.on_layout
        """ 
        pass

    def set_layout(self):
        if isinstance(self.theme, str):
            sg.theme(self.theme)
            self.back_theme = (sg.theme_background_color(), sg.theme_background_color())
        
        return self.on_layout()
    
    def on_layout(self):
        self.layout = [
            [sg.Text(text='Default Window')],
            [sg.Button('Break', size=(15, 1))],
        ]
        # this return will be passed as a parameter in the self.on_window callback
        return (None)

    def create_window(self):
        """
        Cria o layout e inicializa a janela

        Args:
            `_call_window` (WindowBase, optional):
                deve ser a window que iniciou essa janela, para que a outra janela não "morra".\n
                caso seja a primeira janela, não tem problema.\n
        Exemplo:
            WindowBase.run(self)
        """
        if self.window is not None:
            print(f"[ Warning ]: There is already a window!!")
            self.window.close()
        
        window_settings = {
            'title', 'layout', 'default_element_size', 'default_button_element_size', 'auto_size_text',
            'auto_size_buttons', 'location', 'relative_location', 'size', 'element_padding', 'margins',
            'button_color', 'font', 'progress_bar_color', 'background_color', 'border_depth', 'auto_close',
            'auto_close_duration', 'icon', 'force_toplevel', 'alpha_channel', 'return_keyboard_events',
            'use_default_focus', 'text_justification', 'no_titlebar', 'grab_anywhere', 'grab_anywhere_using_control',
            'keep_on_top', 'resizable', 'disable_close', 'disable_minimize', 'right_click_menu', 'transparent_color',
            'debugger_enabled', 'right_click_menu_background_color', 'right_click_menu_text_color',
            'right_click_menu_disabled_text_color', 'right_click_menu_selected_colors', 'right_click_menu_font',
            'right_click_menu_tearoff', 'finalize', 'element_justification', 'ttk_theme', 'use_ttk_buttons',
            'modal', 'enable_close_attempted_event', 'titlebar_background_color', 'titlebar_text_color',
            'titlebar_font', 'titlebar_icon', 'use_custom_titlebar', 'scaling', 'metadata',
        }
        arguments = dict(map(lambda name: (name, getattr(self, name)), window_settings))
        self.window = sg.Window(**arguments)

    def run(self, _call_window=None):
        if _call_window == True:
            pass
        elif _call_window is not None:
            self._call_window = _call_window
        elif isinstance(self._root_running_mainloop, Toplevel):
            print(f"[ Warning ]: _call_window from WindowBase.run must be a WindowBase!! not {type(_call_window)}")

        while self._running:
            self.event, self.values = self.window.read()
            if self.event == sg.WIN_CLOSED:
                # Close the window end break mainloop
                self.close()
            self.on_events(self.event, self.values)
        self.close()

    def on_events(self, event, values):
        pass

    def close(self):
        if self.window is None:
            return None
        
        self.on_close()
        self.window.close()
        self.window = None
        self._running = False
        
        if self._call_window is not None:
            try:
                win = self._call_window.window
            except Exception:
                win = self._call_window
            win.read(10)
            # win.NonBlocking = False
            # win.CurrentlyRunningMainloop = True
            # sg.Window._window_running_mainloop = win
            
            # win._ReadNonBlocking()
            # sg.Window._root_running_mainloop.mainloop()

    def on_close(self):
        pass

if __name__ == '__main__':
    class TestWindow(WindowBase):
        size = [200, 250]
        title = 'Screen Login'
        theme = 'LightBlue'

        def __init__(self, **kwargs):
            # before create layout and window
            super().__init__(**kwargs)
            # after create layout and window

        # will be called automatically when initialize the window
        def on_layout(self):
            self.layout = [
                [sg.Text('Login', font=('Arial', 46))],
                [sg.Text('Senha', font=('Courier', 20), size=(7, 1))],
                [sg.Text(' ')],
                [sg.Button('Connect', size=(15, 2))],
                [sg.Button('Cancel', size=(15, 2))],
            ]

        # will be called automatically when have events
        def on_events(self, event, values):
            if event == 'Cancel':
                # Close the window end break mainloop
                self.close()
            elif event == 'Connect':
                print('Wellcome!!')

    TestWindow().run()
