import yt_dlp
import os
import time
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from PIL import Image, ImageTk
import threading
import subprocess

# Caminho para a pasta em ProgramData
program_data_dir = r'C:\ProgramData\DMloaderYT'
if not os.path.exists(program_data_dir):
    os.makedirs(program_data_dir)

CONFIG_FILE = os.path.join(program_data_dir, 'config.txt')
TERMO_FILE = os.path.join(program_data_dir, 'termos_aceitos.txt')
TEMPLATE_NOME = '[%(uploader)s] - %(title)s.%(ext)s'

class LoggerWindow:
    def __init__(self, root):
        self.log_window = tk.Toplevel(root)
        self.log_window.title("DMLoaderYT - Log de Download")
        self.log_window.geometry("700x400")
        
        # Definir o ícone da janela de log
        try:
            self.log_window.iconbitmap(r'C:\yt\images.ico')  # Caminho do ícone
        except Exception as e:
            print(f"Erro ao carregar o ícone: {e}")

        self.text_area = scrolledtext.ScrolledText(self.log_window, wrap=tk.WORD)
        self.text_area.pack(expand=True, fill='both')

    
    def log(self, message):
        self.text_area.insert(tk.END, message + "\n")
        self.text_area.see(tk.END)
    
    def close(self):
        self.log_window.destroy()

def exibir_termos():
    if not os.path.exists(TERMO_FILE):  # Verifica se os termos já foram aceitos
        termos_texto = (
            "⚠️ **TERMO DE RESPONSABILIDADE** ⚠️\n\n"
            "Ao utilizar este programa, você concorda que é totalmente responsável pelo uso do mesmo, "
            "inclusive se baixar conteúdo protegido por direitos autorais. Não nos responsabilizamos pelo seu uso!\n\n"
            "Além disso, o programa utiliza ferramentas de terceiros:\n\n"
            " - yt-dlp (https://github.com/yt-dlp/yt-dlp)\n"
            " - ffmpeg (https://ffmpeg.org/)\n\n"
            "que são fornecidas sob suas respectivas licenças. Todos os direitos reservados aos seus criadores.\n\n"
            "Ao clicar em aceitar, você concorda com os termos!"
        )
        resposta = messagebox.askquestion(
            "Termo de Responsabilidade",
            termos_texto
        )
        if resposta == 'yes':
            with open(TERMO_FILE, 'w') as file:
                file.write('termos_aceitos')
        else:
            exit()

def obter_diretorio():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as file:
            caminho = file.read().strip()
            if os.path.exists(caminho):
                return caminho
    return definir_novo_diretorio()

def definir_novo_diretorio():
    # Remova a linha abaixo, pois não deve ser chamada antes da criação do root
    # root.iconbitmap(r'C:\yt\images.ico')  # Caminho do ícone
    
    novo_caminho = filedialog.askdirectory(title="Escolha a pasta de download", parent=root)
    
    if novo_caminho:
        with open(CONFIG_FILE, 'w') as file:
            file.write(novo_caminho)
        return novo_caminho
    return obter_diretorio()
 

def obter_url():
    url_window = tk.Toplevel(root)
    url_window.title("DMloaderYT - Link")
    url_window.iconbitmap(r'C:\yt\images.ico')
    
    # Obter a largura e altura da tela
    screen_width = url_window.winfo_screenwidth()
    screen_height = url_window.winfo_screenheight()

    # Largura e altura da janela
    window_width = 400
    window_height = 200

    # Calcular a posição para centralizar
    position_top = int((screen_height - window_height) / 2)
    position_left = int((screen_width - window_width) / 2)

    # Definir a geometria da janela para centralizá-la
    url_window.geometry(f'{window_width}x{window_height}+{position_left}+{position_top}')
    
    label = tk.Label(url_window, text="Link a ser baixado:", font=('Arial', 12), padx=10, pady=5)
    label.pack(pady=10)

    # Envolvendo o Entry em um Frame para adicionar padding
    frame_entry = tk.Frame(url_window)
    frame_entry.pack(pady=10)

    url_entry = tk.Entry(frame_entry, font=('Arial', 12), width=60)
    url_entry.pack(padx=10, pady=5)  # Padding interno para o Entry
    
    url = None

    def pegar_url():
        nonlocal url
        url = url_entry.get()
        if url:
            url_window.destroy()
        else:
            messagebox.showwarning("Aviso", "Você precisa inserir um link!")
    
    tk.Button(url_window, text="Confirmar", command=pegar_url, font=('Arial', 12)).pack(pady=10)
    
    url_window.wait_window(url_window)
    return url


def progress_hook(d):
    if d['status'] == 'downloading':
        perc = d.get('percent', 0)
        eta = d.get('eta', None)
        
        if eta is not None:
            minutos, segundos = divmod(eta, 60)
            print(f"\rTempo previsto para concluir: {minutos:02}:{segundos:02} | Concluído: {perc}% ", end="")
        else:
            print(f"\rConcluído: {perc}% | Tempo estimado desconhecido... ", end="") 
    elif d['status'] == 'finished':
        print(f"\nConcluído em {d.get('elapsed', 0):.0f} segundos.")

def baixar_conteudo(formato, codec=None, nome_funcao=""):
    url = obter_url()
    if not url:
        return
    diretorio = obter_diretorio()
    
    log_window = LoggerWindow(root)
    
    def download():
        cmd = [
            'yt-dlp',
            '-f', formato,
            '--ffmpeg-location', r'C:\ffmpeg\bin',
            '-o', os.path.join(diretorio, TEMPLATE_NOME),
            url
        ]
        if codec:
            cmd += ['--extract-audio', '--audio-format', codec, '--audio-quality', '192']
        
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, creationflags=subprocess.CREATE_NO_WINDOW)
        
        for line in process.stdout:
            log_window.log(line.strip())
        
        process.wait()
        messagebox.showinfo("Sucesso", f"Download concluído em {diretorio}!")
        log_window.close()
    
    threading.Thread(target=download, daemon=True).start()

import tkinter as tk
from tkinter import scrolledtext

def exibir_sobre():
    sobre_window = tk.Toplevel(root)
    sobre_window.title("Sobre o DMloaderYT")
    sobre_window.geometry("500x400")

    # Adicionar o ícone personalizado
    try:
        sobre_window.iconbitmap("images.ico")  # Caminho do ícone
    except:
        print("Erro ao carregar o ícone. Verifique se 'images.ico' está no diretório correto.")

    # Centralizar a janela na tela
    sobre_window.update_idletasks()
    largura = 500
    altura = 400
    largura_tela = sobre_window.winfo_screenwidth()
    altura_tela = sobre_window.winfo_screenheight()
    x = (largura_tela - largura) // 2
    y = (altura_tela - altura) // 2
    sobre_window.geometry(f"{largura}x{altura}+{x}+{y}")

    # Criar a área de texto rolável
    text_area = scrolledtext.ScrolledText(sobre_window, wrap=tk.WORD)
    text_area.pack(expand=True, fill='both')

    # Texto informativo
    sobre_texto = """
    SOBRE O DMloaderYT
    Desenvolvido por: Walter Lucas

    O DMloaderYT foi desenvolvido utilizando a linguagem Python, com a integração das ferramentas yt-dlp e ffmpeg, com o objetivo de permitir o download de vídeos e músicas da internet, oferecendo uma interface simples e eficaz para facilitar o processo.

    Registro de alterações:
        v1.0b:
            - Inclusão das funções 'Baixar Áudio MP3' e 'Baixar Vídeo MP4'.
        v1.1b:
            - Inclusão das funções 'Baixar Playlist em MP3' e 'Baixar Playlist em MP4'.
        v1.2b:
            - Inclusão da função 'Baixar Áudio WAV - Alta Qualidade'.
        v1.3b:
            - Inclusão das funções 'Alterar Pasta de Download' e 'Sobre'.
            - Ajustes na interface gráfica.
            - Inclusão de mensagens de tempo, pasta salva e retorno ao menu em 5 segundos.
            - Ajuste na configuração do Termo de Uso e função de Encerramento.
        v1.4:
            - Criação da interface gráfica (GUI).
            - Alteração do ícone do aplicativo.
            - Separação da interface de log.
    
    Direitos autorais:
        Este programa utiliza ferramentas de código aberto, cujos direitos autorais são mantidos pelos respectivos criadores:

        yt-dlp (https://github.com/yt-dlp/yt-dlp)
        ffmpeg (https://ffmpeg.org/)

    Sites suportados:
        Para consultar a lista de sites suportados pelo yt-dlp, acesse: https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md

    Licença de uso:
        Este software é disponibilizado sob a Licença MIT, permitindo que você use, modifique e distribua o código livremente. Para mais detalhes sobre a licença, consulte o arquivo LICENSE no repositório do projeto.

    """
    text_area.insert(tk.END, sobre_texto)
    text_area.config(state=tk.DISABLED)

    # Botão de fechar
    tk.Button(sobre_window, text="Fechar", command=sobre_window.destroy).pack(pady=10)


def criar_interface():
    global root
    root = tk.Tk()
    root.title("DMloaderYT")

    # Calculando as dimensões da tela e da janela para centralizá-la
    screen_width = root.winfo_screenwidth()  # Largura da tela
    screen_height = root.winfo_screenheight()  # Altura da tela
    window_width = 400  # Largura da janela
    window_height = 600  # Altura da janela
    
    # Calculando a posição central
    position_top = int((screen_height - window_height) / 2)
    position_right = int((screen_width - window_width) / 2)
    
    # Definindo a geometria da janela principal
    root.geometry(f'{window_width}x{window_height}+{position_right}+{position_top}')
    
    root.iconbitmap(r'C:\yt\images.ico')
    img = Image.open(r'C:\yt\images.ico')
    img = img.resize((100, 100), Image.Resampling.LANCZOS)
    img_tk = ImageTk.PhotoImage(img)
    
    img_label = tk.Label(root, image=img_tk)
    img_label.image = img_tk
    img_label.pack(pady=10)

    tk.Button(root, text="🎵 Baixar Playlist MP3", 
            command=lambda: (definir_novo_diretorio(), baixar_conteudo('bestaudio/best', 'mp3', "Playlist MP3")), 
            width=25, height=1, font=('Arial', 16, 'bold'), bg='#e8e8e8', fg='black', bd=2, relief='raised', activebackground='#e1dddd', activeforeground='white').pack(pady=5)

    tk.Button(root, text="🎥 Baixar Playlist MP4", 
            command=lambda: (definir_novo_diretorio(), baixar_conteudo('bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]', None, "Playlist MP4")),
            width=25, height=1, font=('Arial', 16, 'bold'), bg='#e8e8e8', fg='black', bd=2, relief='raised', activebackground='#e1dddd', activeforeground='white').pack(pady=5)

    tk.Button(root, text="🎵 Baixar Áudio MP3", 
            command=lambda: (definir_novo_diretorio(), baixar_conteudo('bestaudio/best', 'mp3', "Áudio MP3")), 
            width=25, height=1, font=('Arial', 16, 'bold'), bg='#e8e8e8', fg='black', bd=2, relief='raised', activebackground='#e1dddd', activeforeground='white').pack(pady=5)

    tk.Button(root, text="🎵 Baixar Áudio WAV", 
            command=lambda: (definir_novo_diretorio(), baixar_conteudo('bestaudio/best', 'wav', "Áudio WAV")), 
            width=25, height=1, font=('Arial', 16, 'bold'), bg='#e8e8e8', fg='black', bd=2, relief='raised', activebackground='#e1dddd', activeforeground='white').pack(pady=5)

    tk.Button(root, text="🎥 Baixar Vídeo MP4", 
            command=lambda: (definir_novo_diretorio(), baixar_conteudo('bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]', None, "Vídeo MP4")),
            width=25, height=1, font=('Arial', 16, 'bold'), bg='#e8e8e8', fg='black', bd=2, relief='raised', activebackground='#e1dddd', activeforeground='white').pack(pady=5)

    tk.Button(root, text="Sobre", command=exibir_sobre, width=25, height=1, font=('Arial', 16, 'bold'), bg='#434343', fg='white', bd=2, relief='raised', activebackground='#222222', activeforeground='white').pack(pady=5)


    # Adicionando o nome do programa e versão abaixo
    program_info_label = tk.Label(root, text="DMloaderYT - v1.4", font=('Arial', 8, 'bold'), fg='gray')
    program_info_label.pack(side=tk.BOTTOM, pady=10)

    root.protocol("WM_DELETE_WINDOW", root.quit)
    root.mainloop()

if __name__ == "__main__":
    exibir_termos()
    criar_interface()
