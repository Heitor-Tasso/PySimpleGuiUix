
from PySimpleGUI import PySimpleGUI as sg
from PySimpleGuiUix.utils import space, icon_path
from PySimpleGuiUix.popup import PopupError, PopupOk, PopupConfirm
from PySimpleGuiUix.window import WindowBase
from __init__ import path

class ScreenLogin(WindowBase):

    size = [500, 500]
    title = 'Screen Login'
    btn_down = True

    def on_layout(self):
        self.layout = [
            [space(1, 3)],
            [space(21, 1), sg.Text('Login', font=('Arial', 30))], [space(1, 1)],
            [space(13, 1), 
                sg.Image(icon_path('user1', path), (30, 30)),
                sg.Text('Usuario', (7, 1), font=('Courier', 16))],
            [space(10, 1), 
                sg.Input('', (25, 1), font=('Calibri', 16), key='username')], [space(1, 1)],
            [space(13, 1), 
                sg.Image(icon_path('password1', path), (30, 30)),
                sg.Text('Senha', (7, 1), font=('Courier', 16))],
            [space(10, 1),
                sg.Input('', (25, 1), font=('Calibri', 16), key='password', password_char='*'),
                sg.Button(image_filename=icon_path('unsee_eye', path), key='btnPassword', button_color=self.back_theme, border_width=0)],
            [space(1, 2)],
            [space(14, 2), sg.Button('Connect', size=(12, 2)), sg.Button('Cancel', size=(12, 2))],
        ]

    def on_events(self, event, values):
        if event == 'Cancel':
            pop = PopupConfirm(text=" \n Really want continue? \n ").run(self)
            if pop.state == 'Confirm':
                self.close()
        # fazer login
        elif event == 'Connect':
            # usuario e senha dos inputs
            input_password = values['password']
            input_user = values['username']

            if input_password == '' or input_user == '':
                # Error handling: se qualquer um dos campos não puderem ser autenticados
                return PopupError(text=' \n Usuario ou Senha inválidos!! \n ').run(self)
            return PopupOk(text=' \n Senha Correta! \n ').run(self)

        elif event == 'btnPassword':
            # fazer a troca de imagem do botao "hide"
            # e mudar o caracter de mascara do sg.Input
            self.btn_down = not self.btn_down
            if self.btn_down:
                source = icon_path('unsee_eye', path)
                password_char = "*"
            else:
                source = icon_path('see_eye', path)
                password_char = ""
            self.window['btnPassword'].update(image_filename=source)
            self.window['password'].update(password_char=password_char)

if __name__ == '__main__':
    ScreenLogin().run()
