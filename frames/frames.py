import customtkinter as ctk
from PIL import Image, ImageTk
import tkinter as tk
from pathlib import Path
from frames.dados_usuario import DadosUsuario
from frames.relatorios import RelatoriosMateriais  

caminho_imagem = Path("C:/Users/Win10/Downloads/tcc/TCC 27.09/login2.png")

class Principal(ctk.CTkFrame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.usuario_atual = self.master.current_user

        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")

        self.pack(fill="both", expand=True)
        self.master.geometry("1366x768")  # Ajuste a janela para 1366x768

        header_frame = ctk.CTkFrame(self, height=80, fg_color="#ADD8E6")
        header_frame.pack(side=ctk.TOP, fill=ctk.X)

        logo_frame = ctk.CTkFrame(header_frame, fg_color="#ADD8E6")
        logo_frame.pack(side=ctk.LEFT, padx=10)

        try:
            imagem = Image.open(caminho_imagem)
            imagem_resized = imagem.resize((50, 55), Image.LANCZOS)  # Ajuste da imagem do logo
            img_tk = ImageTk.PhotoImage(imagem_resized)

            label_imagem = ctk.CTkLabel(logo_frame, image=img_tk, text="")
            label_imagem.image = img_tk
            label_imagem.pack(side=ctk.LEFT, padx=10)
        except Exception as e:
            print(f"Erro ao carregar a imagem do logo: {e}")

        titulo_label = ctk.CTkLabel(logo_frame, text="Gerenciador de Laboratórios", font=ctk.CTkFont(size=20))
        titulo_label.pack(side=ctk.LEFT, padx=10)

        icones_frame = ctk.CTkFrame(header_frame, fg_color="#ADD8E6")
        icones_frame.pack(side=ctk.RIGHT, padx=20)

        icones = [("📤", self.open_user_out), ("⚙", self.open_user_info)]
        for icone, funcao in icones:
            ctk.CTkButton(icones_frame, text=icone, width=70, height=70, fg_color="#75c3d1", corner_radius=15,
                          command=funcao, font=ctk.CTkFont(size=24)).pack(side=ctk.LEFT, padx=10)

        botoes_frame = ctk.CTkFrame(self, width=200, fg_color="#F5F5DC")
        botoes_frame.pack(side=ctk.LEFT, fill=ctk.Y, padx=10, pady=10)

        botoes = [
            ("🕗", "Horários", "#FF6347", open_verreserva),
            ("📒", "Reserva", "#862ff7", open_reservas),
            ("🚚", "Empréstimo", "#32CD32", self.open_vermateriais),
            ("💼", "Materiais", "#FFD700", open_recursos),
            ("📋", "Relatórios", "#b861c7", self.open_relatorios)  
        ]

        for icone, texto, cor, funcao in botoes:
            botao_frame = ctk.CTkFrame(botoes_frame, fg_color="transparent")
            botao_frame.pack(pady=10)

            botao = ctk.CTkButton(
                botao_frame, text=icone, width=80, height=80, font=ctk.CTkFont(size=30), fg_color=cor,
                corner_radius=15, command=funcao
            )
            botao.pack()

            rotulo = ctk.CTkLabel(botao_frame, text=texto, font=ctk.CTkFont(size=14))
            rotulo.pack(pady=3)

        conteudo_frame = ctk.CTkFrame(self, fg_color="white")
        conteudo_frame.pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True)

        self.carregar_imagem_fundo(conteudo_frame)
        conteudo_frame.bind("<Configure>", lambda event: self.carregar_imagem_fundo(conteudo_frame))

        conteudo_label = ctk.CTkLabel(conteudo_frame, text="Tela Principal", font=ctk.CTkFont(size=24))
        conteudo_label.pack(pady=20)

    def carregar_imagem_fundo(self, parent_frame):
        try:
            largura_frame = parent_frame.winfo_width()
            altura_frame = parent_frame.winfo_height()

            imagem_cubo = Image.open("C:/Users/Win10/Downloads/tcc/TCC 27.09pixelcut-export-removebg-preview.png")
            imagem_cubo_resized = imagem_cubo.resize((largura_frame, altura_frame), Image.LANCZOS)

            self.imagem_fundo = ImageTk.PhotoImage(imagem_cubo_resized)

            canvas_fundo = tk.Canvas(parent_frame, width=largura_frame, height=altura_frame)
            canvas_fundo.pack(fill=tk.BOTH, expand=True)
            canvas_fundo.create_image(0, 0, anchor=tk.NW, image=self.imagem_fundo)
            canvas_fundo.lower()

        except Exception as e:
            print(f"Erro ao carregar a imagem de fundo: {e}")

    def open_vermateriais(self):
        from frames.vermateriais import VisualizarMateriais
        janela = tk.Toplevel(self)
        janela.title("Materiais")
        janela.geometry("800x600")

        app = VisualizarMateriais(janela)
        janela.mainloop()

    def open_user_info(self):
        janela = tk.Toplevel(self)
        janela.title("Dados da Conta")
        janela.geometry("300x300")

        usuario_atual = self.usuario_atual if self.usuario_atual else "Usuário Desconhecido"
        app = DadosUsuario(janela, usuario_atual)
        app.pack(fill="both", expand=True)

    def open_user_out(self):
        janela = tk.Toplevel(self)
        janela.title("Dados da Conta")
        janela.geometry("300x300")

        nome_usuario = self.usuario_atual if self.usuario_atual else "Usuário Desconhecido"
        nome_label = ctk.CTkLabel(janela, text=f"Bem-vindo, {nome_usuario} \n\n Deseja encerrar a sessão?", font=ctk.CTkFont(size=16))
        nome_label.pack(pady=20)
        voltar_button = ctk.CTkButton(janela, text="Voltar ao Login", command=self.voltar_login)
        voltar_button.pack(pady=10)

    def voltar_login(self):
        from auth.auth_login import Login
        self.master.switch_frame(Login)

    def open_relatorios(self):
        if not hasattr(self, 'relatorios_window') or not self.relatorios_window.winfo_exists():
            self.relatorios_window = tk.Toplevel(self)
            RelatoriosMateriais(self.relatorios_window)
        else:
            self.relatorios_window.lift() 

def open_recursos():
    from frames.materiais import CadastroMateriais
    janela = tk.Toplevel()
    janela.title("Materiais")
    janela.geometry("600x500")

    app = CadastroMateriais(janela)
    janela.mainloop()

def open_reservas():
    from frames.frames_reservas import CalendarApp
    janela = tk.Toplevel()
    janela.title("Reservas")
    janela.geometry("600x500")
    usuario_atual = "Usuário Teste"
    app = CalendarApp(janela, usuario_atual)
    janela.mainloop()

def open_verreserva():
    from frames.verreserva import open_ver_reservas_window
    usuario_atual = "Usuário Teste"
    open_ver_reservas_window(None, usuario_atual)
