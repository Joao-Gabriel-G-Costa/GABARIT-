import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import sqlite3
from frames.provas import Provas

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
        self.alunos = []
        # Remove the undefined attribute reference
        # self.nova_janela

    def mostrar_alunos(self, turma):
            if hasattr(self, 'main_frame'):
                self.main_frame.destroy()
            if self.button_frame:
                self.button_frame.destroy()

            self.root.configure(bg="white")

            self.main_frame = tk.Frame(self.root, bg="white")
            self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

            header = tk.Frame(self.main_frame, bg="white")
            header.pack(fill=tk.X)

            voltar_btn = tk.Button(header, text="← Voltar", font=("Arial", 12),
                                command=lambda: self.abrir_tela_turma(turma),
                                bg="#013b50", fg="white")
            voltar_btn.pack(side=tk.LEFT)

            tk.Label(header, text=f"Alunos da Turma: {turma['TURMA_NOME']}",
                    font=("Arial", 16, "bold"), bg="white").pack(side=tk.LEFT, padx=10)

            alunos = self.carregar_alunos_db()

            if not alunos:
                self.criar_tela_sem_alunos()
            else:
                for aluno in alunos:
                    frame = tk.Frame(self.main_frame, bg="#e0e0e0", bd=1, relief=tk.SOLID, padx=10, pady=5)
                    frame.pack(fill=tk.X, pady=5)

                    nome_label = tk.Label(frame, text=aluno["ALUN_NOME"], font=("Arial", 12), bg="#e0e0e0")
                    nome_label.pack(side=tk.LEFT)

                    cpf_label = tk.Label(frame, text=f"CPF: {aluno['ALUN_CPF']}", font=("Arial", 10), bg="#e0e0e0")
                    cpf_label.pack(side=tk.LEFT, padx=10)

                    editar_btn = tk.Button(frame, text="✏️", command=lambda a=aluno: self.abrir_tela_cadastro_aluno(a, turma))
                    editar_btn.pack(side=tk.RIGHT, padx=5)

                    excluir_btn = tk.Button(frame, text="🗑️", command=lambda a=aluno: self.excluir_aluno_e_atualizar(a["ALUN_MATRICULA"], turma))
                    excluir_btn.pack(side=tk.RIGHT, padx=5)

            self.adicionar_aluno_botao() 

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
    
    def carregar_alunos_db(self):
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        cursor.execute("SELECT ALUN_MATRICULA, ALUN_NOME, ALUN_CPF FROM ALUNO ORDER BY ALUN_NOME")
        rows = cursor.fetchall()

        alunos = []
        for row in rows:
            alunos.append({
                "ALUN_MATRICULA": row[0],
                "ALUN_NOME": row[1],
                "ALUN_CPF": row[2]
            })

        conn.close()
        return alunos

    def adicionar_aluno_db(self, ALUN_NOME, ALUN_CPF):
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        cursor.execute("INSERT INTO ALUNO (ALUN_NOME, ALUN_CPF) VALUES (?, ?)", (ALUN_NOME, ALUN_CPF))
        TURMA_ID = cursor.lastrowid

        conn.commit()
        conn.close()

        return TURMA_ID
    
    def adicionar_turma_db(self, TURMA_NOME, TURMA_MATERIA):
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        cursor.execute("INSERT INTO TURMA (TURMA_NOME, TURMA_MATERIA) VALUES (?, ?)", (TURMA_NOME, TURMA_MATERIA))
        TURMA_ID = cursor.lastrowid

        conn.commit()
        conn.close()

        return TURMA_ID
    
    def aluno_existe_db(self, nome, cpf):
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM ALUNO WHERE ALUN_NOME = ? OR ALUN_CPF = ?", (nome, cpf))
        exists = cursor.fetchone() is not None
        conn.close()
        return exists
    
    def excluir_turma_db(self, TURMA_ID):
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM TURMA WHERE TURMA_ID = ?", (TURMA_ID,))
        
        conn.commit()
        conn.close()

    def excluir_aluno_db(self, ALUN_MATRICULA):
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM ALUNO WHERE ALUN_MATRICULA = ?", (ALUN_MATRICULA,))
        
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
            
        # Always add the button
        self.adicionar_turma_botao()
            
    def criar_tela_sem_alunos(self):
        center_frame = tk.Frame(self.main_frame, bg="#f0f0f0")
        center_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        msg_label = tk.Label(center_frame, text="Registre um aluno",
                             font=("Arial", 16), bg="#f0f0f0", fg="#555555")
        msg_label.pack(pady=20)
            
    def criar_tela_alunos(self):
        if hasattr(self, 'main_frame'):
            self.main_frame.destroy()

        if self.button_frame:
            self.button_frame.destroy()

        self.main_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.alunos = self.carregar_alunos_db()

        if not self.alunos:
            self.criar_tela_sem_alunos()
        else:
            self.cadastro_de_alunos()
            
        self.adicionar_aluno_botao()

    def adicionar_turma_botao(self):
        if self.button_frame:
            self.button_frame.destroy()
            
        self.button_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.button_frame.pack(fill=tk.X, padx=20, pady=10)

        self.add_btn = tk.Button(self.button_frame, text="+", font=("Arial", 20),
                          bg="#4a6fa5", fg="black", activebackground="#3a5a8a",
                          bd=0, width=2, height=1, command=self.abrir_tela_cadastro)
        self.add_btn.pack(side=tk.RIGHT)
        
    def adicionar_aluno_botao(self):
        if self.button_frame:
            self.button_frame.destroy()
            
        self.button_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.button_frame.pack(fill=tk.X, padx=20, pady=10)

        self.add_btn = tk.Button(self.button_frame, text="+", font=("Arial", 20),
                          bg="#4a6fa5", fg="black", activebackground="#3a5a8a",
                          bd=0, width=2, height=1, command=self.cadastro_de_alunos)
        self.add_btn.pack(side=tk.RIGHT)

    def criar_tela_sem_turmas(self):
        center_frame = tk.Frame(self.main_frame, bg="#f0f0f0")
        center_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        msg_label = tk.Label(center_frame, text="Crie uma turma para começar",
                             font=("Arial", 16), bg="#f0f0f0", fg="#555555")
        msg_label.pack(pady=20)

    def limpar_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def abrir_tela_cadastro(self):
        if hasattr(self, 'main_frame'):
            self.main_frame.destroy()
            
        if self.button_frame:
            self.button_frame.destroy()

        self.main_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        tk.Label(self.main_frame, text="Nova Turma",
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
                  bg="#f0f0f0", width=10, 
                  command=self.voltar_tela_principal).pack(side=tk.LEFT, padx=(0, 10))

        tk.Button(button_frame, text="Salvar", font=("Arial", 12),
                  bg="#4a6fa5", fg="white", width=10, 
                  command=self.adicionar_turma).pack(side=tk.LEFT)

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
        canvas_width = canvas_width if canvas_width > 0 else 750  # Default value if canvas width is not yet determined
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

            nome_label = tk.Label(card, text=turma["TURMA_NOME"], font=("Arial", 14, "bold"),
                                  bg="white", fg="#4aa6ae", cursor="hand2")
            nome_label.pack(anchor=tk.W, padx=10, pady=(10, 5))

            materia_label = tk.Label(card, text=turma["TURMA_MATERIA"], font=("Arial", 12),
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
        
        tk.Label(header_frame, text=turma["TURMA_NOME"], 
                 font=("Arial", 18, "bold"), bg="white", fg="black").pack(side=tk.LEFT)
        
        sidebar_frame = tk.Frame(self.main_frame, bg="white", bd=1, relief=tk.SOLID, width=160)
        sidebar_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 30))
        sidebar_frame.pack_propagate(False)  
        
        menu_buttons = [
            ("Alunos", "👥"),
            ("Desempenho", "✓"),
            ("Provas", "📝"),
            ("Editar", "✏️"),
            ("Excluir", "❌")
        ]
        
        for texto, icone in menu_buttons:
            if texto == "Editar":
                command = lambda t=turma: self.abrir_tela_editar_turma(t)
            elif texto == "Excluir":
                command = lambda t=turma: self.confirmar_exclusao_turma(t)
            elif texto == "Alunos": 
                command = lambda t=turma: self.mostrar_alunos(t)
            elif texto == "Desempenho":
                command = lambda: messagebox.showinfo("Info", "Função em desenvolvimento")
            elif texto == "Provas":
                command = lambda t=turma: self.abrir_tela_provas(t)

            btn = tk.Button(sidebar_frame, text=f"{icone} {texto}",
                            font=("Arial", 12), bg="#2e828f", fg="white",
                            bd=1, relief=tk.SOLID, anchor=tk.W,
                            activebackground="#333", activeforeground="white",
                            command=command)
            btn.pack(fill=tk.X, pady=5, padx=2)
        
        content_frame = tk.Frame(self.main_frame, bg="white")
        content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        content_header = tk.Frame(content_frame, bg="white")
        content_header.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(content_header, text=f" {turma['TURMA_MATERIA']}", 
                 font=("Arial", 14, "bold"), bg="white", fg="black").pack(side=tk.LEFT)
        
        options_frame = tk.Frame(content_frame, bg="white")
        options_frame.pack(fill=tk.X, pady=10)
    
        
        content_main = tk.Frame(content_frame, bg="white")
        content_main.pack(fill=tk.BOTH, expand=True, pady=20)

    def abrir_tela_provas(self, turma):
        # Crie uma nova janela para as provas
        nova_janela_provas = tk.Toplevel(self.root)  # Não precisa armazenar em self.nova_janela_provas
        nova_janela_provas.title(f"Provas - {turma['TURMA_NOME']}")

        # Função de callback para voltar à tela da turma (definida dentro de abrir_tela_provas)
        def voltar_para_turma():
            nova_janela_provas.destroy()
            self.abrir_tela_turma(turma)

        # Instancie a classe Provas, passando a nova janela e o callback
        Provas(nova_janela_provas, voltar_para_turma) # Não precisa armazenar em self.app_provas

    def abrir_tela_cadastro_aluno(self, aluno=None, turma=None):
        nova_janela = tk.Toplevel(self.root)
        nova_janela.title("Cadastrar Aluno" if not aluno else "Editar Aluno")

        tk.Label(nova_janela, text="Nome do Aluno:").pack()
        nome_entry = tk.Entry(nova_janela)
        nome_entry.pack()

        tk.Label(nova_janela, text="CPF do Aluno:").pack()
        cpf_entry = tk.Entry(nova_janela)
        cpf_entry.pack()

        if aluno:
            nome_entry.insert(0, aluno["ALUN_NOME"])
            cpf_entry.insert(0, aluno["ALUN_CPF"])

        def salvar_aluno():
            nome = nome_entry.get()
            cpf = cpf_entry.get()
            if aluno:
                self.editar_aluno(aluno["ALUN_MATRICULA"], nome, cpf)
            else:
                self.salvar_aluno_info(nome, cpf)
                # Aqui você pode criar a associação aluno-turma se quiser

            nova_janela.destroy()
            self.mostrar_alunos(turma)

        tk.Button(nova_janela, text="Salvar", command=salvar_aluno).pack(pady=10)
        
    def salvar_aluno_info(self, nome, cpf):
        # Método para salvar o aluno (renomeado para evitar conflito com outro método)
        if not nome or not cpf:
            messagebox.showwarning("Aviso", "Todos os campos são obrigatórios.")
            return

        try:
            self.adicionar_aluno_db(nome, cpf)
            messagebox.showinfo("Sucesso", "Aluno cadastrado com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro: {e}")

    def editar_aluno(self, matricula, nome, cpf):
        # Implementar a edição de aluno
        messagebox.showinfo("Info", "Função de edição em desenvolvimento")
        
    def excluir_aluno_e_atualizar(self, matricula, turma):
        # Implementar a exclusão de aluno
        resposta = messagebox.askyesno("Confirmação", "Tem certeza que deseja excluir este aluno?")
        if resposta:
            self.excluir_aluno_db(matricula)
            messagebox.showinfo("Sucesso", "Aluno excluído com sucesso!")
            self.mostrar_alunos(turma)
        
    def cadastro_de_alunos(self, turma=None):
        if hasattr(self, 'main_frame'):
            self.main_frame.destroy()

        if self.button_frame:
            self.button_frame.destroy()

        self.main_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        frame = tk.Frame(self.main_frame, bg="white", bd=2, relief=tk.GROOVE)
        frame.pack(pady=20, padx=20)

        titulo = tk.Label(frame, text="Cadastro de Aluno", font=("Arial", 16, "bold"), bg="white")
        titulo.grid(row=0, column=0, columnspan=2, pady=10)

        lbl_nome = tk.Label(frame, text="Nome:", font=("Arial", 12), bg="white")
        lbl_nome.grid(row=2, column=0, padx=10, pady=5, sticky=tk.E)
        self.entry_nome = tk.Entry(frame, font=("Arial", 12))
        self.entry_nome.grid(row=2, column=1, padx=10, pady=5)

        lbl_cpf = tk.Label(frame, text="CPF:", font=("Arial", 12), bg="white")
        lbl_cpf.grid(row=3, column=0, padx=10, pady=5, sticky=tk.E)
        self.entry_cpf = tk.Entry(frame, font=("Arial", 12))
        self.entry_cpf.grid(row=3, column=1, padx=10, pady=5)

        btn_salvar = tk.Button(frame, text="Salvar", font=("Arial", 12), bg="#4CAF50", fg="white",
                            command=self.salvar_aluno)
        btn_salvar.grid(row=4, column=0, padx=10, pady=20)

        btn_cancelar = tk.Button(frame, text="Voltar", font=("Arial", 12), bg="#f44336", fg="white",
                                command=self.voltar_tela_alunos)
        btn_cancelar.grid(row=4, column=1, padx=10, pady=20)

    def salvar_aluno(self):
        nome = self.entry_nome.get().strip()
        cpf = self.entry_cpf.get().strip()

        if not nome or not cpf:
            messagebox.showwarning("Aviso", "Todos os campos são obrigatórios.")
            return

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        try:
            cursor.execute("INSERT INTO ALUNO (ALUN_NOME, ALUN_CPF) VALUES (?, ?)",
                        (nome, cpf))
            conn.commit()
            messagebox.showinfo("Sucesso", "Aluno cadastrado com sucesso!")
            self.criar_tela_alunos()
        except sqlite3.IntegrityError:
            messagebox.showerror("Erro", "Já existe um aluno com essa matrícula ou CPF.")
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro: {e}")
        finally:
            conn.close()

    def salvar_aluno(self):
        nome = self.entry_nome.get().strip()
        cpf = self.entry_cpf.get().strip()

        if not nome or not cpf:
            messagebox.showwarning("Aviso", "Todos os campos são obrigatórios.")
            return

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        try:
            cursor.execute("INSERT INTO ALUNO (ALUN_NOME, ALUN_CPF) VALUES (?, ?)",
                        (nome, cpf))
            conn.commit()
            messagebox.showinfo("Sucesso", "Aluno cadastrado com sucesso!")
            self.criar_tela_alunos()
        except sqlite3.IntegrityError:
            messagebox.showerror("Erro", "Já existe um aluno com essa matrícula ou CPF.")
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro: {e}")
        finally:
            conn.close()

    def adicionar_aluno(self):
        ALUN_NOME = self.nome_aluno_entry.get().strip()
        ALUN_CPF = self.cpf_entry.get().strip()

        if not ALUN_NOME or not ALUN_CPF:
            messagebox.showwarning("Aviso", "Por favor, preencha todos os campos!")
            return

        if self.aluno_existe_db(ALUN_NOME, ALUN_CPF):
            messagebox.showwarning("Duplicado", "Esse aluno já está cadastrado!")
            return

        ALUN_MATRICULA = self.adicionar_aluno_db(ALUN_NOME, ALUN_CPF)
        
        self.alunos.append({"ALUN_MATRICULA": ALUN_MATRICULA, "ALUN_NOME": ALUN_NOME, "ALUN_CPF": ALUN_CPF})
        
        self.voltar_tela_alunos()
    
    def adicionar_turma(self):
        TURMA_NOME = self.nome_entry.get().strip()
        TURMA_MATERIA = self.materia_entry.get().strip()

        if not TURMA_NOME or not TURMA_MATERIA:
            messagebox.showwarning("Aviso", "Por favor, preencha todos os campos!")
            return

        for TURMA in self.turmas:
            if TURMA["TURMA_NOME"].lower() == TURMA_NOME.lower():
                messagebox.showwarning("Duplicado", "Essa turma já foi cadastrada!")
                return

        TURMA_ID = self.adicionar_turma_db(TURMA_NOME, TURMA_MATERIA)
        
        self.turmas.append({"TURMA_ID": TURMA_ID, "TURMA_NOME": TURMA_NOME, "TURMA_MATERIA": TURMA_MATERIA})
        
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
        self.nome_entry.insert(0, turma["TURMA_NOME"])
        self.nome_entry.pack(anchor=tk.W, pady=(0, 20), fill=tk.X)

        tk.Label(form_frame, text="Matéria:", font=("Arial", 12),
                 bg="#f0f0f0").pack(anchor=tk.W)
        self.materia_entry = tk.Entry(form_frame, font=("Arial", 12))
        self.materia_entry.insert(0, turma["TURMA_MATERIA"])
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
            if t["TURMA_NOME"].lower() == nome.lower() and t["TURMA_ID"] != turma["TURMA_ID"]:
                messagebox.showwarning("Duplicado", "Já existe outra turma com este nome!")
                return

        self.atualizar_turma_db(turma["TURMA_ID"], nome, materia)
        
        turma["TURMA_NOME"] = nome
        turma["TURMA_MATERIA"] = materia
        
        self.abrir_tela_turma(turma)

    def confirmar_exclusao_turma(self, turma):
        resposta = messagebox.askyesno("Confirmação", 
                                       f"Tem certeza que deseja excluir a turma '{turma['TURMA_NOME']}'?")
        if resposta:
            self.excluir_turma_db(turma["TURMA_ID"])
            
            self.turmas = [t for t in self.turmas if t["TURMA_ID"] != turma["TURMA_ID"]]
            
            self.voltar_tela_principal()

    def confirmar_exclusao_aluno(self, turma):
        resposta = messagebox.askyesno("Confirmação", 
                                       f"Tem certeza que deseja excluir o aluno '{turma['ALUN_NOME']}'?")
        if resposta:
            self.excluir_aluno_db(turma["ALUN_MATRICULA"])
            
            self.turmas = [t for t in self.turmas if t["ALUN_MATRICULA"] != turma["ALUN_MATRICULA"]]
            
            self.voltar_tela_principal()
    
    def voltar_tela_principal(self):
        self.root.configure(bg="#f0f0f0")
        self.criar_tela_principal()
        
    def voltar_tela_alunos(self):
        self.root.configure(bg="#f0f0f0")
        self.criar_tela_alunos()
