import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import pyautogui
import pyperclip
import time

def executar_automacao(lojas, divergencias, status, autorizado_por):
    if not messagebox.askokcancel(
        "Iniciar Automação?",
        "A automação começará 3 segundos após você clicar em OK.\n\n"
        "Certifique-se de que a janela do sistema de destino esteja ativa e em primeiro plano.\n\n"
        "Para PARAR a automação a qualquer momento, mova o mouse para o canto superior esquerdo da tela."
    ):
        print("Automação cancelada pelo usuário.")
        return

    try:
        print("Iniciando a automação em 3 segundos...")
        time.sleep(3)

        pyautogui.FAILSAFE = True

        print("1. Clicando para selecionar a NF (X:674 Y:110)")
        pyautogui.click(x=674, y=110)
        time.sleep(0.5)

        print("2. Clicando para liberar as criticas (X:39 Y:168)")
        pyautogui.click(x=39, y=168)
        time.sleep(0.5)

        print("3. Clicando em 'Sim' (X:579 Y:420)")
        pyautogui.click(x=579, y=420)
        time.sleep(0.5)

        print("4. Inserindo credenciais de ADM")
        pyautogui.click(x=639, y=290)
        pyautogui.write("1844")
        pyautogui.press("enter")
        
        time.sleep(0.5)
        
        pyautogui.write("d777777777")
        pyautogui.press("enter")

        print("Aguardando o sistema processar o login...")
        time.sleep(1.2)
        
        print("5. Colando a observação em MAIÚSCULAS (método de colagem manual)")
        
        def colar_manual(texto):
            pyperclip.copy(texto)
            time.sleep(0.2) 
            pyautogui.keyDown('ctrl')
            time.sleep(0.1)
            pyautogui.press('v')
            time.sleep(0.1)
            pyautogui.keyUp('ctrl')

        linha_loja = f"{lojas} | PRE LANÇAMENTO: LUCAS | BAIXA:"
        linha_formatada = linha_loja.upper().replace('Ç', 'C')
        colar_manual(linha_formatada)
        pyautogui.press('enter')
        pyautogui.press('enter')
        time.sleep(0.7)

        linha_divergencia = f"DIVERGENCIA: {divergencias}"
        linha_formatada = linha_divergencia.upper().replace('Ç', 'C')
        colar_manual(linha_formatada)
        pyautogui.press('enter')
        time.sleep(0.7)

        linha_status = f"STATUS: {status}"
        linha_formatada = linha_status.upper().replace('Ç', 'C')
        colar_manual(linha_formatada)
        pyautogui.press('enter')
        time.sleep(0.7)

        # Linha 4
        linha_autorizado = f"AUTORIZADO POR: {autorizado_por}"
        linha_formatada = linha_autorizado.upper().replace('Ç', 'C')
        colar_manual(linha_formatada)
        pyautogui.press('enter')
        pyautogui.press('enter')
        time.sleep(0.7)

        # Linha 5
        colar_manual("ANEXO")

        print("\n--- Automação Concluída ---")
        messagebox.showinfo("Sucesso", "A sequência de automação foi concluída com sucesso!")

    except pyautogui.FailSafeException:
        messagebox.showwarning("Cancelado", "Automação cancelada pelo usuário.")
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro durante a automação: {e}")

def processar_dados():
    lojas_selecionadas = [loja for loja, var in lojas_vars.items() if var.get()]
    divergencias_selecionadas = [div for div, var in divergencias_vars.items() if var.get()]
    status_selecionado = status_var.get()
    autorizado_por = autorizado_entry.get().strip()

    if not lojas_selecionadas:
        messagebox.showwarning("Aviso", "Selecione pelo menos uma loja.")
        return
    if not divergencias_selecionadas:
        messagebox.showwarning("Aviso", "Selecione pelo menos uma divergência.")
        return
    if not status_selecionado:
        messagebox.showwarning("Aviso", "Selecione um status.")
        return
    if not autorizado_por:
        messagebox.showwarning("Aviso", "Preencha o campo 'Autorizado por'.")
        return

    lojas_str = ", ".join(lojas_selecionadas)
    divergencias_str = ", ".join(divergencias_selecionadas)

    print("--- DADOS SELECIONADOS ---")
    print(f"Lojas: {lojas_str}")
    print(f"Divergências: {divergencias_str}")
    print(f"Status: {status_selecionado}")
    print(f"Autorizado por: {autorizado_por}")
    print("--------------------------\n")

    executar_automacao(lojas_str, divergencias_str, status_selecionado, autorizado_por)

app = tk.Tk()
app.title("Sistema de Automação de Lojas")
app.geometry("450x550")
app.resizable(False, False)

main_frame = ttk.Frame(app, padding="15")
main_frame.pack(fill=tk.BOTH, expand=True)

lojas_frame = ttk.LabelFrame(main_frame, text="1. Selecione a(s) Loja(s)", padding="10")
lojas_frame.pack(fill=tk.X, expand=True, pady=5)

lojas_disponiveis = ["OBJETIVA", "SO REPAROS", "AC COELHO", "FINITURA"]
lojas_vars = {loja: tk.BooleanVar() for loja in lojas_disponiveis}
for loja, var in lojas_vars.items():
    cb = ttk.Checkbutton(lojas_frame, text=loja, variable=var)
    cb.pack(anchor=tk.W, padx=5)

divergencia_frame = ttk.LabelFrame(main_frame, text="2. Selecione a(s) Divergência(s)", padding="10")
divergencia_frame.pack(fill=tk.X, expand=True, pady=5)

divergencias_disponiveis = ["SEM PEDIDO", "ITEM SEM PEDIDO", "PREÇO"]
divergencias_vars = {div: tk.BooleanVar() for div in divergencias_disponiveis}
for div, var in divergencias_vars.items():
    cb = ttk.Checkbutton(divergencia_frame, text=div, variable=var)
    cb.pack(anchor=tk.W, padx=5)

status_frame = ttk.LabelFrame(main_frame, text="3. Selecione o Status", padding="10")
status_frame.pack(fill=tk.X, expand=True, pady=5)

status_var = tk.StringVar()
status_opcoes = ["RESPONDIDA", "SEM RESPOSTA"]
for status in status_opcoes:
    rb = ttk.Radiobutton(status_frame, text=status, variable=status_var, value=status)
    rb.pack(anchor=tk.W, padx=5)

autorizado_frame = ttk.LabelFrame(main_frame, text="4. Autorização", padding="10")
autorizado_frame.pack(fill=tk.X, expand=True, pady=5)

autorizado_label = ttk.Label(autorizado_frame, text="Autorizado por:")
autorizado_label.pack(side=tk.LEFT, padx=(0, 10))

autorizado_entry = ttk.Entry(autorizado_frame, width=30)
autorizado_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

button_frame = ttk.Frame(main_frame, padding="10")
button_frame.pack(fill=tk.X, expand=True, side=tk.BOTTOM)

prosseguir_button = ttk.Button(
    button_frame,
    text="Prosseguir e Executar Automação",
    command=processar_dados
)
prosseguir_button.pack(fill=tk.X, ipady=5)

app.mainloop()