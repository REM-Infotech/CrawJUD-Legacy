"""Define elementos e seletores utilizados para automação no sistema Projudi.

Este módulo contém variáveis com URLs, seletores CSS e XPath para facilitar
operações automatizadas de login, busca de processos, navegação e manipulação
de documentos no Projudi.

"""

url_login = (
    "https://projudi.tjam.jus.br/projudi/usuario/logon.do?actionType=inicio"
)
# Elementos Projudi
XPATH_RADIO_POLO_PARTE = "//input[@type='radio'][following-sibling::text()[contains(., '{POLO_PARTE}')]]"
XPATH_CHECKBOX_PARTE = "//input[@type='checkbox'][following-sibling::text()[contains(., '{NOME_PARTE}')]]"
CSS_BTN_PETICIONAR = 'input[id="peticionarButton"]'
CSS_INPUT_TIPO_PROTOCOLO = 'input[id="descricaoTipoDocumento"]'
XPATH_INPUT_ARQUIVO = '//*[@id="trUploadArquivo"]/td/input'
CSS_BTN_ENTRAR_TELA_ARQUIVOS = 'input[value="Adicionar"]'
XPATH_CHECK_CONTAINS_FILES = "//td[contains(@colspan, '3')]"
CSS_TABLE_ARQUIVOS = 'table[class="resultTable"] > tbody'
CSS_SENHA_CERTIFICADO = 'input[name="senhaCertificado"]'
CSS_BTN_CONFIRMA_INCLUSAO = 'input#closeButton[value="Confirmar Inclusão"]'
CSS_BTN_CONCLUIR_MOVIMENTO = 'input#editButton[value="Concluir Movimento"]'
CSS_BTN_REMOVE_ARQUIVO = 'input[name="deleteButton"]'
# Elementos Projudi


campo_username = "#login"
campo_2_login = "#senha"  # nosec: B105
btn_entrar = "#btEntrar"
chk_login = 'iframe[name="userMainFrame"]'


INFORMACAO_PROCESSO = "table#informacoesProcessuais > tbody > tr > td > a"
# Capa
# - Primeira Instancia
info_geral_table_primeiro_grau = (
    '//div[@id="includeContent"]/fieldset/table/tbody'
)
info_processual_primeiro_grau = '//table[@id="informacoesProcessuais"]/tbody'

# - Segunta Instancia
info_geral_table_segundo_grau = '//div[@id="tabprefix0"]/fieldset/table/tbody'
info_processual_segundo_grau = (
    '//*[@id="recursoForm"]/fieldset/table[1]/tbody/tr/td[1]/table/tbody'
)

partes_projudi = '//*[@id="includeContent"]'


url_busca = (
    "https://projudi.tjam.jus.br/projudi/processo/"
    "buscaProcessosQualquerInstancia.do?actionType=pesquisar"
)
url_mesa_adv = "https://projudi.tjam.jus.br/projudi/usuario/mesaAdvogado.do?actionType=listaInicio&pageNumber=1"

btn_busca = ""
btn_aba_intimacoes = 'li[id="tabItemprefix1"]'
select_page_size_intimacoes = 'select[name="pagerConfigPageSize"]'

tab_intimacoes_script = (
    "setTab("
    "'/projudi/usuario/mesaAdvogado.do?actionType=listaInicio&pageNumber=1', "
    "'tabIntimacoes', 'prefix', 1, true)"
)

btn_partes = "#tabItemprefix2"
btn_infogeral = "#tabItemprefix0"
includecontent_capa = "includeContent"

infoproc = 'table[id="informacoesProcessuais"]'
assunto_proc = 'a[class="definitionAssuntoPrincipal"]'
resulttable = "resultTable"

select_page_size = 'select[name="pagerConfigPageSize"]'
data_inicio = 'input[id="dataInicialMovimentacaoFiltro"]'
data_fim = 'input[id="dataFinalMovimentacaoFiltro"]'
filtro = 'input[id="editButton"]'
expand_btn_projudi = 'a[href="javascript://nop/"]'

table_mov = './/tr[contains(@class, "odd") or contains(@class, "even")][not(@style="display:none;")]'

table_moves = '//div[@id="includeContent"]/table/tbody'
MOV_SEM_ARQUIVO = '//tr[(contains(@class, "even") or contains(@class, "odd")) and contains(@id, "SEMARQUIVO")][not(@style="display:none")]'
MOV_COM_ARQUIVO = '//tr[(contains(@class, "even") or contains(@class, "odd")) and not(contains(@id, "SEMARQUIVO"))][not(@style="display:none")]'


primeira_instform1 = "#informacoesProcessuais"
primeira_instform2 = "#tabprefix0 > #container > #includeContent > fieldset"

segunda_instform = "#recursoForm > fieldset"

exception_arrow = './/a[@class="arrowNextOn"]'

input_radio = "input[type='radio']"

tipo_documento = 'input[name="descricaoTipoDocumento"]'
descricao_documento = (
    "div#ajaxAuto_descricaoTipoDocumento > ul > li:nth-child(1)"
)
include_content = 'input#editButton[value="Adicionar"]'
border = 'iframe[frameborder="0"][id]'
conteudo = '//*[@id="conteudo"]'
botao_assinar = 'input[name="assinarButton"]'
botao_confirmar = 'input#closeButton[value="Confirmar Inclusão"]'
botao_concluir = 'input#editButton[value="Concluir Movimento"]'
botao_deletar = 'input[type="button"][name="deleteButton"]'
css_containerprogressbar = 'div[id="divProgressBarContainerAssinado"]'
css_divprogressbar = 'div[id="divProgressBarAssinado"]'


# Protocolo
command_select_parte_protocolo = (
    'document.getElementById("{id_radio}").removeAttribute("disabled");'
)
command_sel_parte_protocolo2 = (
    "return document.getElementById('{id_part}').checked"
)
