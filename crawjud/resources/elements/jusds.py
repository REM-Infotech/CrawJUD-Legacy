"""Elementos sistema JUSDS."""

from __future__ import annotations

URL_LOGIN_JUSDS = "https://infraero.jusds.com.br/JRD/openform.do?sys=JRD&action=openform&formID=464569215&firstLoad=true"
URL_CONFIRMA_LOGIN = "https://infraero.jusds.com.br/JRD/open.do?sys=JRD"

CSS_CAMPO_INPUT_LOGIN = 'input[id="WFRInput819915"]'
CSS_CAMPO_INPUT_SENHA = 'input[id="WFRInput819916"]'
XPATH_BTN_ENTRAR = '//*[@id="loginbutton"]/button'


LINK_CONSULTA_PROCESSO = "https://infraero.jusds.com.br/JRD/openform.do?sys=JRD&action=openform&formID=464569314"


XPATH_SELECT_CAMPO_BUSCA = '//*[@id="cmbPesquisa"]/select'
CSS_CAMPO_BUSCA_PROCESSO = 'input[id="WFRInput819417"]'
XPATH_BTN_ENTRA_PROCESSO = '//*[@id="isc_Vtable"]/tbody/tr/td[1]/div/img'
URL_INFORMACOES_PROCESSO = (
    "https://infraero.jusds.com.br/JRD/openform.do?{args_url}"
)

CSS_BTN_TAB_COMPROMISSOS = 'a[id="tabButton3"]'
XPATH_BTN_NOVO_COMPROMISSO = '//*[@id="TMAKERGRID6bar"]/i[@id="addButton"]'
XPATH_TABELA_COMPROMISSOS = '//*[@id="isc_4Qtable"]/tbody'
XPATH_SALVA_COMPROMISSO = '//*[@id="TMAKERGRID6bar"]/I[@id="saveButton"]'
XPATH_BTN_NEXT_PAGE = '//*[@id="TMAKERGRIDbar"]/div/ul/li[4]'
XPATH_TABLE_PRAZOS = '//table[@id="isc_34table"]/tbody'
URL_CORRETA = "https://infraero.jusds.com.br/JRD/openform.do?{url}"
