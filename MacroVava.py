import tkinter as tk
from tkinter import messagebox
import threading
import pyautogui
import keyboard
import mouse
import time
import pyperclip

class MacroApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Macro Vava")
        self.root.geometry("500x350")
        self.root.resizable(False, False)

        self.frases = [tk.StringVar() for _ in range(3)]
        self.teclas = [tk.StringVar() for _ in range(3)]
        self.tecla_entries = []
        self.select_buttons = []
        self.key_hook = None
        self.mouse_hook = None
        self.capturando = False
        self.macros_ativos = False
        self.macro_mapping = {}
        self.mouse_mapping = {}
        self.executando = False

        for i in range(3):
            tk.Label(root, text=f"Frase {i+1}:").place(x=30, y=30 + i*70)
            tk.Entry(root, textvariable=self.frases[i], width=30).place(x=100, y=30 + i*70)
            tk.Label(root, text="Tecla:").place(x=30, y=60 + i*70)
            entry = tk.Entry(root, textvariable=self.teclas[i], width=15, state='readonly')
            entry.place(x=100, y=60 + i*70)
            self.tecla_entries.append(entry)
            btn = tk.Button(root, text="Selecionar tecla", command=lambda idx=i: self.aguardar_tecla(idx))
            btn.place(x=230, y=58 + i*70)
            self.select_buttons.append(btn)

        self.status_label = tk.Label(root, text="", fg="green")
        self.status_label.place(x=30, y=260)

        tk.Button(root, text="Ativar Macros", command=self.ativar_macros).place(x=200, y=300)

    def aguardar_tecla(self, idx):
        if self.capturando:
            return
        self.capturando = True
        self.status_label.config(text="Pressione uma tecla ou botão do mouse...")
        if self.key_hook is not None:
            keyboard.unhook(self.key_hook)
            self.key_hook = None
        if self.mouse_hook is not None:
            mouse.unhook(self.mouse_hook)
            self.mouse_hook = None

        def on_key(e):
            self.tecla_entries[idx].config(state='normal')
            self.teclas[idx].set(e.name)
            self.tecla_entries[idx].config(state='readonly')
            self.status_label.config(text=f"Tecla selecionada: {e.name}")
            if self.key_hook is not None:
                keyboard.unhook(self.key_hook)
            if self.mouse_hook is not None:
                mouse.unhook(self.mouse_hook)
            self.key_hook = None
            self.mouse_hook = None
            self.capturando = False

        def on_mouse(e):
            if isinstance(e, mouse.ButtonEvent):
                valor = e.button
                print(f"Botão do mouse selecionado: {valor}")
                self.status_label.config(text=f"Tecla selecionada: {valor}")
            elif isinstance(e, mouse.WheelEvent):
                valor = 'wheel_up' if e.delta > 0 else 'wheel_down'
                print(f"Scroll do mouse selecionado: {valor}")
                self.status_label.config(text=f"Tecla selecionada: {valor}")
            else:
                return
            self.tecla_entries[idx].config(state='normal')
            self.teclas[idx].set(valor)
            self.tecla_entries[idx].config(state='readonly')
            if self.key_hook is not None:
                keyboard.unhook(self.key_hook)
            if self.mouse_hook is not None:
                mouse.unhook(self.mouse_hook)
            self.key_hook = None
            self.mouse_hook = None
            self.capturando = False

        self.key_hook = keyboard.hook(on_key)
        self.mouse_hook = mouse.hook(on_mouse)

    def on_key_press(self, e):
        if e.name in self.macro_mapping and not self.executando:
            frase = self.macro_mapping[e.name]
            print(f'Executando macro (teclado): /all {frase}')
            threading.Thread(target=self.executar_macro_thread, args=(frase,), daemon=True).start()

    def executar_macro_thread(self, frase):
        if self.executando:
            return
        
        self.executando = True
        try:
            print(f'Iniciando execução do macro: /all {frase}')
            
            clipboard_original = pyperclip.paste()
            
            time.sleep(0.01)
            
            pyautogui.press('enter')
            time.sleep(0.01)
            
            mensagem_completa = f"/all {frase}"
            pyperclip.copy(mensagem_completa)
            time.sleep(0.005)
            
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(0.005)
            
            pyautogui.press('enter')
            
            time.sleep(0.005)
            pyperclip.copy(clipboard_original)
            
            print(f'Macro executado com sucesso: {mensagem_completa}')
            
        except Exception as e:
            print(f'Erro ao executar macro: {e}')
        finally:
            self.executando = False

    def on_mouse_event(self, e):
        if isinstance(e, mouse.ButtonEvent):
            if e.button in self.mouse_mapping and not self.executando:
                frase = self.mouse_mapping[e.button]
                print(f'Executando macro (mouse): /all {frase}')
                threading.Thread(target=self.executar_macro_thread, args=(frase,), daemon=True).start()
        elif isinstance(e, mouse.WheelEvent):
            wheel_key = 'wheel_up' if e.delta > 0 else 'wheel_down'
            if wheel_key in self.mouse_mapping and not self.executando:
                frase = self.mouse_mapping[wheel_key]
                print(f'Executando macro (scroll): /all {frase}')
                threading.Thread(target=self.executar_macro_thread, args=(frase,), daemon=True).start()

    def ativar_macros(self):
        if self.macros_ativos:
            keyboard.unhook_all()
            mouse.unhook_all()
            self.macro_mapping = {}
            self.mouse_mapping = {}
            self.macros_ativos = False
            self.status_label.config(text="Macros desativadas.")
            return

        frases = [f.get().strip() for f in self.frases]
        teclas = [t.get().strip() for t in self.teclas]
        
        ativou = False
        self.macro_mapping = {}
        self.mouse_mapping = {}
        
        for i in range(3):
            if frases[i] and teclas[i]:
                print(f'Registrando hotkey: {teclas[i]}')
                
                if teclas[i] in ['left', 'right', 'middle', 'x', 'wheel_up', 'wheel_down']:
                    self.mouse_mapping[teclas[i]] = frases[i]
                    ativou = True
                    print(f'Mouse hotkey {teclas[i]} registrada com sucesso')
                else:
                    self.macro_mapping[teclas[i]] = frases[i]
                    ativou = True
                    print(f'Teclado hotkey {teclas[i]} registrada com sucesso')
        
        if ativou:
            self.macros_ativos = True
            keyboard.on_press(self.on_key_press)
            mouse.hook(self.on_mouse_event)
            self.status_label.config(text="Macros ativadas! Pressione 'Ativar Macros' novamente para desativar.")
        else:
            self.status_label.config(text="Nenhuma macro ativada.")

    def executar_macro(self, frase):
        print(f'Executando macro: /all {frase}')
        pyautogui.press('enter')
        pyautogui.write('/all ')
        pyautogui.write(frase)
        pyautogui.press('enter')

if __name__ == "__main__":
    root = tk.Tk()
    app = MacroApp(root)
    root.mainloop() 