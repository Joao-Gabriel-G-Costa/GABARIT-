def adicionar_aluno_db(self, ALUN_NOME, ALUN_CPF):
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        cursor.execute("INSERT INTO ALUNO (ALUN_NOME, ALUN_CPF) VALUES (?, ?)", (ALUN_NOME, ALUN_CPF))
        TURMA_ID = cursor.lastrowid

        conn.commit()
        conn.close()

        return TURMA_ID

def cadastro_de_alunos(self, turma):
        if hasattr(self, 'main_frame'):
            self.main_frame.destroy()
            
        if self.button_frame:
            self.button_frame.destroy()
            
        self.root.configure(bg="#f0f0f0")

        self.main_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        tk.Label(self.main_frame, text="Cadastra alunos",
                 font=("Arial", 18, "bold"), bg="#f0f0f0").pack(anchor=tk.W, pady=(0, 30))

        form_frame = tk.Frame(self.main_frame, bg="#f0f0f0")
        form_frame.pack(fill=tk.BOTH, expand=True, padx=50)

        tk.Label(form_frame, text="Nome do aluno", font=("Arial", 12),
                 bg="#f0f0f0").pack(anchor=tk.W)
        self.nome_aluno_entry = tk.Entry(form_frame, font=("Arial", 12))
        self.nome_aluno_entry.pack(anchor=tk.W, pady=(0, 20), fill=tk.X)

        tk.Label(form_frame, text="CPF:", font=("Arial", 12),
                 bg="#f0f0f0").pack(anchor=tk.W)
        self.cpf_entry = tk.Entry(form_frame, font=("Arial", 12))
        self.cpf_entry.pack(anchor=tk.W, pady=(0, 30), fill=tk.X)

        button_frame = tk.Frame(form_frame, bg="#f0f0f0")
        button_frame.pack(fill=tk.X, pady=20)

        tk.Button(button_frame, text="Cancelar", font=("Arial", 12),
                  bg="#f0f0f0", width=10, command=self.voltar_tela_principal).pack(side=tk.LEFT, padx=(0, 10))

        tk.Button(button_frame, text="Adicionar", font=("Arial", 12),
                  bg="#4a6fa5", fg="white", width=10, command=self.adicionar_aluno).pack(side=tk.LEFT)

def adicionar_aluno(self):
        ALUN_NOME = self.nome_aluno_entry.get().strip()
        ALUN_CPF = self.cpf_entry.get().strip()

        if not ALUN_NOME or not ALUN_CPF:
            messagebox.showwarning("Aviso", "Por favor, preencha todos os campos!")
            return

        for ALUNO in self.alunos:
            if ALUNO["ALUN_NOME"].lower() == ALUN_NOME.lower():
                messagebox.showwarning("Duplicado", "Essa turma já foi cadastrada!")
                return

        ALUN_ID = self.adicionar_aluno_db(ALUN_NOME, ALUN_CPF)
        
        self.alunos.append({"ALUN_ID": ALUN_ID, "ALUN_NOME": ALUN_NOME, "ALUN_CPF": ALUN_CPF})
        
        self.voltar_tela_principal()

def carregar_alunos_db(self):
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        cursor.execute("SELECT ALUN_MATRICULA, ALUN_NOME, ALUN_CPF FROM TURMA ORDER BY ALUN_NOME")
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

def aluno_existe_db(self, nome, cpf):
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM ALUNO WHERE ALUN_NOME = ? OR ALUN_CPF = ?", (nome, cpf))
        exists = cursor.fetchone() is not None
        conn.close()
        return exists

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

        self.turmas = self.carregar_alunos_db()

        if not self.turmas:
            self.criar_tela_sem_alunos()
        else:
            self.exibir_lista_alunos()
            self.adicionar_aluno_botao()

def adicionar_aluno_botao(self):
        if self.button_frame:
            self.button_frame.destroy()
        self.button_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.button_frame.pack(fill=tk.X, padx=20, pady=10)

        self.add_btn = tk.Button(self.button_frame, text="+", font=("Arial", 20),
                          bg="#4a6fa5", fg="black", activebackground="#3a5a8a",
                          bd=0, width=2, height=1, command=self.cadastro_de_alunos)
        self.add_btn.pack(side=tk.RIGHT)

def exibir_lista_alunos(self):
        titulo_label = tk.Label(self.main_frame, text="Alunos",
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
