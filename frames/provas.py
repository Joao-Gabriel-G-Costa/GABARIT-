import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import random
from datetime import datetime

DB_FILE = "BANCOGABARIBOT.db"

class Provas:
    def __init__(self, root, voltar_turma):
        self.root = root
        self.voltar_turma = voltar_turma
        self.questoes_criadas = []
        self.questoes_selecionadas = []

        try:
            self.conn = sqlite3.connect(DB_FILE)
            self.cursor = self.conn.cursor()

            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS PROVA (
                    PROVA_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    ENUNCIADO TEXT NOT NULL,
                    CORRETA TEXT NOT NULL,
                    ALTERN1 TEXT NOT NULL,
                    ALTERN2 TEXT NOT NULL,
                    ALTERN3 TEXT NOT NULL,
                    ALTERN4 TEXT NOT NULL
                )
            ''')

            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS PROVA_COMPLETA (
                    ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    NOME TEXT NOT NULL,
                    DATA_CRIACAO TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS PROVA_QUESTOES (
                    ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    PROVA_COMPLETA_ID INTEGER,
                    PROVA_ID INTEGER,
                    ORDEM INTEGER,
                    FOREIGN KEY (PROVA_COMPLETA_ID) REFERENCES PROVA_COMPLETA (ID),
                    FOREIGN KEY (PROVA_ID) REFERENCES PROVA (PROVA_ID)
                )
            ''')

            self.conn.commit()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao criar as tabelas: {e}")

        self.setup_ui()
        self.carregar_questoes()

    def setup_ui(self):
        self.root.title("Criação de Provas")
        self.root.geometry("800x600")

        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        btn_voltar = ttk.Button(main_frame, text="Voltar ao Menu", command=self.voltar_turma)
        btn_voltar.grid(row=0, column=0, sticky="w", pady=10)

        criar_frame = ttk.LabelFrame(main_frame, text="Criar Nova Questão", padding="10")
        criar_frame.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

        listar_frame = ttk.LabelFrame(main_frame, text="Questões Criadas", padding="10")
        listar_frame.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")

        prova_frame = ttk.LabelFrame(main_frame, text="Criar Prova", padding="10")
        prova_frame.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")

        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=3)
        main_frame.rowconfigure(2, weight=2)

        # Frame de criação de questões
        ttk.Label(criar_frame, text="Enunciado:").grid(row=0, column=0, sticky="w", pady=5)
        self.enunciado_text = tk.Text(criar_frame, height=5, width=40, wrap=tk.WORD)
        self.enunciado_text.grid(row=0, column=1, sticky="ew", pady=5)

        ttk.Label(criar_frame, text="Alternativa Correta:").grid(row=1, column=0, sticky="w", pady=5)
        self.correta_entry = ttk.Entry(criar_frame, width=40)
        self.correta_entry.grid(row=1, column=1, sticky="ew", pady=5)

        ttk.Label(criar_frame, text="Alternativa 1:").grid(row=2, column=0, sticky="w", pady=5)
        self.altern1_entry = ttk.Entry(criar_frame, width=40)
        self.altern1_entry.grid(row=2, column=1, sticky="ew", pady=5)

        ttk.Label(criar_frame, text="Alternativa 2:").grid(row=3, column=0, sticky="w", pady=5)
        self.altern2_entry = ttk.Entry(criar_frame, width=40)
        self.altern2_entry.grid(row=3, column=1, sticky="ew", pady=5)

        ttk.Label(criar_frame, text="Alternativa 3:").grid(row=4, column=0, sticky="w", pady=5)
        self.altern3_entry = ttk.Entry(criar_frame, width=40)
        self.altern3_entry.grid(row=4, column=1, sticky="ew", pady=5)

        ttk.Label(criar_frame, text="Alternativa 4:").grid(row=5, column=0, sticky="w", pady=5)
        self.altern4_entry = ttk.Entry(criar_frame, width=40)
        self.altern4_entry.grid(row=5, column=1, sticky="ew", pady=5)

        btn_salvar = ttk.Button(criar_frame, text="Salvar Questão", command=self.salvar_questao)
        btn_salvar.grid(row=6, column=0, columnspan=2, pady=10)

        criar_frame.columnconfigure(1, weight=1)

        # Frame de listagem de questões
        self.tree = ttk.Treeview(listar_frame, columns=("id", "enunciado"), show="headings")
        self.tree.heading("id", text="ID")
        self.tree.heading("enunciado", text="Enunciado")
        self.tree.column("id", width=50)
        self.tree.column("enunciado", width=350)
        self.tree.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(listar_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)

        listar_frame.columnconfigure(0, weight=1)
        listar_frame.rowconfigure(0, weight=1)

        # Frame de criação de prova
        ttk.Label(prova_frame, text="Nome da Prova:").grid(row=0, column=0, sticky="w", pady=5)
        self.nome_prova_entry = ttk.Entry(prova_frame, width=30)
        self.nome_prova_entry.grid(row=0, column=1, sticky="ew", pady=5)

        ttk.Label(prova_frame, text="Selecione 10 questões:").grid(row=1, column=0, sticky="nw", pady=5)

        selecao_frame = ttk.Frame(prova_frame)
        selecao_frame.grid(row=1, column=1, sticky="nsew", pady=5)

        self.tree_selecao = ttk.Treeview(selecao_frame, columns=("id", "enunciado"), show="headings", height=6)
        self.tree_selecao.heading("id", text="ID")
        self.tree_selecao.heading("enunciado", text="Enunciado")
        self.tree_selecao.column("id", width=50)
        self.tree_selecao.column("enunciado", width=350)
        self.tree_selecao.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar_selecao = ttk.Scrollbar(selecao_frame, orient=tk.VERTICAL, command=self.tree_selecao.yview)
        scrollbar_selecao.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree_selecao.configure(yscrollcommand=scrollbar_selecao.set)

        btn_frame = ttk.Frame(prova_frame)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=10)

        btn_adicionar = ttk.Button(btn_frame, text="Adicionar Questão à Prova", command=self.adicionar_questao_prova)
        btn_adicionar.pack(side=tk.LEFT, padx=5)

        btn_remover = ttk.Button(btn_frame, text="Remover Questão da Prova", command=self.remover_questao_prova)
        btn_remover.pack(side=tk.LEFT, padx=5)

        btn_criar_prova = ttk.Button(btn_frame, text="Criar Prova", command=self.criar_prova)
        btn_criar_prova.pack(side=tk.LEFT, padx=5)

        prova_frame.columnconfigure(1, weight=1)
        prova_frame.rowconfigure(1, weight=1)

        self.tree.bind("<Double-1>", self.visualizar_questao)

    def visualizar_questao(self, event):
        item = self.tree.selection()[0]
        question_id = self.tree.item(item, "values")[0]
        
        try:
            self.cursor.execute("SELECT * FROM PROVA WHERE PROVA_ID=?", (question_id,))
            questao = self.cursor.fetchone()
            
            if questao:
                messagebox.showinfo("Detalhes da Questão", 
                                  f"Enunciado: {questao[1]}\n\n"
                                  f"Alternativa Correta: {questao[2]}\n"
                                  f"Alternativa 1: {questao[3]}\n"
                                  f"Alternativa 2: {questao[4]}\n"
                                  f"Alternativa 3: {questao[5]}\n"
                                  f"Alternativa 4: {questao[6]}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao visualizar questão: {e}")

    def carregar_questoes(self):
        try:
            self.tree.delete(*self.tree.get_children())
            self.cursor.execute("SELECT PROVA_ID, ENUNCIADO FROM PROVA")
            questoes = self.cursor.fetchall()
            
            for questao in questoes:
                self.tree.insert("", tk.END, values=(questao[0], questao[1]))
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar questões: {e}")

    def salvar_questao(self):
        enunciado = self.enunciado_text.get("1.0", tk.END).strip()
        correta = self.correta_entry.get().strip()
        altern1 = self.altern1_entry.get().strip()
        altern2 = self.altern2_entry.get().strip()
        altern3 = self.altern3_entry.get().strip()
        altern4 = self.altern4_entry.get().strip()

        if not enunciado or not correta or not altern1 or not altern2 or not altern3 or not altern4:
            messagebox.showwarning("Aviso", "Todos os campos devem ser preenchidos!")
            return

        try:
            self.cursor.execute(
                "INSERT INTO PROVA (ENUNCIADO, CORRETA, ALTERN1, ALTERN2, ALTERN3, ALTERN4) VALUES (?, ?, ?, ?, ?, ?)",
                (enunciado, correta, altern1, altern2, altern3, altern4)
            )
            self.conn.commit()
            
            self.enunciado_text.delete("1.0", tk.END)
            self.correta_entry.delete(0, tk.END)
            self.altern1_entry.delete(0, tk.END)
            self.altern2_entry.delete(0, tk.END)
            self.altern3_entry.delete(0, tk.END)
            self.altern4_entry.delete(0, tk.END)
            
            messagebox.showinfo("Sucesso", "Questão salva com sucesso!")
            self.carregar_questoes()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar questão: {e}")

    def adicionar_questao_prova(self):
        if len(self.questoes_selecionadas) >= 10:
            messagebox.showwarning("Aviso", "Você já selecionou o máximo de 10 questões!")
            return
            
        try:
            item = self.tree.selection()[0]
            question_id, enunciado = self.tree.item(item, "values")
            
            if question_id not in [q[0] for q in self.questoes_selecionadas]:
                self.questoes_selecionadas.append((question_id, enunciado))
                self.tree_selecao.insert("", tk.END, values=(question_id, enunciado))
        except IndexError:
            messagebox.showwarning("Aviso", "Selecione uma questão para adicionar!")

    def remover_questao_prova(self):
        try:
            item = self.tree_selecao.selection()[0]
            question_id = self.tree_selecao.item(item, "values")[0]
            
            self.questoes_selecionadas = [q for q in self.questoes_selecionadas if q[0] != question_id]
            self.tree_selecao.delete(item)
        except IndexError:
            messagebox.showwarning("Aviso", "Selecione uma questão para remover!")

    def criar_prova(self):
        nome_prova = self.nome_prova_entry.get().strip()
        
        if not nome_prova:
            messagebox.showwarning("Aviso", "Digite um nome para a prova!")
            return
            
        if len(self.questoes_selecionadas) != 10:
            messagebox.showwarning("Aviso", "Selecione exatamente 10 questões para criar a prova!")
            return

        try:
            # Salva a prova completa
            self.cursor.execute(
                "INSERT INTO PROVA_COMPLETA (NOME) VALUES (?)",
                (nome_prova,)
            )
            prova_completa_id = self.cursor.lastrowid
            
            # Salva as questões da prova
            for i, (question_id, _) in enumerate(self.questoes_selecionadas, start=1):
                self.cursor.execute(
                    "INSERT INTO PROVA_QUESTOES (PROVA_COMPLETA_ID, PROVA_ID, ORDEM) VALUES (?, ?, ?)",
                    (prova_completa_id, question_id, i)
                )
            
            self.conn.commit()
            
            # Limpa a seleção
            self.questoes_selecionadas = []
            self.tree_selecao.delete(*self.tree_selecao.get_children())
            self.nome_prova_entry.delete(0, tk.END)
            
            messagebox.showinfo("Sucesso", "Prova criada com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao criar prova: {e}")

    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.close()