import customtkinter as ctk
from customtkinter import CTkImage
from conecta import *  
from PIL import Image, ImageTk
from pathlib import Path
import sqlite3

class Login(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        
        self.frame_esquerda = ctk.CTkFrame(self, width=300)
        self.frame_esquerda.pack(side="left", fill="both", expand=True)

        self.frame_direita = ctk.CTkFrame(self, width=300)
        self.frame_direita.pack(side="right", fill="both", expand=True)

        caminho_imagem = Path(__file__).resolve().parent.parent / "assets" / "gabarito.png"

        try:
            imagem_pil = Image.open(caminho_imagem)
            self.img_tk = CTkImage(light_image=imagem_pil, size=(650, 650))

            self.label_imagem = ctk.CTkLabel(self.frame_esquerda, image=self.img_tk, text="")
            self.label_imagem.pack(expand=True)
        except Exception as e:
            print(f"Erro ao carregar a imagem: {e}")

        self.titulo = ctk.CTkLabel(self.frame_direita, text="", font=ctk.CTkFont(size=30, weight="bold"))
        self.titulo.pack(pady=160)

        self.usuarioLabel = ctk.CTkLabel(self.frame_direita, text="Usuário",font=ctk.CTkFont(size=20))
        self.usuarioLabel.pack()

        self.usuario = ctk.CTkEntry(self.frame_direita,height=30, width=350)
        self.usuario.pack(pady=10)

        self.senhaLabel = ctk.CTkLabel(self.frame_direita, text="Senha",font=ctk.CTkFont(size=20))
        self.senhaLabel.pack()

        self.senha = ctk.CTkEntry(self.frame_direita, width=350,height=30, show="*")
        self.senha.pack(pady=10)

        self.entrar = ctk.CTkButton(self.frame_direita, text="Entrar", command=self.verificaSenha)
        self.entrar.pack(pady=10)

        self.frame_botoes = ctk.CTkFrame(self.frame_direita)
        self.frame_botoes.pack(pady=10)

        self.cadastrar = ctk.CTkButton(
            self.frame_botoes,
            text="Cadastrar",
            command=self.abrir_tela_cadastro,
            fg_color="#cfcfcf",  
            text_color="#2883F7", 
            hover_color="#e0e0e0" 
        )
        self.cadastrar.pack(side="left", padx=10)

        self.esqueci_senha = ctk.CTkButton(
            self.frame_botoes,
            text="Esqueci minha senha",
            command=self.esqueciSenha,
            fg_color="#cfcfcf",  
            text_color="#2883F7", 
            hover_color="#e0e0e0"  
        )
        self.esqueci_senha.pack(side="left", padx=5)

        self.mensagem = ctk.CTkLabel(self.frame_direita, text="")
        self.mensagem.pack()

    def verificaSenha(self):
        from principal import App
        usuario = self.usuario.get()
        senha = self.senha.get()
        try:
            conn = sqlite3.connect('BANCOGABARIBOT.db')  
            cursor = conn.cursor()

            cursor.execute("SELECT PROF_SENHA FROM PROFESSOR WHERE PROF_USU = ?", (usuario,))
            resultado = cursor.fetchone()

            if resultado and resultado[0] == senha:
                self.master.current_user = usuario  
                self.master.switch_frame(App)
            else:
                self.mensagem.configure(text="Erro na autenticação")
        except sqlite3.Error as err:
            self.mensagem.configure(text=f"Erro na autenticação: {err}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def abrir_tela_cadastro(self):
        from auth.auth_cadastro import Cadastro 
        self.master.switch_frame(Cadastro)

    def esqueciSenha(self):
        from auth.auth_esqueci_senha import EsqueciSenha  
        self.master.switch_frame(EsqueciSenha)
