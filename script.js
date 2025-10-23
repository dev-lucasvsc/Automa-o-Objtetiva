window.addEventListener('pywebviewready', () => {

    const modal = document.getElementById('modal');
    const modalTitle = document.getElementById('modalTitle');
    const modalMessage = document.getElementById('modalMessage');
    const modalCloseButton = document.getElementById('modalCloseButton');

    const dataInicioInput = document.getElementById('data-inicio');
    const dataFimInput = document.getElementById('data-fim');
    
    const nfInput = document.getElementById('nf-input');
    const btnNfSubmit = document.getElementById('btn-nf-submit');
    
    const fornecedorSearch = document.getElementById('fornecedor-search');
    const btnFornecedorSearch = document.getElementById('btn-fornecedor-search');
    const fornecedorResults = document.getElementById('fornecedor-results');
    const fornecedorInput = document.getElementById('fornecedor-input');
    const btnFornecedorSubmit = document.getElementById('btn-fornecedor-submit');
    
    const btnStart = document.getElementById('btn-start');
    const btnEncerrar = document.getElementById('btn-encerrar');

    const allControls = [
        dataInicioInput, dataFimInput,
        nfInput, btnNfSubmit, btnStart,
        fornecedorSearch, btnFornecedorSearch, fornecedorInput, btnFornecedorSubmit
    ];

    window.showMessage = function(title, message) {
        modalTitle.textContent = title;
        modalMessage.textContent = message;
        modal.classList.add('show');
    }

    window.enableControls = function() {
        allControls.forEach(control => control.disabled = false);
    }
    
    function disableControls() {
        allControls.forEach(control => control.disabled = true);
    }
    
    function saveCurrentConfig() {
        const config = {
            data_inicio: dataInicioInput.value,
            data_fim: dataFimInput.value,
            fornecedor_codigos: fornecedorInput.value,
            nf: nfInput.value
        };
        window.pywebview.api.save_last_config(config);
    }

    function loadLastConfig() {
        window.pywebview.api.get_last_config().then(config => {
            if (config.data_inicio) {
                dataInicioInput.value = config.data_inicio;
            }
            if (config.data_fim) {
                dataFimInput.value = config.data_fim;
            }
            if (config.fornecedor_codigos) {
                fornecedorInput.value = config.fornecedor_codigos;
            }
            if (config.nf) {
                nfInput.value = config.nf;
            }
        });
    }

    modalCloseButton.addEventListener('click', () => {
        modal.classList.remove('show');
    });

    btnStart.addEventListener('click', () => {
        const dataInicio = dataInicioInput.value;
        const dataFim = dataFimInput.value;
        if (!dataInicio || !dataFim) {
            window.showMessage("Entrada Inválida", "Por favor, selecione as datas de início e fim.");
            return;
        }
        
        saveCurrentConfig(); 
        
        const dataInicioFormatada = dataInicio.split('-').reverse().join('');
        const dataFimFormatada = dataFim.split('-').reverse().join('');
        disableControls();
        pywebview.api.executar_automacao_filtros(dataInicioFormatada, dataFimFormatada);
    });

    btnFornecedorSearch.addEventListener('click', () => {
        const termo = fornecedorSearch.value;
        if (termo.length < 2) {
            window.showMessage("Busca Inválida", "Digite pelo menos 2 letras para buscar.");
            return;
        }
        fornecedorResults.innerHTML = "<small>Buscando...</small>";
        window.pywebview.api.buscar_fornecedores(termo).then(resultados => {
            renderizarResultadosFornecedor(resultados);
        });
    });
    
    fornecedorSearch.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            btnFornecedorSearch.click();
        }
    });

    function renderizarResultadosFornecedor(resultados) {
        if (!resultados || resultados.length === 0) {
            fornecedorResults.innerHTML = "<small>Nenhum fornecedor encontrado.</small>";
            return;
        }
        fornecedorResults.innerHTML = ""; 
        
        const codigosJaSelecionados = fornecedorInput.value.split(',').map(s => s.trim());

        resultados.forEach(fornecedor => {
            const div = document.createElement('div');
            div.className = 'result-item';
            
            const input = document.createElement('input');
            input.type = 'checkbox';
            input.id = `forn-${fornecedor.codigo}`;
            input.dataset.codigo = fornecedor.codigo;
            
            if (codigosJaSelecionados.includes(fornecedor.codigo)) {
                input.checked = true;
            }

            const label = document.createElement('label');
            label.htmlFor = `forn-${fornecedor.codigo}`;
            label.textContent = `${fornecedor.nome} (Cód: ${fornecedor.codigo})`;
            
            input.addEventListener('change', atualizarInputFornecedores);
            
            div.appendChild(input);
            div.appendChild(label);
            fornecedorResults.appendChild(div);
        });
    }

    function atualizarInputFornecedores() {
        const checkboxesMarcados = fornecedorResults.querySelectorAll('input[type="checkbox"]:checked');
        const codigos = [];
        
        checkboxesMarcados.forEach(cb => {
            codigos.push(cb.dataset.codigo);
        });
        
        fornecedorInput.value = codigos.join(', ');
    }
    
    btnFornecedorSubmit.addEventListener('click', () => {
        const codigos = fornecedorInput.value;
        if (!codigos) {
            window.showMessage("Entrada Inválida", "Nenhum código de fornecedor selecionado.");
            return;
        }
        
        saveCurrentConfig(); 
        
        disableControls();
        pywebview.api.inserir_fornecedores(codigos);
    });

    btnNfSubmit.addEventListener('click', () => {
        const nfs = nfInput.value;
        if (!nfs) {
            window.showMessage("Entrada Inválida", "Digite os números das NFs.");
            return;
        }
        
        saveCurrentConfig(); 
        
        disableControls();
        pywebview.api.inserir_nf(nfs);
    });
    
    btnEncerrar.addEventListener('click', () => {
        pywebview.api.encerrar_automacao();
    });

    loadLastConfig(); 

});