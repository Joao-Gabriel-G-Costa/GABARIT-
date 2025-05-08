import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import sqlite3

DB_FILE = "gabarito.db"

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
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS turmas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            materia TEXT NOT NULL
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def carregar_turmas_db(self):
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, nome, materia FROM turmas ORDER BY nome")
        rows = cursor.fetchall()
        
        turmas = []
        for row in rows:
            turmas.append({
                "id": row[0],
                "nome": row[1],
                "materia": row[2]
            })
        
        conn.close()
        return turmas
    
    def adicionar_turma_db(self, nome, materia):
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute("INSERT INTO turmas (nome, materia) VALUES (?, ?)", (nome, materia))
        turma_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        
        return turma_id
    
    def excluir_turma_db(self, turma_id):
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM turmas WHERE id = ?", (turma_id,))
        
        conn.commit()
        conn.close()
    
    def atualizar_turma_db(self, turma_id, nome, materia):
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute("UPDATE turmas SET nome = ?, materia = ? WHERE id = ?", 
                      (nome, materia, turma_id))
        
        conn.commit()
        conn.close()

    def criar_header(self):
        self.header = tk.Frame(self.root, bg="#4a6fa5", height=60)
        self.header.pack(fill=tk.X)

        self.logo_label = tk.Label(self.header, text="Gabaritô", font=("Arial", 20, "bold"),
                                   bg="#4a6fa5", fg="white")
        self.logo_label.pack(side=tk.LEFT, padx=20)

        self.config_btn = tk.Button(self.header, text="⚙", font=("Arial", 16),
                                    bd=0, bg="#4a6fa5", fg="white", activebackground="#3a5a8a")
        self.config_btn.pack(side=tk.RIGHT, padx=10)

        self.perfil_btn = tk.Button(self.header, text="👤", font=("Arial", 16),
                                    bd=0, bg="#4a6fa5", fg="white", activebackground="#3a5a8a")
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

        lista_frame = tk.Frame(self.main_frame, bg="#f0f0f0")
        lista_frame.pack(fill=tk.BOTH, expand=True)

        row, col = 0, 0
        max_col = 3

        for turma in self.turmas:
            card = tk.Frame(lista_frame, bg="white", bd=1, relief=tk.SOLID, cursor="hand2")
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            
            card.bind("<Enter>", lambda e, c=card: c.configure(bg="#f0f7ff"))
            card.bind("<Leave>", lambda e, c=card: c.configure(bg="white"))
            card.bind("<Button-1>", lambda e, t=turma: self.abrir_tela_turma(t))
            
            nome_label = tk.Label(card, text=turma["nome"], font=("Arial", 14, "bold"),
                     bg="white", fg="#4a6fa5", cursor="hand2")
            nome_label.pack(anchor=tk.W, padx=10, pady=(10, 5))
            
            materia_label = tk.Label(card, text=turma["materia"], font=("Arial", 12),
                     bg="white", fg="#555555", cursor="hand2")
            materia_label.pack(anchor=tk.W, padx=10, pady=(0, 10))
            
            nome_label.bind("<Enter>", lambda e, c=card: c.configure(bg="#f0f7ff"))
            nome_label.bind("<Leave>", lambda e, c=card: c.configure(bg="white"))
            nome_label.bind("<Button-1>", lambda e, t=turma: self.abrir_tela_turma(t))
            
            materia_label.bind("<Enter>", lambda e, c=card: c.configure(bg="#f0f7ff"))
            materia_label.bind("<Leave>", lambda e, c=card: c.configure(bg="white"))
            materia_label.bind("<Button-1>", lambda e, t=turma: self.abrir_tela_turma(t))

            col += 1
            if col >= max_col:
                col = 0
                row += 1

        for i in range(max_col):
            lista_frame.columnconfigure(i, weight=1)
        for i in range(row + 1):
            lista_frame.rowconfigure(i, weight=1)


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
                               bg="black", fg="white", bd=0, 
                               activebackground="black", activeforeground="gray",
                               command=self.voltar_tela_principal)
        voltar_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Label(header_frame, text=turma["nome"], 
                 font=("Arial", 18, "bold"), bg="white", fg="black").pack(side=tk.LEFT)
        
        sidebar_frame = tk.Frame(self.main_frame, bg="white", bd=1, relief=tk.SOLID, width=160)
        sidebar_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))
        sidebar_frame.pack_propagate(False)  
        
        menu_buttons = [
            ("Alunos", "👥"),
            ("Desempenho", "✓"),
            ("Provas", "📝")
        ]
        
        for texto, icone in menu_buttons:
            btn = tk.Button(sidebar_frame, text=f"{icone} {texto}",
                          font=("Arial", 12), bg="white", fg="black",
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
        nome = self.nome_entry.get().strip()
        materia = self.materia_entry.get().strip()

        if not nome or not materia:
            messagebox.showwarning("Aviso", "Por favor, preencha todos os campos!")
            return

        for turma in self.turmas:
            if turma["nome"].lower() == nome.lower():
                messagebox.showwarning("Duplicado", "Essa turma já foi cadastrada!")
                return

        turma_id = self.adicionar_turma_db(nome, materia)
        
        self.turmas.append({"id": turma_id, "nome": nome, "materia": materia})
        
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


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()