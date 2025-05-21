import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import random

DB_FILE = "BANCOGABARIBOT.db"

class Provas:
    def __init__(self, root, voltar_turma):
        self.root = root
        self.voltar_turma = voltar_turma
        self.questoes_criadas = []
        self.questoes_selecionadas = []
        
        try:
            self.setup_ui()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao criar a interface: {e}")
        
        self.conn = sqlite3.connect('banco_provas.db')
        self.cursor = self.conn.cursor()
        
        #self.cursor.execute('''
        #    CREATE TABLE IF NOT EXISTS PROVA (
        #        PROVA_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        #        ENUNCIADO TEXT NOT NULL,
        #        CORRETA TEXT NOT NULL,
        #        ALTERN1 TEXT NOT NULL,
        #        ALTERN2 TEXT NOT NULL,
        #        ALTERN3 TEXT NOT NULL,
        #        ALTERN4 TEXT NOT NULL
        #    )
        #''')
        # Criar a tabela PROVA_COMPLETA para armazenar provas geradas
        #self.cursor.execute('''
        #    CREATE TABLE IF NOT EXISTS PROVA_COMPLETA (
        #        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        #        NOME TEXT NOT NULL,
        #        DATA_CRIACAO TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        #    )
        #''')
        # Criar tabela para relacionar PROVA_COMPLETA com questões (PROVA)
        #self.cursor.execute('''
        #    CREATE TABLE IF NOT EXISTS PROVA_QUESTOES (
        #        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        #        PROVA_COMPLETA_ID INTEGER,
        #        PROVA_ID INTEGER,
        #        ORDEM INTEGER,
        #        FOREIGN KEY (PROVA_COMPLETA_ID) REFERENCES PROVA_COMPLETA (ID),
        #        FOREIGN KEY (PROVA_ID) REFERENCES PROVA (PROVA_ID)
        #    )
        #''')
        #criei um novo banco pq achei mais facil de manipular como eu criei um novo arquivo,
        #mas daq um tempo eu tento conectar no normal mesmo
        
        self.conn.commit()
        
        self.carregar_questoes()  
        self.setup_ui() 
    
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
        
    def salvar_questao(self):
        enunciado = self.enunciado_text.get("1.0", tk.END).strip()
        correta = self.correta_entry.get().strip()
        altern1 = self.altern1_entry.get().strip()
        altern2 = self.altern2_entry.get().strip()
        altern3 = self.altern3_entry.get().strip()
        altern4 = self.altern4_entry.get().strip()
        
        if not all([enunciado, correta, altern1, altern2, altern3, altern4]):
            messagebox.showerror("Erro", "Todos os campos são obrigatórios!")
            return
        
        try:
            self.cursor.execute('''
                INSERT INTO PROVA (ENUNCIADO, CORRETA, ALTERN1, ALTERN2, ALTERN3, ALTERN4)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (enunciado, correta, altern1, altern2, altern3, altern4))
            
            self.conn.commit()
            
            questao_id = self.cursor.lastrowid
            self.questoes_criadas.append({
                'id': questao_id,
                'enunciado': enunciado,
                'correta': correta,
                'altern1': altern1,
                'altern2': altern2,
                'altern3': altern3,
                'altern4': altern4
            })
            
            self.tree.insert("", tk.END, values=(questao_id, enunciado[:50] + "..." if len(enunciado) > 50 else enunciado))
            
            # Limpar campos
            self.enunciado_text.delete("1.0", tk.END)
            self.correta_entry.delete(0, tk.END)
            self.altern1_entry.delete(0, tk.END)
            self.altern2_entry.delete(0, tk.END)
            self.altern3_entry.delete(0, tk.END)
            self.altern4_entry.delete(0, tk.END)
            
            messagebox.showinfo("Sucesso", "Questão salva com sucesso!")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar questão: {str(e)}")
    
    def carregar_questoes(self):
        try:
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            self.cursor.execute("SELECT PROVA_ID, ENUNCIADO FROM PROVA")
            questoes = self.cursor.fetchall()
            
            for questao in questoes:
                questao_id, enunciado = questao
                self.tree.insert("", tk.END, values=(questao_id, enunciado[:50] + "..." if len(enunciado) > 50 else enunciado))
            
            self.cursor.execute("SELECT * FROM PROVA")
            self.questoes_criadas = []
            for q in self.cursor.fetchall():
                self.questoes_criadas.append({
                    'id': q[0],
                    'enunciado': q[1],
                    'correta': q[2],
                    'altern1': q[3],
                    'altern2': q[4],
                    'altern3': q[5],
                    'altern4': q[6]
                })
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar questões: {str(e)}")
    
    def visualizar_questao(self, event):
        item_id = self.tree.selection()[0]
        questao_id = self.tree.item(item_id, "values")[0]
        
        for questao in self.questoes_criadas:
            if str(questao['id']) == str(questao_id):
                janela = tk.Toplevel(self.root)
                janela.title("Detalhes da Questão")
                janela.geometry("600x400")
                
                frame = ttk.Frame(janela, padding="20")
                frame.pack(fill=tk.BOTH, expand=True)
                
                ttk.Label(frame, text="Enunciado:", font=("", 12, "bold")).grid(row=0, column=0, sticky="w", pady=5)
                ttk.Label(frame, text=questao['enunciado'], wraplength=550).grid(row=0, column=1, sticky="w", pady=5)
                
                ttk.Label(frame, text="Alternativa Correta:", font=("", 12, "bold")).grid(row=1, column=0, sticky="w", pady=5)
                ttk.Label(frame, text=questao['correta'], wraplength=550).grid(row=1, column=1, sticky="w", pady=5)
                
                ttk.Label(frame, text="Alternativa 1:", font=("", 12, "bold")).grid(row=2, column=0, sticky="w", pady=5)
                ttk.Label(frame, text=questao['altern1'], wraplength=550).grid(row=2, column=1, sticky="w", pady=5)
                
                ttk.Label(frame, text="Alternativa 2:", font=("", 12, "bold")).grid(row=3, column=0, sticky="w", pady=5)
                ttk.Label(frame, text=questao['altern2'], wraplength=550).grid(row=3, column=1, sticky="w", pady=5)
                
                ttk.Label(frame, text="Alternativa 3:", font=("", 12, "bold")).grid(row=4, column=0, sticky="w", pady=5)
                ttk.Label(frame, text=questao['altern3'], wraplength=550).grid(row=4, column=1, sticky="w", pady=5)
                
                ttk.Label(frame, text="Alternativa 4:", font=("", 12, "bold")).grid(row=5, column=0, sticky="w", pady=5)
                ttk.Label(frame, text=questao['altern4'], wraplength=550).grid(row=5, column=1, sticky="w", pady=5)
                
                frame.columnconfigure(1, weight=1)
                
                ttk.Button(frame, text="Fechar", command=janela.destroy).grid(row=6, column=0, columnspan=2, pady=10)
                
                break
    
    def adicionar_questao_prova(self):
        if len(self.questoes_selecionadas) >= 10:
            messagebox.showerror("Erro", "Você já selecionou 10 questões!")
            return
        
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showerror("Erro", "Selecione uma questão para adicionar à prova!")
            return
        
        item_id = selected_items[0]
        questao_id = self.tree.item(item_id, "values")[0]
        questao_enunciado = self.tree.item(item_id, "values")[1]
        
        for q in self.questoes_selecionadas:
            if str(q['id']) == str(questao_id):
                messagebox.showerror("Erro", "Esta questão já foi adicionada à prova!")
                return
        
        for questao in self.questoes_criadas:
            if str(questao['id']) == str(questao_id):
                self.questoes_selecionadas.append(questao)
                
                self.tree_selecao.insert("", tk.END, values=(questao_id, questao_enunciado))
                
                num_selecionadas = len(self.questoes_selecionadas)
                messagebox.showinfo("Seleção", f"Questão adicionada à prova! ({num_selecionadas}/10)")
                
                break
    
    def remover_questao_prova(self):
        selected_items = self.tree_selecao.selection()
        if not selected_items:
            messagebox.showerror("Erro", "Selecione uma questão para remover da prova!")
            return
        
        item_id = selected_items[0]
        questao_id = self.tree_selecao.item(item_id, "values")[0]
        
        self.questoes_selecionadas = [q for q in self.questoes_selecionadas if str(q['id']) != str(questao_id)]
        
        self.tree_selecao.delete(item_id)
        
        num_selecionadas = len(self.questoes_selecionadas)
        messagebox.showinfo("Seleção", f"Questão removida da prova! ({num_selecionadas}/10)")
    
    def criar_prova(self):
        if len(self.questoes_selecionadas) != 10:
            messagebox.showerror("Erro", f"Você precisa selecionar exatamente 10 questões! (Atual: {len(self.questoes_selecionadas)})")
            return
        
        nome_prova = self.nome_prova_entry.get().strip()
        if not nome_prova:
            messagebox.showerror("Erro", "Informe um nome para a prova!")
            return
        
        try:
            self.cursor.execute('''
                INSERT INTO PROVA_COMPLETA (NOME)
                VALUES (?)
            ''', (nome_prova,))
            
            prova_completa_id = self.cursor.lastrowid
            
            # Embaralhar as questões para criar uma ordem aleatória
            questoes_embaralhadas = list(self.questoes_selecionadas)
            random.shuffle(questoes_embaralhadas)
            
            # Associar as questões à prova com a ordem definida
            for i, questao in enumerate(questoes_embaralhadas):
                self.cursor.execute('''
                    INSERT INTO PROVA_QUESTOES (PROVA_COMPLETA_ID, PROVA_ID, ORDEM)
                    VALUES (?, ?, ?)
                ''', (prova_completa_id, questao['id'], i+1))
            
            self.conn.commit()
            
            self.questoes_selecionadas = []
            for item in self.tree_selecao.get_children():
                self.tree_selecao.delete(item)
            
            self.nome_prova_entry.delete(0, tk.END)
            
            messagebox.showinfo("Sucesso", f"Prova '{nome_prova}' criada com sucesso!")
            
            if messagebox.askyesno("Visualizar Prova", "Deseja visualizar a prova criada?"):
                self.visualizar_prova(prova_completa_id, nome_prova, questoes_embaralhadas)
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao criar prova: {str(e)}")
    
    def visualizar_prova(self, prova_id, nome_prova, questoes):
        janela = tk.Toplevel(self.root)
        janela.title(f"Prova: {nome_prova}")
        janela.geometry("800x600")
        
        #essa parte do canvas esta muito bugada tem que corrigir essa função futuramente senao vai pesar muito  o codigo

        main_frame = ttk.Frame(janela)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        ttk.Label(scrollable_frame, text=f"PROVA: {nome_prova}", font=("", 16, "bold")).pack(fill=tk.X, pady=10)
        ttk.Separator(scrollable_frame).pack(fill=tk.X, pady=5)
        
        for i, questao in enumerate(questoes):
            frame_questao = ttk.LabelFrame(scrollable_frame, text=f"Questão {i+1}", padding="10")
            frame_questao.pack(fill=tk.X, padx=10, pady=5)
            
            ttk.Label(frame_questao, text=questao['enunciado'], wraplength=700).pack(anchor="w", pady=5)
            
            alternativas = [
                ('A', questao['correta']),
                ('B', questao['altern1']),
                ('C', questao['altern2']),
                ('D', questao['altern3']),
                ('E', questao['altern4'])
            ]
            
            random.shuffle(alternativas)
            
            for letra, texto in alternativas:
                ttk.Label(frame_questao, text=f"{letra}) {texto}", wraplength=700).pack(anchor="w", padx=15, pady=2)
            
            alternativa_correta = next(letra for letra, texto in alternativas if texto == questao['correta'])
            ttk.Label(frame_questao, text=f"Resposta correta: {alternativa_correta}", foreground="green").pack(anchor="e", pady=5)
        
        ttk.Button(scrollable_frame, text="Fechar", command=janela.destroy).pack(pady=20)
    
    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.close()
    
    def voltar_turma(self):
        self.root.destroy() 
        if self.voltar_turma: 
            self.voltar_turma() 
