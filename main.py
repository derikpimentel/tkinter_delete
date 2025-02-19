# Biblioteca para criação de janelas
import time
from tkinter import *
from tkinter import messagebox
from tkinter.ttk import Treeview, Progressbar
import pystray
from pystray import MenuItem as item
from PIL import Image, ImageDraw
import threading
from new_window import NewWindow

class LoadingScreen:
    def __init__(self, master=None):
        self.master = Toplevel(master.withdraw())
        self.master.geometry("300x100")

        # Remove a barra de título e todos os botões (minimizar, maximizar, fechar)
        self.master.overrideredirect(True)
        
        self.label = Label(self.master, text="Carregando, por favor aguarde...")
        self.label.pack(pady=10)

        # Cria uma barra de progresso
        self.progress = Progressbar(self.master, orient="horizontal", mode="determinate", length=250)
        self.progress.pack(pady=10)

        # Centraliza a janela após o conteúdo ser adicionado
        self.center_window()

    def center_window(self):
        # Atualiza as tarefas pendentes para garantir que o tamanho correto seja calculado
        self.master.update_idletasks()

        # Obtém a largura e altura da tela
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()

        # Obtém a largura e altura da janela atual
        width = self.master.winfo_width()
        height = self.master.winfo_height()

        # Calcula a posição x e y para centralizar a janela
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)

        # Define a geometria da janela
        self.master.geometry(f"{width}x{height}+{x}+{y}")

    def close(self):
        self.master.destroy()

    def update_progress(self, value):
        self.progress['value'] = value
        self.master.update_idletasks()  # Atualiza a interface gráfica

class Application:
    def __init__(self, master=None):
        # Variável para a janela principal
        self.master = master

        # Chama a tela de carregamento
        self.start_loading()

        # Lista para armazenar janelas filhas
        self.child_windows = []

        # Chama o método de minimizar para a bandeja na inicialização
        self.minimize_to_tray()

        # Define o título da janela
        self.master.title("Olá mundo!")

        # Define o tamanho da janela (largura x altura)
        #self.master.geometry("500x500")

        # Detectar evento de minimizar a janela
        self.master.bind("<Unmap>", lambda event: self.minimize_to_tray() if master.state() == 'iconic' else None)

        # Desabilita a maximização
        self.master.resizable(False, False)

        self.font = ("Verdana", "8")

        # Cria o menu principal
        self.menu_bar = Menu(master)

        # Criando o menu "Arquivo"
        self.menu_file = Menu(self.menu_bar, tearoff=0)
        self.menu_file.add_command(label="Novo", command=self.new_file) # Adiciona a opção "Novo"
        self.menu_file.add_command(label="Abrir") # Adiciona a opção "Abrir"
        self.menu_file.add_separator() # Adiciona um separador
        self.menu_file.add_command(label="Sair", command=self.master.quit) # Adiciona a opção "Sair"

        # Adiciona o menu "Arquivo" à barra de menu
        self.menu_bar.add_cascade(label="Arquivo", menu=self.menu_file)

        # Criando outro menu, como "Editar"
        self.menu_edit = Menu(self.menu_bar, tearoff=0)
        self.menu_edit.add_command(label="Copiar")
        self.menu_edit.add_command(label="Colar")

        # Adiciona o menu "Editar" à barra de menu
        self.menu_bar.add_cascade(label="Editar", menu=self.menu_edit)

        # Adiciona o menu "Janela" à barra de menu
        self.menu_bar.add_command(label="Janela", command=self.open_new_window)

        # Adiciona o menu "Janela2" à barra de menu
        self.menu_bar.add_command(label="Janela2", command=self.open_external_window)

        # Configura a janela para usar essa barra de menu
        master.config(menu=self.menu_bar)

        # Adiciona um rótulo (label) à janela
        self.label = Label(master, text="Seja bem-vindo!")
        self.label.pack(pady=20)

        self.container01 = Frame(master)
        self.container01.pack(pady=20)

        # Criando a Treeview (Tabela)
        self.table = Treeview(self.container01, columns=("Nome", "Idade"), show="headings")
        self.table.heading("Nome", text="Nome")
        self.table.heading("Idade", text="Idade")
        self.table.column("Nome")
        self.table.column("Idade", width=100)

        # Adiciona uma barra de rolagem à tabela
        self.scrollbar = Scrollbar(self.container01, orient="vertical", command=self.table.yview)
        self.table.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side='right', fill='y')
        
        # Insere a tabela na janela
        self.table.pack()
        
        # Campos de entrada para adicionar novos dados
        self.container02 = Frame(master)
        self.container02.pack(pady=10)

        Label(self.container02, text="Nome:").grid(row=0, column=0, padx=5)
        self.txt_name = Entry(self.container02)
        self.txt_name.grid(row=0, column=1, padx=5)

        Label(self.container02, text="Idade:").grid(row=1, column=0, padx=5)
        self.txt_age = Entry(self.container02)
        self.txt_age.grid(row=1, column=1, padx=5)

        # Botões para adicionar e remover dados
        self.container03 = Frame(master)
        self.container03.pack(pady=10)

        self.btn_new = Button(self.container03, text="Adicionar")
        self.btn_new["command"] = self.new_row
        self.btn_new.grid(row=0, column=0, padx=10)

        self.btn_delete = Button(self.container03, text="Remover Selecionado")
        self.btn_delete["command"] = self.delete_row
        self.btn_delete.grid(row=0, column=1, padx=10)

        # Adiciona um botão à janela
        self.btn_click = Button(master, text="Clique aqui!")
        self.btn_click["command"] = lambda: print("Botão clicado!")
        self.btn_click.pack(pady=10)

        # Botão de minimizar para a bandeja
        self.btn_minimize = Button(master, text="Minimizar para a bandeja", command=self.minimize_to_tray)
        self.btn_minimize.pack(pady=10)

    def start_loading(self):
        # Cria a tela de carregamento
        loading_screen = LoadingScreen(self.master)

        # Cria uma thread para simular uma operação longa
        threading.Thread(target=self.long_running_operation, args=(loading_screen,), daemon=True).start()

    def long_running_operation(self, loading_screen):
        # Simula uma operação longa, atualizando a barra de progresso
        for i in range(101):  # Simula 100% de progresso
            time.sleep(0.05)  # Simula uma tarefa que leva tempo
            loading_screen.update_progress(i)  # Atualiza a barra de progresso

        # Fecha a tela de carregamento após a operação
        loading_screen.close()

    # Função para ações de menu
    def new_file(self):
        messagebox.showinfo("Novo Arquivo", "Você clicou em Novo Arquivo!")

    # Função para adicionar uma nova linha na tabela
    def new_row(self):
        name = self.txt_name.get()
        age = self.txt_age.get()
        if name and age:
            self.table.insert('', 'end', values=(name, age))
            self.txt_name.delete(0, END)
            self.txt_age.delete(0, END)

    # Função para remover a linha selecionada
    def delete_row(self):
        selected_item = self.table.selection()
        if selected_item:
            self.table.delete(selected_item)

    # Função para minimizar a janela para a bandeja
    def minimize_to_tray(self):
        self.master.withdraw()  # Esconde a janela principal
        self.close_all_child_windows()
        self.create_tray_icon()  # Cria o ícone da bandeja

    # Função para fechar todas as janelas filhas
    def close_all_child_windows(self):
        for window in self.child_windows:
            if window.winfo_exists():
                window.destroy()
        self.child_windows.clear()  # Limpa a lista de janelas filhas

    # Função para criar o ícone da bandeja
    def create_tray_icon(self):
        # Criar imagem para o ícone da bandeja (16x16 px)
        image = Image.new('RGB', (16, 16), (0, 0, 0))
        d = ImageDraw.Draw(image)
        d.rectangle((0, 0, 16, 16), fill=(0, 128, 255))

        # Função para restaurar a janela ao clicar no ícone
        def restore_window(icon):
            icon.stop()
            self.master.deiconify()
            
        def exit(icon):
            icon.stop()
            self.master.destroy()

        # Menu do ícone da bandeja
        menu = (item('Restaurar', restore_window), item('Sair', exit))

        # Criação do ícone da bandeja
        self.icon = pystray.Icon("test", image, "App Tkinter", menu)
        threading.Thread(target=self.icon.run, daemon=True).start()  # Executa o ícone da bandeja em uma nova thread

    def open_new_window(self):
        # Cria uma nova janela
        new_window = Toplevel(self.master)
        new_window.title("Nova Janela")
        
        # Adiciona um rótulo à nova janela
        label = Label(new_window, text="Esta é uma nova janela!")
        label.pack(pady=20)
        
        # Adiciona a janela filha na lista para rastreamento
        self.child_windows.append(new_window)

    def open_external_window(self):
        child = NewWindow(self.master)
        
        # Adiciona a janela filha na lista para rastreamento
        self.child_windows.append(child.master)

root = Tk() # Criando a janela principal
Application(root)
root.mainloop() # Mantêm a janela aberta