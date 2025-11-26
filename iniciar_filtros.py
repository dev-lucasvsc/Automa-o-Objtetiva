import pyautogui
import time
import os
import webview
import threading
import sqlite3
import json
import atexit 

PASTA_IMAGENS = "imagens_referencia"
DB_FILE = "fornecedores.db"
CONFIG_FILE = "config.json"
TEMP_FORNECEDORES_FILE = "temp_fornecedores.json" 
CONFIANCA_PADRAO = 0.85
janela = None

def limpar_arquivo_temporario():
    if os.path.exists(TEMP_FORNECEDORES_FILE):
        try:
            os.remove(TEMP_FORNECEDORES_FILE)
            print_log(f"Arquivo temporário '{TEMP_FORNECEDORES_FILE}' removido.", "info")
        except Exception as e:
            print_log(f"Erro ao remover arquivo temporário '{TEMP_FORNECEDORES_FILE}': {e}", "error")

atexit.register(limpar_arquivo_temporario)


def print_log(message, type='step'):
    """ Imprime o log no console/terminal. """
    prefix = f"[{type.upper()}]"
    print(f"{prefix} {message}")

def finalizar_automacao(title, message, status='waiting'):
    """ Mostra uma mensagem final no modal e reativa os botões. """
    title_js = title.replace('\\', '\\\\').replace("'", "\\'").replace('"', '\\"').replace('\n', '\\n')
    message_js = message.replace('\\', '\\\\').replace("'", "\\'").replace('"', '\\"').replace('\n', '\\n')

    if janela:
        try:
            if status in ['success', 'error', 'warning'] and title != "Fornecedores Salvos":
                 limpar_arquivo_temporario()

            janela.evaluate_js(f'window.showMessage("{title_js}", "{message_js}")')
            janela.evaluate_js('window.enableControls()')
        except Exception as js_e:
            print(f"ERRO AO EXECUTAR JS (evaluate_js): {js_e}")
            print(f"Titulo original: {title}")
            print(f"Mensagem original: {message}")

def clicar_em_imagem(nome_imagem, descricao_botao, timeout=10, offset_y=0, confianca=CONFIANCA_PADRAO):
    pass
def clicar_em_checkbox_por_rotulo(nome_imagem_rotulo, descricao_checkbox, offset_x=-45, timeout=10, confianca=CONFIANCA_PADRAO):
    pass
def clicar_em_campo_por_rotulo(nome_imagem_rotulo, descricao_campo, offset_x=150, offset_y=0, timeout=10, confianca=0.9):
    pass


class Api:

    def _run_in_thread(self, target_func, *args):
        automacao_thread = threading.Thread(target=target_func, args=args, daemon=True)
        automacao_thread.start()

    def get_last_config(self):
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    print_log(f"Configuração anterior carregada de {CONFIG_FILE}", "info")
                    return config
        except Exception as e:
            print_log(f"Erro ao ler {CONFIG_FILE}: {e}", "error")
        return {}

    def save_last_config(self, config_data):
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=4)
                print_log(f"Configuração salva em {CONFIG_FILE}", "info")
        except Exception as e:
            print_log(f"Erro ao salvar {CONFIG_FILE}: {e}", "error")

    def executar_automacao_principal_tab(self, data_inicio, data_fim):
        self._run_in_thread(self._logica_automacao_principal_tab, data_inicio, data_fim)


    def _logica_automacao_principal_tab(self, data_inicio, data_fim):
        """ Lógica principal de automação via Tab, com digitação mais lenta. """
        codigos_fornecedores_para_inserir = []
        try:
            if os.path.exists(TEMP_FORNECEDORES_FILE):
                with open(TEMP_FORNECEDORES_FILE, 'r', encoding='utf-8') as f:
                    try:
                        codigos_fornecedores_para_inserir = json.load(f)
                        if not isinstance(codigos_fornecedores_para_inserir, list):
                             print_log(f"Arquivo '{TEMP_FORNECEDORES_FILE}' não contém lista. Ignorando.", "warning")
                             codigos_fornecedores_para_inserir = []
                        else:
                             print_log(f"Fornecedores carregados: {codigos_fornecedores_para_inserir}", "info")
                    except json.JSONDecodeError:
                         print_log(f"Erro ao ler JSON '{TEMP_FORNECEDORES_FILE}'. Ignorando.", "error")
                         codigos_fornecedores_para_inserir = []

            msg_confirm = ("A automação começará em 3 segundos.\n\n"
                           "Certifique-se de que a janela do sistema esteja ativa.\n\n")
            if codigos_fornecedores_para_inserir:
                msg_confirm += f"Serão inseridos {len(codigos_fornecedores_para_inserir)} fornecedor(es).\n\n"
            else:
                 msg_confirm += "Nenhum fornecedor foi selecionado para inserção.\n\n"
            msg_confirm += "Para PARAR: Mova o mouse para o canto superior esquerdo."

            confirm_result = janela.evaluate_js(f'confirm("{msg_confirm.replace(chr(10), chr(92)+chr(110))}")')

            if not confirm_result:
                print_log("Automação cancelada pelo usuário.", "warning")
                finalizar_automacao("Cancelado", "Automação cancelada pelo usuário.", "warning")
                return

            print_log(f"Iniciando automação em 3 segundos... (Datas: {data_inicio} a {data_fim})")
            time.sleep(3)
            pyautogui.FAILSAFE = True

            print_log("1. Pressionando atalho 'Alt + E + A'...")
            pyautogui.hotkey('alt', 'e', 'a')
            time.sleep(2)

            print_log("2. Inserindo a loja ('2') e Enter")
            pyautogui.write('2', interval=0.08) 
            pyautogui.press('enter')
            time.sleep(0.7)

            print_log("3. Navegando para o campo Fornecedores (Tab x1)")
            pyautogui.press('tab')
            time.sleep(0.4) 

            if codigos_fornecedores_para_inserir:
                print_log(f"   - Inserindo {len(codigos_fornecedores_para_inserir)} código(s) de fornecedor...")
                for codigo in codigos_fornecedores_para_inserir:
                    codigo_str = str(codigo).strip()
                    if codigo_str:
                        print_log(f"     - Inserindo: {codigo_str}")
                        pyautogui.write(codigo_str, interval=0.08) 
                        pyautogui.press('enter')
                        time.sleep(0.9) 
                    else:
                        print_log("     - Código vazio ignorado.", "warning")
            else:
                print_log("   - Nenhum fornecedor para inserir.")

            print_log("4. Navegando para o campo CFOP (Tab x2)")
            pyautogui.press('tab', presses=2)
            time.sleep(0.4) 

            print_log("   - Inserindo CFOP: 2102")
            pyautogui.write('2102', interval=0.08)
            pyautogui.press('enter')
            time.sleep(0.7)

            print_log("   - Inserindo CFOP: 1102")
            pyautogui.write('1102', interval=0.08)
            pyautogui.press('enter')
            time.sleep(0.7) 

            print_log(f"5. Navegando para Data Início (Tab x2) e inserindo: {data_inicio}")
            pyautogui.press('tab', presses=2)
            time.sleep(0.4) 

            pyautogui.hotkey('ctrl', 'a')
            pyautogui.press('backspace')
            pyautogui.write(data_inicio, interval=0.08)
            pyautogui.press('enter')
            time.sleep(0.7) 

            print_log(f"6. Inserindo Data de Fim: {data_fim}")
            pyautogui.hotkey('ctrl', 'a')
            pyautogui.press('backspace')
            pyautogui.write(data_fim, interval=0.08)
            pyautogui.press('enter')
            time.sleep(0.7) 

            tabs_para_checkbox = 15
            print_log(f"7. Navegando para os filtros (Tab x{tabs_para_checkbox} - *confirmar contagem*)")
            pyautogui.press('tab', presses=tabs_para_checkbox)
            time.sleep(0.5)

            print_log("8. Alterando filtros (Espaço, Tab, Espaço, Baixo, Espaço, Baixo, Espaço)")
            pyautogui.press('space'); time.sleep(0.3)
            pyautogui.press('tab'); time.sleep(0.3)
            pyautogui.press('space'); time.sleep(0.3)
            pyautogui.press('down'); time.sleep(0.3)
            pyautogui.press('space'); time.sleep(0.3)
            pyautogui.press('down'); time.sleep(0.3)
            pyautogui.press('space'); time.sleep(0.3)

            print_log("\n--- Automação Principal (via Tab) Concluída! ---", "success")
            finalizar_automacao("Sucesso", "A configuração de filtros foi concluída!", "success")

        except pyautogui.FailSafeException:
            print_log("AUTOMAÇÃO CANCELADA (FAILSAFE).", "error")
            finalizar_automacao("Cancelado", "Automação interrompida (Failsafe).", "error")
        except Exception as e:
            error_message = f"Erro inesperado durante a automação: {e}"
            print_log(error_message, "error")
            finalizar_automacao("Erro Inesperado", error_message, "error")


    def inserir_nf(self, numeros_nf):
        self._run_in_thread(self._logica_inserir_nf, numeros_nf)

    def _logica_inserir_nf(self, numeros_nf):
        print_log(f"Iniciando automação para inserir NFs: {numeros_nf}", "info")
        time.sleep(2) 
        print_log("NFs inseridas (simulação).", "success")
        finalizar_automacao("NFs Inseridas", "As Notas Fiscais foram inseridas (simulação).", "success")


    def buscar_fornecedores(self, termo_busca):
        if not termo_busca or len(termo_busca) < 2:
            return []
        print_log(f"Buscando fornecedores por: '{termo_busca}'")
        try:
            conn = sqlite3.connect(DB_FILE, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            query = "SELECT nome, codigo FROM fornecedores WHERE UPPER(nome) LIKE UPPER(?) LIMIT 50"
            termo_like = f"%{termo_busca}%"
            cursor.execute(query, (termo_like,))
            resultados = [dict(row) for row in cursor.fetchall()]
            conn.close()
            print_log(f"Encontrados {len(resultados)} fornecedores.")
            return resultados
        except sqlite3.Error as e:
            print_log(f"Erro ao buscar no SQLite: {e}", "error")
            return []

    def inserir_fornecedores(self, codigos_fornecedor):
        print_log(f"Salvando fornecedores para a próxima automação: {codigos_fornecedor}", "info")
        lista_codigos = [codigo.strip() for codigo in codigos_fornecedor.split(',') if codigo.strip()]

        if not lista_codigos:
            finalizar_automacao("Nenhum Fornecedor", "Nenhum código válido selecionado para salvar.", "warning")
            return

        try:
            limpar_arquivo_temporario() 
            with open(TEMP_FORNECEDORES_FILE, 'w', encoding='utf-8') as f:
                json.dump(lista_codigos, f)
            print_log(f"{len(lista_codigos)} código(s) salvos em '{TEMP_FORNECEDORES_FILE}'.", "success")
            finalizar_automacao("Fornecedores Salvos",
                                f"{len(lista_codigos)} código(s) de fornecedor foram salvos.\n\n"
                                f"Clique em 'INICIAR FILTROS' para aplicá-los.",
                                "success")
        except Exception as e:
            error_message = f"Erro ao salvar fornecedores: {e}"
            print_log(error_message, "error")
            finalizar_automacao("Erro ao Salvar", error_message, "error")

    def encerrar_automacao(self):
        print_log("Encerrando o assistente...", "info")
        if janela:
            janela.destroy()


if __name__ == "__main__":
    limpar_arquivo_temporario() 

    if not os.path.exists(DB_FILE):
        webview.create_window("Erro DB", html=f"<h1>Erro Crítico</h1><p>'{DB_FILE}' não encontrado!</p><p>Rode 'setup_database.py'.</p>")
        webview.start()
    elif not os.path.exists(PASTA_IMAGENS):
         os.makedirs(PASTA_IMAGENS)
         print_log(f"Pasta '{PASTA_IMAGENS}' criada.", "warning")

    api = Api()
    janela = webview.create_window(
        "Assistente de Automação",
        "web/index.html",
        js_api=api,
        width=750,
        height=800,
        resizable=True
    )
    webview.start(debug=True)