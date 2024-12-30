class AME:

    # Login Elaw
    url_login = ""
    campo_username = ""
    campo_passwd = ""
    btn_entrar = ""
    chk_login = ""

    # Busca Elaw
    url_busca = ""
    btn_busca = ""

    # ANDAMENTOS
    botao_andamento = (
        'button[id="tabViewProcesso:j_id_i3_4_1_3_ae:novoAndamentoPrimeiraBtn"]'
    )
    input_data = 'input[id="j_id_2n:j_id_2r_2_9_input"]'
    inpt_ocorrencia = 'textarea[id="j_id_2n:txtOcorrenciaAndamento"]'
    inpt_obs = 'textarea[id="j_id_2n:txtObsAndamento"]'
    botao_salvar_andamento = "btnSalvarAndamentoProcesso"

    # Robô Lançar Audiências
    switch_pautaAndamento = 'a[href="#tabViewProcesso:agendamentosAndamentos"]'
    btn_NovaAudiencia = 'button[id="tabViewProcesso:novaAudienciaBtn"]'
    selectorTipoAudiencia = 'select[id="j_id_2l:comboTipoAudiencia_input"]'
    DataAudiencia = 'input[id="j_id_2l:j_id_2p_2_8_8:dataAudienciaField_input"]'
    btn_Salvar = 'button[id="btnSalvarNovaAudiencia"]'
    tablePrazos = (
        'tbody[id="tabViewProcesso:j_id_i3_4_1_3_d:dtAgendamentoResults_data"]'
    )

    tipo_polo = "".join(
        [
            'select[id="j_id_3k_1:j_id_3k_4_2_2_t_9_44_2:j_id_3k_4_2_2_t_',
            '9_44_3_1_2_2_1_1:fieldid_13755typeSelectField1CombosCombo_input"]',
        ]
    )

    # CADASTRO
    botao_novo = 'button[id="btnNovo"]'
    css_label_area = 'div[id="comboArea"]'
    elemento = 'div[id="comboArea_panel"]'
    comboAreaSub_css = 'div[id="comboAreaSub"]'
    elemento_ComboAreaSub = 'div[id="comboAreaSub_panel"]'
    css_button = 'button[id="btnContinuar"]'

    label_esfera = 'label[id="j_id_3k_1:j_id_3k_4_2_2_1_9_u_1:comboRito_label"]'

    css_esfera_judge = 'select[id="j_id_3k_1:j_id_3k_4_2_2_1_9_u_1:comboRito_input"]'
    combo_rito = 'div[id="j_id_3k_1:j_id_3k_4_2_2_1_9_u_1:comboRito_panel"]'
    estado_input = "select[id='j_id_3k_1:j_id_3k_4_2_2_1_9_u_1:comboEstadoVara_input']"
    comarca_input = (
        "select[id='j_id_3k_1:j_id_3k_4_2_2_1_9_u_1:comboComarcaVara_input']"
    )
    foro_input = "select[id='j_id_3k_1:j_id_3k_4_2_2_1_9_u_1:comboForoTribunal_input']"
    vara_input = "select[id='j_id_3k_1:j_id_3k_4_2_2_1_9_u_1:comboVara_input']"
    numero_processo = "input[id='j_id_3k_1:j_id_3k_4_2_2_2_9_f_2:txtNumeroMask']"
    empresa_input = "select[id='j_id_3k_1:comboClientProcessoParte_input']"
    tipo_empresa_input = "select[id='j_id_3k_1:j_id_3k_4_2_2_4_9_2_5_input']"
    tipo_parte_contraria_input = (
        "select[id='j_id_3k_1:j_id_3k_4_2_2_5_9_9_1:j_id_3k_4_2_2_5_9_9_4_2_m_input']"
    )
    css_table_tipo_doc = (
        'table[id="j_id_3k_1:j_id_3k_4_2_2_5_9_9_1:tipoDocumentoInput"]'
    )
    css_campo_doc = 'input[id="j_id_3k_1:j_id_3k_4_2_2_5_9_9_1:cpfCnpjInput"]'
    css_search_button = (
        'button[id="j_id_3k_1:j_id_3k_4_2_2_5_9_9_1:j_id_3k_4_2_2_5_9_9_4_2_f"]'
    )
    css_div_select_opt = 'div[id="j_id_3k_1:j_id_3k_4_2_2_9_9_44_2:j_id_3k_4_2_2_9_9_44_3_1_2_2_2_1:fieldid_9240pgTypeSelectField1CombosCombo"]'
    select_field = 'div[id="j_id_3k_1:j_id_3k_4_2_2_9_9_44_2:j_id_3k_4_2_2_9_9_44_3_1_2_2_2_1:fieldid_9240pgTypeSelectField1CombosCombo_panel"]'
    css_other_location = "".join(
        (
            'input[id="j_id_3k_1:j_id_3k_4_2_2_9_9_44_2:j_id_3k_4_2_2_9_9_44_3_1_2_2_2_1:',
            "j_id_3k_4_2_2_9_9_44_3_1_2_2_2_2_1_c:j_id_3k_4_2_2_9_9_44_3_1_2_2_2_2_1_f:0:j",
            '_id_3k_4_2_2_9_9_44_3_1_2_2_2_2_1_1f:fieldText"]',
        )
    )
    comboProcessoTipo = 'div[id="j_id_3k_1:comboProcessoTipo"]'
    filtro_processo = 'input[id="j_id_3k_1:comboProcessoTipo_filter"]'
    css_data_distribuicao = 'input[id="j_id_3k_1:dataDistribuicao_input"]'
    css_adv_responsavel = 'input[id="j_id_3k_1:autoCompleteLawyer_input"]'
    css_div_select_Adv = 'div[id="j_id_3k_1:comboAdvogadoResponsavelProcesso"]'
    css_input_select_Adv = (
        'input[id="j_id_3k_1:comboAdvogadoResponsavelProcesso_filter"]'
    )
    css_input_adv = 'input[id="j_id_3k_1:autoCompleteLawyerOutraParte_input"]'
    css_check_adv = r"#j_id_3k_1\:autoCompleteLawyerOutraParte_panel > ul > li.ui-autocomplete-item.ui-autocomplete-list-item.ui-corner-all.ui-state-highlight"
    css_valor_causa = 'input[id="j_id_3k_1:amountCase_input"]'
    escritrorio_externo = 'div[id="j_id_3k_1:comboEscritorio"]'
    combo_escritorio = 'div[id="j_id_3k_1:comboEscritorio_panel"]'
    contingencia = "select[id='j_id_3k_1:j_id_3k_4_2_2_s_9_n_1:processoContingenciaTipoCombo_input']"
    contigencia_panel = (
        'div[id="j_id_3k_1:j_id_3k_4_2_2_s_9_n_1:processoContingenciaTipoCombo_panel"]'
    )
    css_add_adv = 'button[id="j_id_3k_1:lawyerOutraParteNovoButtom"]'
    xpath = '//*[@id="j_id_3k_1:lawyerOutraParteNovoButtom_dlg"]/div[2]/iframe'
    css_naoinfomadoc = "#cpfCnpjNoGrid-lawyerOutraParte > tbody > tr > td:nth-child(1) > div > div.ui-radiobutton-box.ui-widget.ui-corner-all.ui-state-default"
    botao_continuar = 'button[id="j_id_1e"]'
    css_input_nomeadv = 'input[id="j_id_1h:j_id_1k_2_5"]'
    salvarcss = 'button[id="lawyerOutraParteButtom"]'
    parte_contraria = (
        'button[id="j_id_3k_1:j_id_3k_4_2_2_5_9_9_1:parteContrariaMainGridBtnNovo"]'
    )
    xpath_iframe = '//*[@id="j_id_3k_1:j_id_3k_4_2_2_5_9_9_1:parteContrariaMainGridBtnNovo_dlg"]/div[2]/iframe'
    cpf_cnpj = 'table[id="registrationCpfCnpjChooseGrid-"]'
    botao_radio_widget = 'div[class="ui-radiobutton ui-widget"]'
    tipo_cpf_cnpj = 'table[id="cpfCnpjTipoNoGrid-"]'
    tipo_cpf = 'input[id="j_id_19"]'
    tipo_cnpj = 'input[id="j_id_1a"]'
    botao_parte_contraria = 'button[id="j_id_1d"]'
    css_name_parte = 'input[id="j_id_1k"]'
    css_save_button = 'button[id="parteContrariaButtom"]'
    css_salvar_proc = 'button[id="btnSalvarOpen"]'
    css_t_found = (
        'table[id="j_id_3k_1:j_id_3k_4_2_2_5_9_9_1:parteContrariaSearchDisplayGrid"]'
    )
    div_messageerro_css = 'div[id="messages"]'

    # COMPLEMENTAR
    botao_editar_complementar = 'button[id="dtProcessoResults:0:btnEditar"]'
    css_input_uc = 'textarea[id="j_id_3k_1:j_id_3k_4_2_2_6_9_44_2:j_id_3k_4_2_2_6_9_44_3_1_2_2_1_1:j_id_3k_4_2_2_6_9_44_3_1_2_2_1_13"]'
    elementSelect = 'select[id="j_id_3k_1:j_id_3k_4_2_2_a_9_44_2:j_id_3k_4_2_2_a_9_44_3_1_2_2_1_1:fieldid_9241typeSelectField1CombosCombo_input"]'
    css_data_citacao = 'input[id="j_id_3k_1:dataRecebimento_input"]'
    fase_input = 'select[id="j_id_3k_1:processoFaseCombo_input"]'
    provimento_input = 'select[id="j_id_3k_1:j_id_3k_4_2_2_g_9_44_2:j_id_3k_4_2_2_g_9_44_3_1_2_2_1_1:fieldid_8401typeSelectField1CombosCombo_input"]'
    fato_gerador_input = 'select[id="j_id_3k_1:j_id_3k_4_2_2_m_9_44_2:j_id_3k_4_2_2_m_9_44_3_1_2_2_1_1:fieldid_9239typeSelectField1CombosCombo_input"]'
    input_descobjeto_css = 'textarea[id="j_id_3k_1:j_id_3k_4_2_2_l_9_44_2:j_id_3k_4_2_2_l_9_44_3_1_2_2_1_1:j_id_3k_4_2_2_l_9_44_3_1_2_2_1_13"]'
    objeto_input = 'select[id="j_id_3k_1:j_id_3k_4_2_2_n_9_44_2:j_id_3k_4_2_2_n_9_44_3_1_2_2_1_1:fieldid_8405typeSelectField1CombosCombo_input"]'

    # DOWNLOAD
    anexosbutton_css = 'a[href="#tabViewProcesso:files"]'
    css_table_doc = 'tbody[id="tabViewProcesso:gedEFileDataTable:GedEFileViewDt_data"]'
    botao_baixar = 'button[title="Baixar"]'

    # PAGAMENTOS
    valor_pagamento = 'a[href="#tabViewProcesso:processoValorPagamento"]'
    botao_novo_pagamento = (
        'button[id="tabViewProcesso:pvp-pgBotoesValoresPagamentoBtnNovo"]'
    )
    css_typeitens = (
        'div[id="processoValorPagamentoEditForm:pvp:processoValorPagamentoTipoCombo"]'
    )
    listitens_css = 'ul[id="processoValorPagamentoEditForm:pvp:processoValorPagamentoTipoCombo_items"]'
    css_element = 'input[id="processoValorPagamentoEditForm:pvp:j_id_2m_1_i_1_1_9_1f_1:processoValorRateioAmountAllDt:0:j_id_2m_1_i_1_1_9_1f_2_2_q_input"]'
    type_doc_css = 'div[id="processoValorPagamentoEditForm:pvp:j_id_2m_1_i_2_1_9_g_1:eFileTipoCombo"]'
    list_type_doc_css = 'ul[id="processoValorPagamentoEditForm:pvp:j_id_2m_1_i_2_1_9_g_1:eFileTipoCombo_items"]'
    editar_pagamento = 'input[id="processoValorPagamentoEditForm:pvp:j_id_2m_1_i_2_1_9_g_1:uploadGedEFile_input"]'
    css_div_condenacao_type = 'div[id="processoValorPagamentoEditForm:pvp:j_id_2m_1_i_3_1_9_26_1_1_1:pvpEFBtypeSelectField1CombosCombo"]'
    valor_sentenca = 'li[id="processoValorPagamentoEditForm:pvp:j_id_2m_1_i_3_1_9_26_1_1_1:pvpEFBtypeSelectField1CombosCombo_3"]'
    valor_acordao = 'li[id="processoValorPagamentoEditForm:pvp:j_id_2m_1_i_3_1_9_26_1_1_1:pvpEFBtypeSelectField1CombosCombo_1"]'
    css_desc_pgto = 'textarea[id="processoValorPagamentoEditForm:pvp:processoValorPagamentoDescription"]'
    css_data = 'input[id="processoValorPagamentoEditForm:pvp:processoValorPagamentoVencData_input"]'
    css_inputfavorecido = (
        'input[id="processoValorPagamentoEditForm:pvp:processoValorFavorecido_input"]'
    )
    resultado_favorecido = 'li[class="ui-autocomplete-item ui-autocomplete-list-item ui-corner-all ui-state-highlight"]'
    valor_processo = 'div[id="processoValorPagamentoEditForm:pvp:j_id_2m_1_i_8_1_9_26_1_2_1:pvpEFSpgTypeSelectField1CombosCombo"]'
    boleto = 'li[id="processoValorPagamentoEditForm:pvp:j_id_2m_1_i_8_1_9_26_1_2_1:pvpEFSpgTypeSelectField1CombosCombo_1"]'
    css_cod_bars = 'input[id="processoValorPagamentoEditForm:pvp:j_id_2m_1_i_8_1_9_26_1_2_1:j_id_2m_1_i_8_1_9_26_1_2_c_2:j_id_2m_1_i_8_1_9_26_1_2_c_5:0:j_id_2m_1_i_8_1_9_26_1_2_c_15:j_id_2m_1_i_8_1_9_26_1_2_c_1v"]'
    css_centro_custas = 'input[id="processoValorPagamentoEditForm:pvp:j_id_2m_1_i_9_1_9_26_1_1_1:pvpEFBfieldText"]'
    css_div_conta_debito = 'div[id="processoValorPagamentoEditForm:pvp:j_id_2m_1_i_a_1_9_26_1_1_1:pvpEFBtypeSelectField1CombosCombo"]'
    valor_guia = 'input[id="processoValorPagamentoEditForm:pvp:valorField_input"]'
    css_gru = 'li[id="processoValorPagamentoEditForm:pvp:j_id_2m_1_i_2_1_9_g_1:eFileTipoCombo_35"]'
    editar_pagamentofile = 'div[id="processoValorPagamentoEditForm:pvp:j_id_2m_1_i_2_1_9_g_1:gedEFileDataTable"]'
    css_tipocusta = 'div[id="processoValorPagamentoEditForm:pvp:j_id_2m_1_i_4_1_9_26_1_1_1:pvpEFBtypeSelectField1CombosCombo"]'
    css_listcusta = 'ul[id="processoValorPagamentoEditForm:pvp:j_id_2m_1_i_4_1_9_26_1_1_1:pvpEFBtypeSelectField1CombosCombo_items"]'
    custas_civis = 'li[data-label="CUSTAS JUDICIAIS CIVEIS"]'
    custas_monitorias = 'li[data-label="CUSTAS JUDICIAIS - MONITORIAS"]'
    botao_salvar_pagamento = (
        'button[id="processoValorPagamentoEditForm:btnSalvarProcessoValorPagamento"]'
    )
    valor_resultado = 'div[id="tabViewProcesso:pvp-dtProcessoValorResults"]'
    botao_ver = 'button[title="Ver"]'
    valor = 'iframe[title="Valor"]'
    visualizar_tipo_custas = r"#processoValorPagamentoView\:j_id_p_1_2_1_2_1 > table > tbody > tr:nth-child(5)"
    visualizar_cod_barras = r"#processoValorPagamentoView\:j_id_p_1_2_1_2_7_8_4_23_1\:j_id_p_1_2_1_2_7_8_4_23_2_1_2_1\:j_id_p_1_2_1_2_7_8_4_23_2_1_2_2_1_3 > table > tbody > tr:nth-child(3)"
    visualizar_tipoCondenacao = r"#processoValorPagamentoView\:j_id_p_1_2_1_2_1 > table > tbody > tr:nth-child(4)"

    # PROVISIONAMENTO
    css_btn_edit = (
        'button[id="tabViewProcesso:j_id_i3_c_1_5_2:processoValoresEditarBtn"]'
    )
    ver_valores = 'a[href="#tabViewProcesso:valores"]'
    table_valores_css = 'tbody[id="tabViewProcesso:j_id_i3_c_1_5_2:j_id_i3_c_1_5_70:viewValoresCustomeDt_data"]'
    value_provcss = 'div[id="tabViewProcesso:j_id_i3_c_1_5_2:j_id_i3_c_1_5_70:viewValoresCustomeDt:0:j_id_i3_c_1_5_7e:0:j_id_i3_c_1_5_7m"]'
    div_tipo_obj_css = 'div[id="selectManyObjetoAdicionarList"]'
    itens_obj_div_css = 'div[id="selectManyObjetoAdicionarList_panel"]'
    checkbox = 'div[class="ui-chkbox ui-widget"]'
    botao_adicionar = 'button[id="adicionarObjetoBtn"]'
    botao_editar = 'button[id="j_id_4w:editarFasePedidoBtn"]'
    css_val_inpt = 'input[id="j_id_2m:j_id_2p_2e:processoAmountObjetoDt:0:amountValor_input"][type="text"]'
    css_risk = 'div[id="j_id_2m:j_id_2p_2e:processoAmountObjetoDt:0:j_id_2p_2i_5_1_6_5_k_2_2_1"]'
    processo_objt = 'ul[id="j_id_2m:j_id_2p_2e:processoAmountObjetoDt:0:j_id_2p_2i_5_1_6_5_k_2_2_1_items"]'
    botao_salvar_id = 'button[id="salvarBtn"]'
    DataCorrecaoCss = 'input[id="j_id_2m:j_id_2p_2e:processoAmountObjetoDt:0:amountDataCorrecao_input"]'
    DataJurosCss = (
        'input[id="j_id_2m:j_id_2p_2e:processoAmountObjetoDt:0:amountDataJuros_input"]'
    )
    texto_motivo = 'textarea[id="j_id_2m:j_id_2p_2e:j_id_2p_2i_8:j_id_2p_2i_j"]'
