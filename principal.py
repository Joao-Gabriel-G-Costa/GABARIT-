import tkinter as tk
from tkinter import messagebox
from contextlib import contextmanager
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

    @contextmanager
    def get_db_connection(self):
        """Gerenciador de contexto para conexões com o banco"""
        conn = None
        try:
            conn = sqlite3.connect(DB_FILE)
            conn.execute("PRAGMA foreign_keys = ON")
            yield conn
        except sqlite3.Error as e:
            messagebox.showerror("Erro no Banco", f"Erro ao conectar ao banco: {str(e)}")
            raise
        finally:
            if conn:
                conn.close()

    @contextmanager
    def get_db_cursor(self):
        """Gerenciador de contexto para cursor do banco"""
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            try:
                yield cursor
                conn.commit()
            except sqlite3.Error as e:
                conn.rollback()
                messagebox.showerror("Erro no Banco", f"Erro no banco de dados: {str(e)}")
                raise

    def inicializar_db(self):
        with self.get_db_cursor() as cursor:
            # Tabela de turmas
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS TURMA (
                TURMA_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                TURMA_NOME TEXT NOT NULL,
                TURMA_MATERIA TEXT NOT NULL
            )
            ''')
            
            # Tabela de alunos
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS ALUNO (
                ALUN_MATRICULA INTEGER PRIMARY KEY AUTOINCREMENT,
                ALUN_NOME TEXT NOT NULL,
                ALUN_CPF TEXT NOT NULL UNIQUE
            )
            ''')
            
            # Tabela de associação aluno-turma
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS ALUNO_TURMA (
                ALUN_MATRICULA INTEGER,
                TURMA_ID INTEGER,
                PRIMARY KEY (ALUN_MATRICULA, TURMA_ID),
                FOREIGN KEY (ALUN_MATRICULA) REFERENCES ALUNO(ALUN_MATRICULA) ON DELETE CASCADE,
                FOREIGN KEY (TURMA_ID) REFERENCES TURMA(TURMA_ID) ON DELETE CASCADE
            )
            ''')

    def carregar_turmas_db(self):
        with self.get_db_cursor() as cursor:
            cursor.execute("SELECT TURMA_ID, TURMA_NOME, TURMA_MATERIA FROM TURMA ORDER BY TURMA_NOME")
            return [{
                "TURMA_ID": row[0],
                "TURMA_NOME": row[1],
                "TURMA_MATERIA": row[2]
            } for row in cursor.fetchall()]

    def carregar_alunos_db(self, turma_id=None):
        with self.get_db_cursor() as cursor:
            if turma_id:
                cursor.execute('''
                    SELECT a.ALUN_MATRICULA, a.ALUN_NOME, a.ALUN_CPF 
                    FROM ALUNO a
                    JOIN ALUNO_TURMA at ON a.ALUN_MATRICULA = at.ALUN_MATRICULA
                    WHERE at.TURMA_ID = ?
                    ORDER BY a.ALUN_NOME
                ''', (turma_id,))
            else:
                cursor.execute("SELECT ALUN_MATRICULA, ALUN_NOME, ALUN_CPF FROM ALUNO ORDER BY ALUN_NOME")
                
            return [{
                "ALUN_MATRICULA": row[0],
                "ALUN_NOME": row[1], 
                "ALUN_CPF": row[2]
            } for row in cursor.fetchall()]

    def adicionar_turma_db(self, TURMA_NOME, TURMA_MATERIA):
        with self.get_db_cursor() as cursor:
            cursor.execute("INSERT INTO TURMA (TURMA_NOME, TURMA_MATERIA) VALUES (?, ?)", 
                         (TURMA_NOME, TURMA_MATERIA))
            return cursor.lastrowid

    def aluno_existe_db(self, nome, cpf):
        with self.get_db_cursor() as cursor:
            cursor.execute("SELECT 1 FROM ALUNO WHERE ALUN_NOME = ? OR ALUN_CPF = ?", (nome, cpf))
            return cursor.fetchone() is not None

    def excluir_turma_db(self, TURMA_ID):
        with self.get_db_cursor() as cursor:
            cursor.execute("DELETE FROM TURMA WHERE TURMA_ID = ?", (TURMA_ID,))

    def excluir_aluno_db(self, ALUN_MATRICULA):
        with self.get_db_cursor() as cursor:
            cursor.execute("DELETE FROM ALUNO WHERE ALUN_MATRICULA = ?", (ALUN_MATRICULA,))

    def atualizar_turma_db(self, TURMA_ID, TURMA_NOME, TURMA_MATERIA):
        with self.get_db_cursor() as cursor:
            cursor.execute("UPDATE TURMA SET TURMA_NOME = ?, TURMA_MATERIA = ? WHERE TURMA_ID = ?", 
                         (TURMA_NOME, TURMA_MATERIA, TURMA_ID))

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
            
        self.adicionar_turma_botao()

    def criar_tela_sem_turmas(self):
        center_frame = tk.Frame(self.main_frame, bg="#f0f0f0")
        center_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        tk.Label(center_frame, text="Crie uma turma para começar",
               font=("Arial", 16), bg="#f0f0f0", fg="#555555").pack(pady=20)

    def exibir_lista_turmas(self):
        titulo_label = tk.Label(self.main_frame, text="Minhas Turmas",
                              font=("Arial", 16, "bold"), bg="#f0f0f0")
        titulo_label.pack(anchor=tk.W, pady=(0, 20))

        container = tk.Frame(self.main_frame, bg="#f0f0f0")
        container.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(container, bg="#f0f0f0", highlightthickness=0)
        scrollbar = tk.Scrollbar(container, orient=tk.VERTICAL, command=canvas.yview)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        canvas.configure(yscrollcommand=scrollbar.set)

        lista_frame = tk.Frame(canvas, bg="#f0f0f0")
        canvas.create_window((0, 0), window=lista_frame, anchor="nw")

        def on_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(lista_frame, width=event.width)

        lista_frame.bind("<Configure>", on_configure)
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(lista_frame, width=e.width))

        for i, turma in enumerate(self.turmas):
            card = tk.Frame(lista_frame, bg="white", bd=1, relief=tk.SOLID, cursor="hand2")
            card.grid(row=i//3, column=i%3, padx=10, pady=10, sticky="nsew")
            card.turma_data = turma

            def make_lambda(t):
                return lambda e: self.abrir_tela_turma(t)
                
            card.bind("<Enter>", lambda e: e.widget.configure(bg="#f0f7ff"))
            card.bind("<Leave>", lambda e: e.widget.configure(bg="white"))
            card.bind("<Button-1>", make_lambda(turma))

            tk.Label(card, text=turma["TURMA_NOME"], font=("Arial", 14, "bold"),
                   bg="white", fg="#4aa6ae").pack(anchor=tk.W, padx=10, pady=(10, 5))
            tk.Label(card, text=turma["TURMA_MATERIA"], font=("Arial", 12),
                   bg="white", fg="#555555").pack(anchor=tk.W, padx=10, pady=(0, 10))

    def abrir_tela_turma(self, turma):
        self.current_turma = turma
        
        if hasattr(self, 'main_frame'):
            self.main_frame.destroy()
        if self.button_frame:
            self.button_frame.destroy()
        
        self.root.configure(bg="white")
        self.main_frame = tk.Frame(self.root, bg="white")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Cabeçalho
        header_frame = tk.Frame(self.main_frame, bg="white")
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Button(header_frame, text="←", font=("Arial", 16),
                bg="#013b50", fg="white", bd=0, 
                command=self.voltar_tela_principal).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Label(header_frame, text=turma["TURMA_NOME"], 
               font=("Arial", 18, "bold"), bg="white").pack(side=tk.LEFT)
        
        # Barra lateral
        sidebar_frame = tk.Frame(self.main_frame, bg="white", bd=1, relief=tk.SOLID, width=160)
        sidebar_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 30))
        sidebar_frame.pack_propagate(False)
        
        # Botões do menu
        botoes_menu = [
            ("Alunos", "👥", lambda: self.mostrar_alunos(turma)),
            ("Desempenho", "✓", lambda: messagebox.showinfo("Info", "Função em desenvolvimento")),
            ("Provas", "📝", lambda: self.abrir_tela_provas(turma)),
            ("Editar", "✏️", lambda: self.abrir_tela_editar_turma(turma)),
            ("Excluir", "❌", lambda: self.confirmar_exclusao_turma(turma))
        ]
        
        for texto, icone, comando in botoes_menu:
            tk.Button(sidebar_frame, text=f"{icone} {texto}", font=("Arial", 12),
                    bg="#2e828f", fg="white", bd=1, relief=tk.SOLID, anchor=tk.W,
                    command=comando).pack(fill=tk.X, pady=5, padx=2)
        
        # Área de conteúdo
        content_frame = tk.Frame(self.main_frame, bg="white")
        content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        tk.Label(content_frame, text=f" {turma['TURMA_MATERIA']}", 
               font=("Arial", 14, "bold"), bg="white").pack(anchor=tk.W, pady=(0, 20))

    def mostrar_alunos(self, turma):
        try:
            if hasattr(self, 'main_frame'):
                self.main_frame.destroy()
            if self.button_frame:
                self.button_frame.destroy()

            self.root.configure(bg="white")
            self.main_frame = tk.Frame(self.root, bg="white")
            self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

            # Cabeçalho
            header = tk.Frame(self.main_frame, bg="white")
            header.pack(fill=tk.X)

            tk.Button(header, text="← Voltar", font=("Arial", 12),
                     bg="#013b50", fg="white",
                     command=lambda: self.abrir_tela_turma(turma)).pack(side=tk.LEFT)

            tk.Label(header, text=f"Alunos da Turma: {turma['TURMA_NOME']}",
                    font=("Arial", 16, "bold"), bg="white").pack(side=tk.LEFT, padx=10)

            # Lista de alunos
            alunos = self.carregar_alunos_db(turma["TURMA_ID"])

            if not alunos:
                self.criar_tela_sem_alunos()
            else:
                for aluno in alunos:
                    frame = tk.Frame(self.main_frame, bg="#e0e0e0", bd=1, relief=tk.SOLID, padx=10, pady=5)
                    frame.pack(fill=tk.X, pady=5)

                    tk.Label(frame, text=aluno["ALUN_NOME"], font=("Arial", 12), bg="#e0e0e0").pack(side=tk.LEFT)
                    tk.Label(frame, text=f"CPF: {aluno['ALUN_CPF']}", font=("Arial", 10), bg="#e0e0e0").pack(side=tk.LEFT, padx=10)

                    tk.Button(frame, text="✏️", command=lambda a=aluno: self.abrir_tela_cadastro_aluno(a, turma)).pack(side=tk.RIGHT, padx=5)
                    tk.Button(frame, text="🗑️", command=lambda a=aluno: self.excluir_aluno_e_atualizar(a["ALUN_MATRICULA"], turma)).pack(side=tk.RIGHT, padx=5)

            self.adicionar_aluno_botao()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao carregar alunos: {str(e)}")
            self.voltar_tela_principal()

    def criar_tela_sem_alunos(self):
        center_frame = tk.Frame(self.main_frame, bg="white")
        center_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        tk.Label(center_frame, text="Registre um aluno", font=("Arial", 16), bg="white").pack(pady=20)

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

    def abrir_tela_cadastro(self):
        if hasattr(self, 'main_frame'):
            self.main_frame.destroy()
        if self.button_frame:
            self.button_frame.destroy()

        self.main_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        tk.Label(self.main_frame, text="Nova Turma", font=("Arial", 18, "bold"), bg="#f0f0f0").pack(anchor=tk.W, pady=(0, 30))

        form_frame = tk.Frame(self.main_frame, bg="#f0f0f0")
        form_frame.pack(fill=tk.BOTH, expand=True, padx=50)

        tk.Label(form_frame, text="Nome da Turma:", font=("Arial", 12), bg="#f0f0f0").pack(anchor=tk.W)
        self.nome_entry = tk.Entry(form_frame, font=("Arial", 12))
        self.nome_entry.pack(anchor=tk.W, pady=(0, 20), fill=tk.X)

        tk.Label(form_frame, text="Matéria:", font=("Arial", 12), bg="#f0f0f0").pack(anchor=tk.W)
        self.materia_entry = tk.Entry(form_frame, font=("Arial", 12))
        self.materia_entry.pack(anchor=tk.W, pady=(0, 30), fill=tk.X)

        button_frame = tk.Frame(form_frame, bg="#f0f0f0")
        button_frame.pack(fill=tk.X, pady=20)

        tk.Button(button_frame, text="Cancelar", font=("Arial", 12),
                bg="#f0f0f0", width=10, command=self.voltar_tela_principal).pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(button_frame, text="Salvar", font=("Arial", 12),
                bg="#4a6fa5", fg="white", width=10, command=self.adicionar_turma).pack(side=tk.LEFT)

    def adicionar_turma(self):
        nome = self.nome_entry.get().strip()
        materia = self.materia_entry.get().strip()

        if not nome or not materia:
            messagebox.showwarning("Aviso", "Por favor, preencha todos os campos!")
            return

        for turma in self.turmas:
            if turma["TURMA_NOME"].lower() == nome.lower():
                messagebox.showwarning("Duplicado", "Essa turma já foi cadastrada!")
                return

        try:
            turma_id = self.adicionar_turma_db(nome, materia)
            self.turmas.append({"TURMA_ID": turma_id, "TURMA_NOME": nome, "TURMA_MATERIA": materia})
            self.voltar_tela_principal()
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao adicionar turma: {str(e)}")

    def abrir_tela_editar_turma(self, turma):
        self.root.configure(bg="#f0f0f0")
        
        if hasattr(self, 'main_frame'):
            self.main_frame.destroy()
        if self.button_frame:
            self.button_frame.destroy()

        self.main_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        tk.Label(self.main_frame, text="Editar Turma", font=("Arial", 18, "bold"), bg="#f0f0f0").pack(anchor=tk.W, pady=(0, 30))

        form_frame = tk.Frame(self.main_frame, bg="#f0f0f0")
        form_frame.pack(fill=tk.BOTH, expand=True, padx=50)

        tk.Label(form_frame, text="Nome da Turma:", font=("Arial", 12), bg="#f0f0f0").pack(anchor=tk.W)
        self.nome_entry = tk.Entry(form_frame, font=("Arial", 12))
        self.nome_entry.insert(0, turma["TURMA_NOME"])
        self.nome_entry.pack(anchor=tk.W, pady=(0, 20), fill=tk.X)

        tk.Label(form_frame, text="Matéria:", font=("Arial", 12), bg="#f0f0f0").pack(anchor=tk.W)
        self.materia_entry = tk.Entry(form_frame, font=("Arial", 12))
        self.materia_entry.insert(0, turma["TURMA_MATERIA"])
        self.materia_entry.pack(anchor=tk.W, pady=(0, 30), fill=tk.X)

        button_frame = tk.Frame(form_frame, bg="#f0f0f0")
        button_frame.pack(fill=tk.X, pady=20)

        tk.Button(button_frame, text="Cancelar", font=("Arial", 12),
                bg="#f0f0f0", width=10, command=lambda: self.abrir_tela_turma(turma)).pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(button_frame, text="Salvar", font=("Arial", 12),
                bg="#4a6fa5", fg="white", width=10, command=lambda: self.salvar_edicao_turma(turma)).pack(side=tk.LEFT)

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

        try:
            self.atualizar_turma_db(turma["TURMA_ID"], nome, materia)
            turma["TURMA_NOME"] = nome
            turma["TURMA_MATERIA"] = materia
            self.abrir_tela_turma(turma)
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao atualizar turma: {str(e)}")

    def confirmar_exclusao_turma(self, turma):
        resposta = messagebox.askyesno("Confirmação", f"Tem certeza que deseja excluir a turma '{turma['TURMA_NOME']}'?")
        if resposta:
            try:
                self.excluir_turma_db(turma["TURMA_ID"])
                self.turmas = [t for t in self.turmas if t["TURMA_ID"] != turma["TURMA_ID"]]
                self.voltar_tela_principal()
            except Exception as e:
                messagebox.showerror("Erro", f"Ocorreu um erro ao excluir turma: {str(e)}")

    def cadastro_de_alunos(self, turma=None):
        if not hasattr(self, 'current_turma') or not self.current_turma:
            messagebox.showwarning("Aviso", "Selecione uma turma primeiro!")
            return
        
        if hasattr(self, 'main_frame'):
            self.main_frame.destroy()
        if self.button_frame:
            self.button_frame.destroy()

        self.main_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        frame = tk.Frame(self.main_frame, bg="white", bd=2, relief=tk.GROOVE)
        frame.pack(pady=20, padx=20)

        tk.Label(frame, text="Cadastro de Aluno", font=("Arial", 16, "bold"), bg="white").grid(row=0, column=0, columnspan=2, pady=10)

        tk.Label(frame, text="Nome:", font=("Arial", 12), bg="white").grid(row=1, column=0, padx=10, pady=5, sticky=tk.E)
        self.entry_nome = tk.Entry(frame, font=("Arial", 12))
        self.entry_nome.grid(row=1, column=1, padx=10, pady=5, sticky=tk.W+tk.E)

        tk.Label(frame, text="CPF:", font=("Arial", 12), bg="white").grid(row=2, column=0, padx=10, pady=5, sticky=tk.E)
        self.entry_cpf = tk.Entry(frame, font=("Arial", 12))
        self.entry_cpf.grid(row=2, column=1, padx=10, pady=5, sticky=tk.W+tk.E)

        button_frame = tk.Frame(frame, bg="white")
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)

        tk.Button(button_frame, text="Salvar", font=("Arial", 12),
                bg="#4CAF50", fg="white", command=self.salvar_aluno).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Voltar", font=("Arial", 12),
                bg="#f44336", fg="white", command=self.voltar_tela_principal).pack(side=tk.LEFT, padx=10)

    def salvar_aluno(self):
        nome = self.entry_nome.get().strip()
        cpf = self.entry_cpf.get().strip()

        if not nome or not cpf:
            messagebox.showwarning("Aviso", "Todos os campos são obrigatórios!")
            return

        try:
            with self.get_db_cursor() as cursor:
                # Verifica se aluno já existe
                cursor.execute("SELECT ALUN_MATRICULA FROM ALUNO WHERE ALUN_CPF = ?", (cpf,))
                aluno_existente = cursor.fetchone()
                
                if aluno_existente:
                    aluno_id = aluno_existente[0]
                    # Verifica se já está na turma atual
                    cursor.execute("SELECT 1 FROM ALUNO_TURMA WHERE ALUN_MATRICULA = ? AND TURMA_ID = ?",
                                 (aluno_id, self.current_turma["TURMA_ID"]))
                    if cursor.fetchone():
                        messagebox.showwarning("Aviso", "Este aluno já está cadastrado nesta turma!")
                        return
                else:
                    # Cadastra novo aluno
                    cursor.execute("INSERT INTO ALUNO (ALUN_NOME, ALUN_CPF) VALUES (?, ?)", (nome, cpf))
                    aluno_id = cursor.lastrowid
                
                # Associa à turma atual
                cursor.execute("INSERT INTO ALUNO_TURMA (ALUN_MATRICULA, TURMA_ID) VALUES (?, ?)",
                             (aluno_id, self.current_turma["TURMA_ID"]))
            
            messagebox.showinfo("Sucesso", "Aluno cadastrado na turma com sucesso!")
            self.mostrar_alunos(self.current_turma)
            
        except sqlite3.IntegrityError as e:
            messagebox.showerror("Erro", f"Já existe um aluno com este CPF: {str(e)}")
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro inesperado: {str(e)}")

    def abrir_tela_cadastro_aluno(self, aluno=None, turma=None):
        nova_janela = tk.Toplevel(self.root)
        nova_janela.title("Editar Aluno" if aluno else "Cadastrar Aluno")
        
        tk.Label(nova_janela, text="Nome do Aluno:").pack()
        nome_entry = tk.Entry(nova_janela, font=("Arial", 12))
        nome_entry.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(nova_janela, text="CPF do Aluno:").pack()
        cpf_entry = tk.Entry(nova_janela, font=("Arial", 12))
        cpf_entry.pack(fill=tk.X, padx=10, pady=5)

        if aluno:
            nome_entry.insert(0, aluno["ALUN_NOME"])
            cpf_entry.insert(0, aluno["ALUN_CPF"])

        def salvar():
            nome = nome_entry.get().strip()
            cpf = cpf_entry.get().strip()

            if not nome or not cpf:
                messagebox.showwarning("Aviso", "Todos os campos são obrigatórios!")
                return

            try:
                with self.get_db_cursor() as cursor:
                    if aluno:  # Modo edição
                        cursor.execute("UPDATE ALUNO SET ALUN_NOME = ?, ALUN_CPF = ? WHERE ALUN_MATRICULA = ?",
                                     (nome, cpf, aluno["ALUN_MATRICULA"]))
                    else:  # Modo cadastro
                        cursor.execute("INSERT INTO ALUNO (ALUN_NOME, ALUN_CPF) VALUES (?, ?)", (nome, cpf))
                        aluno_id = cursor.lastrowid
                        cursor.execute("INSERT INTO ALUNO_TURMA (ALUN_MATRICULA, TURMA_ID) VALUES (?, ?)",
                                     (aluno_id, turma["TURMA_ID"]))
                
                messagebox.showinfo("Sucesso", "Dados do aluno salvos com sucesso!")
                nova_janela.destroy()
                self.mostrar_alunos(turma)
            except sqlite3.IntegrityError as e:
                messagebox.showerror("Erro", f"Erro de integridade: {str(e)}")
            except Exception as e:
                messagebox.showerror("Erro", f"Ocorreu um erro: {str(e)}")

        tk.Button(nova_janela, text="Salvar", font=("Arial", 12),
                bg="#4CAF50", fg="white", command=salvar).pack(side=tk.LEFT, padx=10, pady=10)
        tk.Button(nova_janela, text="Cancelar", font=("Arial", 12),
                bg="#f44336", fg="white", command=nova_janela.destroy).pack(side=tk.RIGHT, padx=10, pady=10)

    def excluir_aluno_e_atualizar(self, matricula, turma):
        resposta = messagebox.askyesno("Confirmação", "Tem certeza que deseja excluir este aluno da turma?")
        if resposta:
            try:
                with self.get_db_cursor() as cursor:
                    # Remove a associação aluno-turma
                    cursor.execute("DELETE FROM ALUNO_TURMA WHERE ALUN_MATRICULA = ? AND TURMA_ID = ?", 
                                 (matricula, turma["TURMA_ID"]))
                    
                    # Verifica se o aluno está em outras turmas
                    cursor.execute("SELECT 1 FROM ALUNO_TURMA WHERE ALUN_MATRICULA = ?", (matricula,))
                    if not cursor.fetchone():
                        # Se não estiver em outras turmas, remove o aluno completamente
                        cursor.execute("DELETE FROM ALUNO WHERE ALUN_MATRICULA = ?", (matricula,))
                
                messagebox.showinfo("Sucesso", "Aluno removido da turma com sucesso!")
                self.mostrar_alunos(turma)
            except Exception as e:
                messagebox.showerror("Erro", f"Ocorreu um erro: {str(e)}")

    def abrir_tela_provas(self, turma):
        nova_janela = tk.Toplevel(self.root)
        nova_janela.title(f"Provas - {turma['TURMA_NOME']}")
        
        def voltar():
            nova_janela.destroy()
            self.abrir_tela_turma(turma)
            
        Provas(nova_janela, voltar)

    def voltar_tela_principal(self):
        self.root.configure(bg="#f0f0f0")
        self.criar_tela_principal()
        
    def voltar_tela_alunos(self):
        self.root.configure(bg="#f0f0f0")
        self.criar_tela_alunos()

# Inicialização da aplicação
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()