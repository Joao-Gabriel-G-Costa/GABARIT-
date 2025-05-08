import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import sqlite3

DB_FILE = "BANCOGABARIBOT.db"

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Gabaritô")
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f0f0")

        self.inicializar_db()
        self.turmas = self.carregar_turmas_db()
        
        self.button_frame = None 
        self.add_btn = None       
        self.current_turma = None 
        self.criar_header()
        self.criar_tela_principal()

    def inicializar_db(self):
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # cursor.execute('''
        # CREATE TABLE IF NOT EXISTS TURMA (
        #     TURMA_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        #     TURMA_NOME TEXT NOT NULL,
        #     TURMA_MATERIA TEXT NOT NULL
        # )
        # ''')
        # nao precisa mais disso o banco já existe vou deixar comentado só pra ficar mais 
        # facil de entender o que eu fiz
        
        conn.commit()
        conn.close()
    
    def carregar_turmas_db(self):
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        cursor.execute("SELECT TURMA_ID, TURMA_NOME, TURMA_MATERIA FROM TURMA ORDER BY TURMA_NOME")
        rows = cursor.fetchall()

        turmas = []
        for row in rows:
            turmas.append({
                "TURMA_ID": row[0],
                "TURMA_NOME": row[1],
                "TURMA_MATERIA": row[2]
            })

        conn.close()
        return turmas

    
    def adicionar_turma_db(self, TURMA_NOME, TURMA_MATERIA):
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        cursor.execute("INSERT INTO TURMA (TURMA_NOME, TURMA_MATERIA) VALUES (?, ?)", (TURMA_NOME, TURMA_MATERIA))
        TURMA_ID = cursor.lastrowid

        conn.commit()
        conn.close()

        return TURMA_ID

    
    def excluir_turma_db(self, TURMA_ID):
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM TURMA WHERE TURMA_ID = ?", (TURMA_ID,))
        
        conn.commit()
        conn.close()
    
    def atualizar_turma_db(self, TURMA_ID, TURMA_NOME, TURMA_MATERIA):
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute("UPDATE TURMA SET TURMA_NOME = ?, TURMA_MATERIA = ? WHERE TURMA_ID = ?", 
                      (TURMA_NOME, TURMA_MATERIA, TURMA_ID))
        
        conn.commit()
        conn.close()

    def criar_header(self):
        self.header = tk.Frame(self.root, bg="#003a4d", height=60)
        self.header.pack(fill=tk.X)

        self.logo_label = tk.Label(self.header, text="Gabaritô", font=("Arial", 20, "bold"),
                                   bg="#003a4d", fg="white")
        self.logo_label.pack(side=tk.LEFT, padx=20)

        self.config_btn = tk.Button(self.header, text="⚙", font=("Arial", 16),
                                    bd=0, bg="#003a4d", fg="white", activebackground="#3a5a8a")
        self.config_btn.pack(side=tk.RIGHT, padx=10)

        self.perfil_btn = tk.Button(self.header, text="👤", font=("Arial", 16),
                                    bd=0, bg="#003a4d", fg="white", activebackground="#3a5a8a")
        self.perfil_btn.pack(side=tk.RIGHT, padx=10)

    def criar_tela_principal(self):
        if hasattr(self, 'main_frame'):
            self.main_frame.destroy()
        
        if self.button_frame:
            self.button_frame.destroy()

        self.main_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.turmas = self.carregar_turmas_db()

        if not self.turmas:
            self.criar_tela_sem_turmas()
        else:
            self.exibir_lista_turmas()

        self.button_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.button_frame.pack(fill=tk.X, padx=20, pady=10)

        self.add_btn = tk.Button(self.button_frame, text="+", font=("Arial", 20),
                          bg="#4a6fa5", fg="white", activebackground="#3a5a8a",
                          bd=0, width=2, height=1, command=self.abrir_tela_cadastro)
        self.add_btn.pack(side=tk.RIGHT)

    def criar_tela_sem_turmas(self):
        center_frame = tk.Frame(self.main_frame, bg="#f0f0f0")
        center_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        msg_label = tk.Label(center_frame, text="Crie uma turma para começar",
                             font=("Arial", 16), bg="#f0f0f0", fg="#555555")
        msg_label.pack(pady=20)

    def exibir_lista_turmas(self):
        titulo_label = tk.Label(self.main_frame, text="Minhas Turmas",
                                font=("Arial", 16, "bold"), bg="#f0f0f0")
        titulo_label.pack(anchor=tk.W, pady=(0, 20))

        container = tk.Frame(self.main_frame, bg="#f0f0f0")
        container.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(container, bg="#f0f0f0", highlightthickness=0)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(container, orient=tk.VERTICAL, command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        canvas.configure(yscrollcommand=scrollbar.set)

        lista_frame = tk.Frame(canvas, bg="#f0f0f0")
        canvas_window = canvas.create_window((0, 0), window=lista_frame, anchor="nw", width=canvas.winfo_width())
        
        self.root.update_idletasks()
        canvas_width = container.winfo_width() - scrollbar.winfo_width()
        canvas.itemconfig(canvas_window, width=canvas_width)
        
        def _on_mousewheel(event):
            if event.num == 5 or event.delta == -120:
                canvas.yview_scroll(1, "units")
            elif event.num == 4 or event.delta == 120:
                canvas.yview_scroll(-1, "units")

        def on_canvas_configure(event):
            canvas_width = event.width
            canvas.itemconfig(canvas_window, width=canvas_width)
            
        canvas.bind('<Configure>', on_canvas_configure)
        canvas.bind_all("<MouseWheel>", _on_mousewheel) 
        
        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        lista_frame.bind("<Configure>", on_frame_configure)

        for i in range(3):
            lista_frame.columnconfigure(i, weight=1, uniform="column")

        row, col = 0, 0
        max_col = 3
        card_width = canvas_width // max_col - 20  

        for i, turma in enumerate(self.turmas):
            row = i // max_col
            col = i % max_col
            
            card = tk.Frame(lista_frame, bg="white", bd=1, relief=tk.SOLID, cursor="hand2")

            card.grid(row=row, column=col, padx=10, pady=20, sticky="nsew")
            
            card.turma_data = turma
            
            def on_enter(event):
                widget = event.widget
                widget.configure(bg="#f0f7ff")
                for child in widget.winfo_children():
                    if isinstance(child, tk.Label):
                        child.configure(bg="#f0f7ff")
            
            def on_leave(event):
                widget = event.widget
                widget.configure(bg="white")
                for child in widget.winfo_children():
                    if isinstance(child, tk.Label):
                        child.configure(bg="white")
            
            def on_click(event):
                widget = event.widget
                if hasattr(widget, 'turma_data'):
                    self.abrir_tela_turma(widget.turma_data)
                elif hasattr(widget.master, 'turma_data'):
                    self.abrir_tela_turma(widget.master.turma_data)
            
            card.bind("<Enter>", on_enter)
            card.bind("<Leave>", on_leave)
            card.bind("<Button-1>", on_click)

            nome_label = tk.Label(card, text=turma["nome"], font=("Arial", 14, "bold"),
                                  bg="white", fg="#4aa6ae", cursor="hand2")
            nome_label.pack(anchor=tk.W, padx=10, pady=(10, 5))

            materia_label = tk.Label(card, text=turma["materia"], font=("Arial", 12),
                                    bg="white", fg="#555555", cursor="hand2")
            materia_label.pack(anchor=tk.W, padx=10, pady=(0, 10))

            nome_label.bind("<Enter>", on_enter)
            nome_label.bind("<Leave>", on_leave)
            nome_label.bind("<Button-1>", on_click)
            
            materia_label.bind("<Enter>", on_enter)
            materia_label.bind("<Leave>", on_leave)
            materia_label.bind("<Button-1>", on_click)


    def abrir_tela_turma(self, turma):
        self.current_turma = turma
        
        if hasattr(self, 'main_frame'):
            self.main_frame.destroy()
            
        if self.button_frame:
            self.button_frame.destroy()
        
        self.root.configure(bg="white")
            
        self.main_frame = tk.Frame(self.root, bg="white")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        header_frame = tk.Frame(self.main_frame, bg="white")
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        voltar_btn = tk.Button(header_frame, text="←", font=("Arial", 16),
                               bg="#013b50", fg="white", bd=0, 
                               activebackground="black", activeforeground="gray",
                               command=self.voltar_tela_principal)
        voltar_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Label(header_frame, text=turma["nome"], 
                 font=("Arial", 18, "bold"), bg="white", fg="black").pack(side=tk.LEFT)
        
        sidebar_frame = tk.Frame(self.main_frame, bg="white", bd=1, relief=tk.SOLID, width=160)
        sidebar_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 30))
        sidebar_frame.pack_propagate(False)  
        
        menu_buttons = [
            ("Alunos", "👥"),
            ("Desempenho", "✓"),
            ("Provas", "📝")
        ]
        
        for texto, icone in menu_buttons:
            btn = tk.Button(sidebar_frame, text=f"{icone} {texto}",
                          font=("Arial", 12), bg="#2e828f", fg="white",
                          bd=1, relief=tk.SOLID, anchor=tk.W,
                          activebackground="#333", activeforeground="white")
            btn.pack(fill=tk.X, pady=5, padx=2)
        
        content_frame = tk.Frame(self.main_frame, bg="white")
        content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        content_header = tk.Frame(content_frame, bg="white")
        content_header.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(content_header, text=f" {turma['materia']}", 
                 font=("Arial", 14, "bold"), bg="white", fg="black").pack(side=tk.LEFT)
        
        options_frame = tk.Frame(content_frame, bg="white")
        options_frame.pack(fill=tk.X, pady=10)
        
        editar_btn = tk.Button(options_frame, text="Editar Turma", 
                             font=("Arial", 11), bg="#333", fg="white",
                             activebackground="#555", activeforeground="white",
                             command=lambda: self.abrir_tela_editar_turma(turma))
        editar_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        excluir_btn = tk.Button(options_frame, text="Excluir Turma", 
                              font=("Arial", 11), bg="#333", fg="white",
                              activebackground="#555", activeforeground="white",
                              command=lambda: self.confirmar_exclusao_turma(turma))
        excluir_btn.pack(side=tk.LEFT)
        
        content_main = tk.Frame(content_frame, bg="white")
        content_main.pack(fill=tk.BOTH, expand=True, pady=20)

    def abrir_tela_cadastro(self):
        if hasattr(self, 'main_frame'):
            self.main_frame.destroy()
            
        if self.button_frame:
            self.button_frame.destroy()
            
        self.root.configure(bg="#f0f0f0")

        self.main_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        tk.Label(self.main_frame, text="Cadastrar Nova Turma",
                 font=("Arial", 18, "bold"), bg="#f0f0f0").pack(anchor=tk.W, pady=(0, 30))

        form_frame = tk.Frame(self.main_frame, bg="#f0f0f0")
        form_frame.pack(fill=tk.BOTH, expand=True, padx=50)

        tk.Label(form_frame, text="Nome da Turma:", font=("Arial", 12),
                 bg="#f0f0f0").pack(anchor=tk.W)
        self.nome_entry = tk.Entry(form_frame, font=("Arial", 12))
        self.nome_entry.pack(anchor=tk.W, pady=(0, 20), fill=tk.X)

        tk.Label(form_frame, text="Matéria:", font=("Arial", 12),
                 bg="#f0f0f0").pack(anchor=tk.W)
        self.materia_entry = tk.Entry(form_frame, font=("Arial", 12))
        self.materia_entry.pack(anchor=tk.W, pady=(0, 30), fill=tk.X)

        button_frame = tk.Frame(form_frame, bg="#f0f0f0")
        button_frame.pack(fill=tk.X, pady=20)

        tk.Button(button_frame, text="Cancelar", font=("Arial", 12),
                  bg="#f0f0f0", width=10, command=self.voltar_tela_principal).pack(side=tk.LEFT, padx=(0, 10))

        tk.Button(button_frame, text="Adicionar", font=("Arial", 12),
                  bg="#4a6fa5", fg="white", width=10, command=self.adicionar_turma).pack(side=tk.LEFT)

    def adicionar_turma(self):
        TURMA_NOME = self.nome_entry.get().strip()
        TURMA_MATERIA = self.materia_entry.get().strip()

        if not TURMA_NOME or not TURMA_MATERIA:
            messagebox.showwarning("Aviso", "Por favor, preencha todos os campos!")
            return

        for TURMA in self.turmas:
            if TURMA["nome"].lower() == TURMA_NOME.lower():
                messagebox.showwarning("Duplicado", "Essa turma já foi cadastrada!")
                return

        TURMA_ID = self.adicionar_turma_db(TURMA_NOME, TURMA_MATERIA)
        
        self.turmas.append({"id": TURMA_ID, "nome": TURMA_NOME, "materia": TURMA_MATERIA})
        
        self.voltar_tela_principal()

    def abrir_tela_editar_turma(self, turma):
        self.root.configure(bg="#f0f0f0")
        
        if hasattr(self, 'main_frame'):
            self.main_frame.destroy()
            
        if self.button_frame:
            self.button_frame.destroy()

        self.main_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        tk.Label(self.main_frame, text="Editar Turma",
                 font=("Arial", 18, "bold"), bg="#f0f0f0").pack(anchor=tk.W, pady=(0, 30))

        form_frame = tk.Frame(self.main_frame, bg="#f0f0f0")
        form_frame.pack(fill=tk.BOTH, expand=True, padx=50)

        tk.Label(form_frame, text="Nome da Turma:", font=("Arial", 12),
                 bg="#f0f0f0").pack(anchor=tk.W)
        self.nome_entry = tk.Entry(form_frame, font=("Arial", 12))
        self.nome_entry.insert(0, turma["nome"])
        self.nome_entry.pack(anchor=tk.W, pady=(0, 20), fill=tk.X)

        tk.Label(form_frame, text="Matéria:", font=("Arial", 12),
                 bg="#f0f0f0").pack(anchor=tk.W)
        self.materia_entry = tk.Entry(form_frame, font=("Arial", 12))
        self.materia_entry.insert(0, turma["materia"])
        self.materia_entry.pack(anchor=tk.W, pady=(0, 30), fill=tk.X)

        button_frame = tk.Frame(form_frame, bg="#f0f0f0")
        button_frame.pack(fill=tk.X, pady=20)

        tk.Button(button_frame, text="Cancelar", font=("Arial", 12),
                  bg="#f0f0f0", width=10, 
                  command=lambda: self.abrir_tela_turma(turma)).pack(side=tk.LEFT, padx=(0, 10))

        tk.Button(button_frame, text="Salvar", font=("Arial", 12),
                  bg="#4a6fa5", fg="white", width=10, 
                  command=lambda: self.salvar_edicao_turma(turma)).pack(side=tk.LEFT)

    def salvar_edicao_turma(self, turma):
        nome = self.nome_entry.get().strip()
        materia = self.materia_entry.get().strip()

        if not nome or not materia:
            messagebox.showwarning("Aviso", "Por favor, preencha todos os campos!")
            return

        for t in self.turmas:
            if t["nome"].lower() == nome.lower() and t["id"] != turma["id"]:
                messagebox.showwarning("Duplicado", "Já existe outra turma com este nome!")
                return

        self.atualizar_turma_db(turma["id"], nome, materia)
        
        turma["nome"] = nome
        turma["materia"] = materia
        
        self.abrir_tela_turma(turma)

    def confirmar_exclusao_turma(self, turma):
        resposta = messagebox.askyesno("Confirmação", 
                                       f"Tem certeza que deseja excluir a turma '{turma['nome']}'?")
        if resposta:
            self.excluir_turma_db(turma["id"])
            
            self.turmas = [t for t in self.turmas if t["id"] != turma["id"]]
            
            self.voltar_tela_principal()

    def voltar_tela_principal(self):
        self.root.configure(bg="#f0f0f0")
        self.criar_tela_principal()
