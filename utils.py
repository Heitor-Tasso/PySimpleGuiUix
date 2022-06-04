from PySimpleGUI import PySimpleGUI as sg
import sys, os

def space(w, h):
    return sg.Text(size=(w, h))

def icon_path(name, ad=''):
    local = f'{ad}assets/icons/{name}.png'
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, local)
    return local

def correct_path(path_filename):
    for w in ["\\", "//"]:
        path_filename = path_filename.replace(w, '/')
    return path_filename
