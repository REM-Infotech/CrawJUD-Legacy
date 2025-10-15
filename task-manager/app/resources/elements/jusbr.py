"""Elementos para robôs do Jus.Br."""

url_jusbr = "https://www.jus.br"

url_consultaprocesso = "https://portaldeservicos.pdpj.jus.br/consulta"
url_peticionamento = "https://portaldeservicos.pdpj.jus.br/peticao"
btn_login_certificado = '//*[@id="kc-form-login"]/div/div/div/div[7]/a'
input_busca_processo = 'input[name="numeroProcesso"]'
text_info = '//*[@id="lista_processo"]/div/app-lista-processo/div[1]/div/div/app-alert-card/mat-card/p'

table_processo = 'mat-table[role="table"]'
tag_rows_table = "mat-row"
btn_acao = 'button[id="botao-acao"]'

campo_tipo_protocolo = 'mat-select[formcontrolname="idTipoDocumento"]'
tipos_protocolos = '//*[@id="mat-select-0-panel"]/mat-option'
campo_arquivo_principal = (
    '//*[@id="document_list_upload"]/div[1]/div/custom-file-upload/input'
)

campo_tipo_documento = 'mat-select[id="mat-select-2"]'
options_tipo_documento = '//*[@id="mat-select-2-panel"]/mat-option'
