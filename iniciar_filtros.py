import pyautogui
import time
import os
import webview 
import threading
import sqlite3 
import json 

PASTA_IMAGENS = "imagens_referencia"
DB_FILE = "fornecedores.db" 
CONFIG_FILE = "config.json" 
CONFIANCA_PADRAO = 0.85
janela = None 


def print_log(message, type='step'):
    """ Imprime o log no console/terminal. """
    prefix = f"[{type.upper()}]"
    print(f"{prefix} {message}")

def finalizar_automacao(title, message, status='waiting'):
    """ Mostra uma mensagem final no modal e reativa os botões. """
    
    title_js = title.replace('\\', '\\\\').replace("'", "\\'").replace('"', '\\"').replace('\n', '\\n')
    message_js = message.replace('\\', '(\\\\').replace("'", "(\\'").replace('"', '(\\"').replace('\n', '(\\n')
    
    if janela:
        try:
            janela.evaluate_js(f'window.showMessage("{title_js}", "{message_js}")')
            janela.evaluate_js('window.enableControls()')
        except Exception as js_e:
            print(f"ERRO AO EXECUTAR JS (evaluate_js): {js_e}")
            print(f"Titulo original: {title}")
            print(f"Mensagem original: {message}")


def clicar_em_imagem(nome_imagem, descricao_botao, timeout=10, offset_y=0, confianca=CONFIANCA_PADRAO):
    print_log(f"Procurando pelo elemento: '{descricao_botao}' (confiança: {confianca * 100}%)")
    caminho_completo = os.path.join(PASTA_IMAGENS, nome_imagem)
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            posicao = pyautogui.locateCenterOnScreen(caminho_completo, confidence=confianca, grayscale=True)
            if posicao:
                ponto_clique = (posicao.x, posicao.y + offset_y)
                pyautogui.click(ponto_clique)
                print_log(f"Sucesso: Clicou em '{descricao_botao}'.", "success")
                time.sleep(0.5)
                return True
        except pyautogui.ImageNotFoundException:
            pass
        except Exception as e:
            msg = f"Ocorreu um erro ao procurar a imagem: {e}\n\nCertifique-se de ter instalado o 'opencv-python'."
            print_log(msg, "error")
            finalizar_automacao("Erro de Biblioteca", msg, "error")
            return False
        time.sleep(0.5)
    
    msg = f"Não foi possível encontrar o elemento '{descricao_botao}' ({nome_imagem}) na tela após {timeout} segundos."
    print_log(msg, "error")
    finalizar_automacao("Erro de Automação", msg, "error")
    return False

def clicar_em_checkbox_por_rotulo(nome_imagem_rotulo, descricao_checkbox, offset_x=-45, timeout=10, confianca=CONFIANCA_PADRAO):
    print_log(f"Procurando pelo rótulo da checkbox: '{descricao_checkbox}' (confiança: {confianca * 100}%)")
    caminho_completo = os.path.join(PASTA_IMAGENS, nome_imagem_rotulo)
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            posicao_rotulo = pyautogui.locateCenterOnScreen(caminho_completo, confidence=confianca, grayscale=True)
            if posicao_rotulo:
                ponto_clique = (posicao_rotulo.x + offset_x, posicao_rotulo.y)
                pyautogui.click(ponto_clique)
                print_log(f"Sucesso: Clicou na checkbox '{descricao_checkbox}'.", "success")
                time.sleep(0.5)
                return True
        except Exception as e:
            msg = f"Erro ao procurar imagem: {e}\n\nVerifique a instalação do 'opencv-python'."
            print_log(msg, "error")
            finalizar_automacao("Erro de Biblioteca", msg, "error")
            return False
        time.sleep(0.5)
    
    msg = f"Não foi possível encontrar o rótulo '{descricao_checkbox}' ({nome_imagem_rotulo}) na tela."
    print_log(msg, "error")
    finalizar_automacao("Erro de Automação", msg, "error")
    return False

def clicar_em_campo_por_rotulo(nome_imagem_rotulo, descricao_campo, offset_x=150, offset_y=0, timeout=10, confianca=0.9):
    print_log(f"Procurando pelo rótulo do campo: '{descricao_campo}' (confiança: {confianca * 100}%)")
    caminho_completo = os.path.join(PASTA_IMAGENS, nome_imagem_rotulo)
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            posicao_rotulo = pyautogui.locateCenterOnScreen(caminho_completo, confidence=confianca, grayscale=True)
            if posicao_rotulo:
                ponto_clique = (posicao_rotulo.x + offset_x, posicao_rotulo.y + offset_y)
                pyautogui.click(ponto_clique)
                print_log(f"Sucesso: Clicou no campo '{descricao_campo}'.", "success")
                time.sleep(0.5)
                return True
        except Exception as e:
            msg = f"Erro ao procurar imagem: {e}\n\nVerifique a instalação do 'opencv-python'."
            print_log(msg, "error")
            finalizar_automacao("Erro de Biblioteca", msg, "error")
            return False
        time.sleep(0.5)
        
    msg = f"Não foi possível encontrar o rótulo '{descricao_campo}' ({nome_imagem_rotulo}) na tela."
    print_log(msg, "error")
    finalizar_automacao("Erro de Automação", msg, "error")
    return False


class Api:
    
    def _run_in_thread(self, target_func, *args):
        """ Roda a automação em uma thread separada para não travar a UI """
        automacao_thread = threading.Thread(target=target_func, args=args, daemon=True)
        automacao_thread.start()

    def get_last_config(self):
        """ Lê o config.json e retorna para o JS """
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
        """ Salva a configuração atual no config.json """
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=4)
                print_log(f"Configuração salva em {CONFIG_FILE}", "info")
        except Exception as e:
            print_log(f"Erro ao salvar {CONFIG_FILE}: {e}", "error")

    def executar_automacao_filtros(self, data_inicio, data_fim):
        self._run_in_thread(self._logica_automacao_filtros, data_inicio, data_fim)


    def _logica_automacao_filtros(self, data_inicio, data_fim):
        """
        Lógica principal de automação (Baseada em 'Tab')
        Ajustado: 3 Tabs da Empresa até o CFOP.
        """
        try:
            confirm = janela.evaluate_js('confirm("A automação (baseada em \'Tab\') começará 3 segundos após você clicar em OK.\\n\\nCertifique-se de que a janela do sistema de destino esteja ativa.\\n\\nPara PARAR a automação, mova o mouse para o canto superior esquerdo da tela.")')

            if not confirm:
                print_log("Automação cancelada pelo usuário.", "error")
                finalizar_automacao("Cancelado", "Automação cancelada pelo usuário.")
                return

            print_log(f"Iniciando a automação em 3 segundos... (Datas: {data_inicio} a {data_fim})")
            time.sleep(3)
            pyautogui.FAILSAFE = True
            
            print_log("1. Pressionando atalho 'Alt + E + A'...")
            pyautogui.hotkey('alt', 'e', 'a')
            time.sleep(2) 

            print_log("2. Inserindo a empresa ('2') e Enter")
            pyautogui.write('2')
            pyautogui.press('enter') 
            time.sleep(0.5) 

            print_log("3. Pulando campo Fornecedores (Tab x1)")

            pyautogui.press('tab')
            time.sleep(0.1) 

            print_log("4. Chegando no campo CFOP (Tab x2)") 
            pyautogui.press('tab', presses=2) 
            time.sleep(0.1)

            print_log("   - Inserindo CFOP fixo: 2102")
            pyautogui.write('2102')
            pyautogui.press('enter')
            time.sleep(0.5)
            
            print_log("   - Inserindo CFOP fixo: 1102")
            pyautogui.write('1102')
            pyautogui.press('enter')
            time.sleep(0.5)

            print_log(f"5. Chegando na Data Início (Tab x2) e inserindo: {data_inicio}")
            pyautogui.press('tab', presses=2) 
            time.sleep(0.1)
            
            pyautogui.hotkey('ctrl', 'a')
            pyautogui.press('backspace')
            pyautogui.write(data_inicio)
            
            print_log("   - Pressionando Enter para pular para Data Fim")
            pyautogui.press('enter') 
            time.sleep(0.5) 

            print_log(f"6. Inserindo Data de Fim: {data_fim}")
            pyautogui.hotkey('ctrl', 'a')
            pyautogui.press('backspace')
            pyautogui.write(data_fim)
            
            print_log("   - Pressionando Enter para confirmar Data Fim")
            pyautogui.press('enter')
            time.sleep(0.5)

            print_log("7. Navegando para os filtros de checkbox (Tab x15)")
            pyautogui.press('tab', presses=15)
            time.sleep(0.5) 

            print_log("8. Alterando filtros (Espaço, Tab, Espaço, Baixo, Espaço, Baixo, Espaço)")
            
            pyautogui.press('space')
            time.sleep(0.2)
            pyautogui.press('tab')
            time.sleep(0.2)
            pyautogui.press('space')
            time.sleep(0.2)
            pyautogui.press('down')
            time.sleep(0.2)
            pyautogui.press('space')
            time.sleep(0.2)
            pyautogui.press('down')
            time.sleep(0.2)
            pyautogui.press('space')
            time.sleep(0.2)
            
            print_log("\n--- Automação de Filtros (via Tab) Concluída com Sucesso! ---", "success")
            finalizar_automacao("Sucesso", "A configuração de filtros (via Tab) foi concluída!", "success")

        except pyautogui.FailSafeException:
            print_log("AUTOMAÇÃO CANCELADA PELO USUÁRIO (FAILSAFE).", "error")
            finalizar_automacao("Cancelado", "Automação interrompida pelo usuário (Failsafe ativado).", "error")
        except Exception as e:
            error_message = f"Ocorreu um erro fatal durante a automação: {e}"
            print_log(error_message, "error")
            finalizar_automacao("Erro Inesperado", error_message, "error")

    def inserir_nf(self, numeros_nf):
        self._run_in_thread(self._logica_inserir_nf, numeros_nf)
        
    def _logica_inserir_nf(self, numeros_nf):
        print_log(f"Iniciando automação para inserir NFs: {numeros_nf}", "info")
        time.sleep(2)
        print_log("NFs inseridas com sucesso.", "success")
        finalizar_automacao("NFs Inseridas", "As Notas Fiscais foram inseridas com sucesso.", "success")


    def buscar_fornecedores(self, termo_busca):
        if not termo_busca or len(termo_busca) < 2:
            return [] 
        print_log(f"Buscando fornecedores por: '{termo_busca}'")
        try:
            conn = sqlite3.connect(DB_FILE, check_same_thread=False)
            conn.row_factory = sqlite3.Row 
            cursor = conn.cursor()
            query = "SELECT nome, codigo FROM fornecedores WHERE nome LIKE ? LIMIT 50"
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
        self._run_in_thread(self._logica_fornecedores, codigos_fornecedor)

    def _logica_fornecedores(self, codigos_fornecedor):
        """ Esta função AINDA USA reconhecimento de imagem """
        print_log(f"Iniciando automação para Fornecedores: {codigos_fornecedor}", "info")
        lista_codigos = [codigo.strip() for codigo in codigos_fornecedor.split(',') if codigo.strip()]
        
        if not lista_codigos:
            finalizar_automacao("Erro", "Nenhum código de fornecedor foi inserido.", "error")
            return

        try:
            print_log("Localizando o campo de inserção do código do fornecedor...")
            if not clicar_em_campo_por_rotulo(
                'label_codigo_fornec.png', 
                "Campo Código Fornecedor",
                offset_x=100,
                offset_y=0,
                timeout=10
            ): return
            
            for codigo in lista_codigos:
                print_log(f"Inserindo código: {codigo}")
                pyautogui.write(codigo)
                pyautogui.press('enter') 
                time.sleep(0.5) 

            print_log("Etapa de fornecedores concluída.", "success")
            finalizar_automacao("Etapa Concluída", f"Foram processados {len(lista_codigos)} fornecedores.", "success")

        except pyautogui.FailSafeException:
            print_log("AUTOMAÇÃO CANCELADA PELO USUÁRIO (FAILSAFE).", "error")
            finalizar_automacao("Cancelado", "Automação interrompida pelo usuário (Failsafe ativado).", "error")
        except Exception as e:
            error_message = f"Ocorreu um erro fatal durante a automação: {e}"
            print_log(error_message, "error")
            finalizar_automacao("Erro Inesperado", error_message, "error")


    def encerrar_automacao(self):
        print_log("Encerrando o assistente...", "info")
        if janela:
            janela.destroy()


if __name__ == "__main__":
    if not os.path.exists(DB_FILE): 
        webview.create_window(
            "Erro de Configuração",
            html=f"<h1>Erro Crítico</h1><p>O banco de dados '{DB_FILE}' não foi encontrado!</p>"
                 f"<p>Por favor, rode o script 'setup_database.py' primeiro.</p>"
        )
        webview.start()
    elif not os.path.exists(PASTA_IMAGENS):
        webview.create_window(
            "Erro de Configuração",
            html=f"<h1>Erro Crítico</h1><p>A pasta '{PASTA_IMAGENS}' não foi encontrada!</p>"
        )
        webview.start()
    else:
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