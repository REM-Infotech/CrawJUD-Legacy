"""Elementos sistema JUSDS."""

URL_LOGIN_JUSDS = "https://infraero.jusds.com.br/JRD/openform.do?sys=JRD&action=openform&formID=464569215&firstLoad=true"
URL_CONFIRMA_LOGIN = "https://infraero.jusds.com.br/JRD/open.do?sys=JRD"

CSS_CAMPO_INPUT_LOGIN = 'input[id="WFRInput819915"]'
CSS_CAMPO_INPUT_SENHA = 'input[id="WFRInput819916"]'
XPATH_BTN_ENTRAR = '//*[@id="loginbutton"]/button'


LINK_CONSULTA_PROCESSO = "https://infraero.jusds.com.br/JRD/openform.do?sys=JRD&action=openform&formID=464569314"


XPATH_SELECT_CAMPO_BUSCA = '//*[@id="cmbPesquisa"]/select'
CSS_CAMPO_BUSCA_PROCESSO = 'input[id="WFRInput819417"]'
XPATH_BTN_BUSCAR_PROCESSO = '//*[@id="btnPesquisa"]/button'

XPATH_LOAD_MODAL = '//*[@class="modal show d-block"]/div'
XPATH_CLOSE_MODAL = '//*[@class="modal show d-block"]/div/div/div[1]/button'

XPATH_BTN_ENTRA_PROCESSO = '//*[@id="isc_Vtable"]/tbody/tr/td[1]/div/img'
URL_INFORMACOES_PROCESSO = (
    "https://infraero.jusds.com.br/JRD/openform.do?{args_url}"
)

CSS_BTN_TAB_COMPROMISSOS = 'a[id="tabButton3"]'
XPATH_BTN_NOVO_COMPROMISSO = '//*[@id="TMAKERGRID6bar"]/i[@id="addButton"]'
XPATH_TABELA_COMPROMISSOS = '//*[@id="isc_4Qtable"]/tbody'
XPATH_SALVA_COMPROMISSO = '//*[@id="TMAKERGRID6bar"]/I[@id="saveButton"]'
XPATH_BTN_NEXT_PAGE = '//*[@id="TMAKERGRIDbar"]/div/ul/li[4]'
XPATH_TABLE_PRAZOS = '//table[contains(@id, "isc_4")]/tbody'
URL_CORRETA = "https://infraero.jusds.com.br/JRD/openform.do?{url}"

XPATH_BTN_ANEXOS = '//*[@id="tabButton6"]'
XPATH_BTN_COMPROMISSOS = '//*[@id="tabButton3"]'

XPATH_BTN_ADD_ANEXO = '//*[@id="TMAKERBUTTON"]/button'

XPATH_IFRAME_ANEXOS = '//div[@id="WFRIframeForm19"]/div/iframe'
XPATH_INPUT_TIPO_DOCUMENTO = '//input[@id="WFRInput431"]'
XPATH_BTN_AENXAR_ARQUIVO = '//*[@id="MakerButton1"]/button'

XPATH_INPUT_FILE = '//*[@id="file-input"]'

XPATH_IFRAME_UPLOAD_ANEXO = (
    '//div[contains(@id, "WFRIframeFormRuleUpload19")]/div/iframe'
)
XPATH_BTN_ENVIAR_ARQUIVO = '//*[@id="uploadButton"]'
XPATH_BTN_CLOSE_MODAL = '//*[@id="WFRIframeForm19"]/div[1]/div/a'
XPATH_BTN_SALVA_STATUS = '//div[@id="TMAKERGRID6bar"]/i[@id="saveButton"]'
