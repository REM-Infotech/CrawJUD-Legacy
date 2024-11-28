class PROJUDI_AM:

    url_login = "https://projudi.tjam.jus.br/projudi/usuario/logon.do?actionType=inicio"
    campo_username = "#login"
    campo_passwd = "#senha"
    btn_entrar = "#btEntrar"
    chk_login = 'iframe[name="userMainFrame"]'

    url_busca = "https://projudi.tjam.jus.br/projudi/processo/buscaProcessosQualquerInstancia.do?actionType=pesquisar"
    btn_busca = ""

    btn_partes = "#tabItemprefix2"
    btn_infogeral = "#tabItemprefix0"
    includeContent_capa = "includeContent"

    infoproc = 'table[id="informacoesProcessuais"]'
    assunto_proc = 'a[class="definitionAssuntoPrincipal"]'
    resulttable = "resultTable"

    select_page_size = 'select[name="pagerConfigPageSize"]'
    data_inicio = 'input[id="dataInicialMovimentacaoFiltro"]'
    data_fim = 'input[id="dataFinalMovimentacaoFiltro"]'
    filtro = 'input[id="editButton"]'
    element_exception = 'a[href="javascript://nop/"]'
    table_moves = './/tr[contains(@class, "odd") or contains(@class, "even")][not(@style="display:none;")]'

    exception_arrow = './/a[@class="arrowNextOn"]'

    input_radio = "input[type='radio']"

    tipo_documento = 'input[name="descricaoTipoDocumento"]'
    descricao_documento = "div#ajaxAuto_descricaoTipoDocumento > ul > li:nth-child(1)"
    includeContent = 'input#editButton[value="Adicionar"]'
    border = 'iframe[frameborder="0"][id]'
    conteudo = '//*[@id="conteudo"]'
    botao_assinar = 'input[name="assinarButton"]'
    botao_confirmar = 'input#closeButton[value="Confirmar Inclusão"]'
    botao_concluir = 'input#editButton[value="Concluir Movimento"]'
    botao_deletar = 'input[type="button"][name="deleteButton"]'
    css_containerprogressbar = 'div[id="divProgressBarContainerAssinado"]'
    css_divprogressbar = 'div[id="divProgressBarAssinado"]'
