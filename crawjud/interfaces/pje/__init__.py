"""Defina os dicionários tipados para processos judiciais e entidades relacionadas.

Este módulo contém definições de TypedDicts para representar estruturas de dados
utilizadas no contexto de processos judiciais, incluindo classes judiciais,
localizações, órgãos julgadores, jurisdições, usuários, atividades, municípios
e processos JT, conforme o padrão de integração do sistema PJe.

"""

from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from datetime import datetime


class CapaProcessualPJeDict(TypedDict):
    """Defina o dicionário para salvar dados da planilha de processos PJE.

    Args:
        ID_PJE (int): Identificador único do processo no PJE.
        LINK_CONSULTA (str): URL para consulta do processo.
        NUMERO_PROCESSO (str): Número do processo judicial.
        CLASSE (str): Classe judicial do processo.
        SIGLA_CLASSE (str): Sigla da classe judicial.
        DATA_DISTRIBUICAO (datetime): Data de distribuição do processo.
        STATUS_PROCESSO (str): Status atual do processo.
        SEGREDO_JUSTIÇA (str): Indica se o processo está em segredo de justiça.

    Returns:
        CapaProcessualPJeDict: Dicionário tipado com os dados do processo.

    """

    ID_PJE: int
    LINK_CONSULTA: str
    NUMERO_PROCESSO: str
    CLASSE: str
    SIGLA_CLASSE: str
    ORGAO_JULGADOR: str
    SIGLA_ORGAO_JULGADOR: str
    DATA_DISTRIBUICAO: datetime
    STATUS_PROCESSO: str
    SEGREDO_JUSTIÇA: str


class PartesProcessoPJeDict(TypedDict):
    """Defina os campos das partes do processo judicial no padrão PJe.

    Args:
        ID_PJE (int): Identificador único do processo no PJE.
        NOME (str): Nome da parte.
        CPF (str): CPF da parte.
        TIPO_PESSOA (str): Tipo da pessoa (física/jurídica).
        PROCESSO (str): Número do processo.
        POLO (str): Polo da parte (ativo/passivo).
        PARTE_PRINCIPAL (bool): Indica se é parte principal.
        TIPO_PARTE (str): Tipo da parte no processo.

    Returns:
        PartesProcessoPJeDict: Dicionário tipado com os dados da parte.

    """

    ID_PJE: int
    NOME: str
    DOCUMENTO: str
    TIPO_DOCUMENTO: str
    TIPO_PARTE: str
    TIPO_PESSOA: str
    PROCESSO: str
    POLO: str
    PARTE_PRINCIPAL: bool


class RepresentantePartesPJeDict(TypedDict):
    """Defina os campos dos representantes das partes do processo judicial no padrão PJe.

    Args:
        ID_PJE (int): Identificador único do processo no PJE.
        NOME (str): Nome do representante.
        CPF (str): CPF do representante.
        PARTE_PRINCIPAL (bool): Indica se é parte principal.
        TIPO_PARTE (str): Tipo da parte representada.
        TIPO_PESSOA (str): Tipo da pessoa (física/jurídica).
        PROCESSO (str): Número do processo.
        POLO (str): Polo da parte (ativo/passivo).
        OAB (str): Número de inscrição na OAB.
        EMAILS (str): E-mails do representante.
        TELEFONE (str): Telefone do representante.

    Returns:
        RepresentantePartesPJeDict: Dicionário tipado com os dados do representante.

    """

    ID_PJE: int
    NOME: str
    DOCUMENTO: str
    TIPO_DOCUMENTO: str
    REPRESENTADO: str
    TIPO_PARTE: str
    TIPO_PESSOA: str
    PROCESSO: str
    POLO: str
    OAB: str
    EMAILS: str
    TELEFONE: str


class AssuntosProcessoPJeDict(TypedDict):
    """Defina os campos dos assuntos do processo judicial no padrão PJe.

    Args:
        ID_PJE (int): Identificador único do processo no PJE.
        PROCESSO (str): Número do processo judicial.
        ASSUNTO_COMPLETO (str): Descrição completa do assunto.
        ASSUNTO_RESUMIDO (str): Descrição resumida do assunto.

    Returns:
        AssuntosProcessoPJeDict: Dicionário tipado com os dados dos assuntos.

    """

    ID_PJE: int
    PROCESSO: str
    ASSUNTO_COMPLETO: str
    ASSUNTO_RESUMIDO: str


class ClasseJudicialDict(TypedDict):
    """Defina os campos da classe judicial conforme estrutura do processo JSON.

    Args:
            id (int): Identificador da classe judicial
            codigo (str): Código da classe judicial
            descricao (str): Descrição da classe judicial
            sigla (str): Sigla da classe judicial
            requerProcessoReferenciaCodigo (str): Código de referência do processo
            controlaValorCausa (bool): Indica se controla valor da causa
            podeIncluirAutoridade (bool): Indica se pode incluir autoridade
            pisoValorCausa (float): Valor mínimo da causa
            ativo (bool): Indica se está ativo
            idClasseJudicialPai (int): ID da classe judicial pai
            possuiFilhos (bool): Indica se possui filhos

    Returns:
            dict: Dicionário tipado da classe judicial

    """

    id: int
    codigo: str
    descricao: str
    sigla: str
    requerProcessoReferenciaCodigo: str
    controlaValorCausa: bool
    podeIncluirAutoridade: bool
    pisoValorCausa: float
    ativo: bool
    idClasseJudicialPai: int
    possuiFilhos: bool


class LocalizacaoPaiDict(TypedDict):
    """Defina os campos da localização pai do processo judicial.

    Args:
            id (int): Identificador da localização pai
            descricao (str): Descrição da localização pai
            ativo (bool): Indica se está ativo
            estruturada (bool): Indica se é estruturada

    Returns:
            dict: Dicionário tipado da localização pai

    """

    id: int
    descricao: str
    ativo: bool
    estruturada: bool


class LocalizacaoInicialDict(TypedDict):
    """Defina os campos da localização inicial do processo judicial.

    Args:
            id (int): Identificador da localização
            descricao (str): Descrição da localização
            ativo (bool): Indica se está ativo
            idLocalizacaoPai (int): ID da localização pai
            estruturada (bool): Indica se é estruturada
            localizacaoPai (LocalizacaoPaiDict): Dados da localização pai

    Returns:
            dict: Dicionário tipado da localização inicial

    """

    id: int
    descricao: str
    ativo: bool
    idLocalizacaoPai: int
    estruturada: bool
    localizacaoPai: LocalizacaoPaiDict


class OrgaoJulgadorDict(TypedDict):
    """Defina os campos do órgão julgador do processo judicial.

    Args:
            id (int): Identificador do órgão julgador
            descricao (str): Descrição do órgão julgador
            cejusc (bool): Indica se é CEJUSC
            ativo (bool): Indica se está ativo
            sigla (str): Sigla do órgão julgador
            postoAvancado (bool): Indica se é posto avançado
            siglaEnvioDejt (str): Sigla para envio DEJT
            idLocalizacao (int): ID da localização
            idJurisdicao (int): ID da jurisdição
            dataCriacao (str): Data de criação
            dddTelefone (str): DDD do telefone
            dddFax (str): DDD do fax
            numeroTelefone (str): Número do telefone
            novoOrgaoJulgador (bool): Indica se é novo órgão julgador
            codigoOrigem (str): Código de origem
            instancia (str): Instância
            numeroVara (int): Número da vara
            idAplicacaoClasse (int): ID da aplicação da classe
            email (str): E-mail do órgão julgador
            codigoServentiaCnj (int): Código serventia CNJ
            codigoTipo (str): Código do tipo

    Returns:
            dict: Dicionário tipado do órgão julgador

    """

    id: int
    descricao: str
    cejusc: bool
    ativo: bool
    sigla: str
    postoAvancado: bool
    siglaEnvioDejt: str
    idLocalizacao: int
    idJurisdicao: int
    dataCriacao: str
    dddTelefone: str
    dddFax: str
    numeroTelefone: str
    novoOrgaoJulgador: bool
    codigoOrigem: str
    instancia: str
    numeroVara: int
    idAplicacaoClasse: int
    email: str
    codigoServentiaCnj: int
    codigoTipo: str


class OrgaoJulgadorCargoDict(TypedDict):
    """Defina os campos do cargo do órgão julgador do processo judicial.

    Args:
            id (int): Identificador do cargo
            descricao (str): Descrição do cargo
            siglaCargo (str): Sigla do cargo
            idCargo (int): ID do cargo
            dsCargo (str): Descrição do cargo
            idGrupoCargoJudicial (int): ID do grupo do cargo judicial
            dsGrupoCargoJudicial (str): Descrição do grupo do cargo judicial
            ativo (bool): Indica se está ativo
            recebeDistribuicao (bool): Indica se recebe distribuição
            auxiliar (bool): Indica se é auxiliar
            valorPeso (float): Valor do peso
            idOrgaoJulgador (int): ID do órgão julgador
            dsOrgaoJulgador (str): Descrição do órgão julgador
            pesoDistribuicao (float): Peso da distribuição
            acumulaMediaDosCargosEspecializados (bool): Acumula média dos cargos especializados
            compensacaoPorProdutividadePorClasse (bool): Compensação por produtividade por classe

    Returns:
            dict: Dicionário tipado do cargo do órgão julgador

    """

    id: int
    descricao: str
    siglaCargo: str
    idCargo: int
    dsCargo: str
    idGrupoCargoJudicial: int
    dsGrupoCargoJudicial: str
    ativo: bool
    recebeDistribuicao: bool
    auxiliar: bool
    valorPeso: float
    idOrgaoJulgador: int
    dsOrgaoJulgador: str
    pesoDistribuicao: float
    acumulaMediaDosCargosEspecializados: bool
    compensacaoPorProdutividadePorClasse: bool


class JurisdicaoDict(TypedDict):
    """Defina os campos da jurisdição do processo judicial.

    Args:
            id (int): Identificador da jurisdição
            descricao (str): Descrição da jurisdição
            ativo (bool): Indica se está ativo
            inibeLixeiraGigs (bool): Inibe lixeira GIGS
            codigoOrigem (int): Código de origem
            estado (str): Estado
            idEstado (int): ID do estado
            instancia (int): Instância
            idRegional (int): ID regional
            descricaoRegional (str): Descrição regional
            idRamoJustica (int): ID do ramo da justiça
            descricaoRamoJustica (str): Descrição do ramo da justiça

    Returns:
            dict: Dicionário tipado da jurisdição

    """

    id: int
    descricao: str
    ativo: bool
    inibeLixeiraGigs: bool
    codigoOrigem: int
    estado: str
    idEstado: int
    instancia: int
    idRegional: int
    descricaoRegional: str
    idRamoJustica: int
    descricaoRamoJustica: str


class UsuarioCadastroProcessoDict(TypedDict):
    """Defina os campos do usuário de cadastro do processo judicial.

    Args:
            id (int): Identificador do usuário
            nome (str): Nome do usuário
            login (str): Login do usuário

    Returns:
            dict: Dicionário tipado do usuário de cadastro

    """

    id: int
    nome: str
    login: str


class AtividadeDict(TypedDict):
    """Defina os campos da atividade do processo judicial.

    Args:
            id (int): Identificador da atividade
            nome (str): Nome da atividade

    Returns:
            dict: Dicionário tipado da atividade

    """

    id: int
    nome: str


class MunicipioDict(TypedDict):
    """Defina os campos do município do processo judicial.

    Args:
            id (int): Identificador do município
            nome (str): Nome do município
            idEstado (int): ID do estado
            ativo (bool): Indica se está ativo

    Returns:
            dict: Dicionário tipado do município

    """

    id: int
    nome: str
    idEstado: int
    ativo: bool


class ProcessoJTDict(TypedDict):
    """Defina os campos do processo JT do processo judicial.

    Args:
            id (int): Identificador do processo JT
            idProcesso (int): ID do processo
            atividade (AtividadeDict): Dados da atividade
            municipio (MunicipioDict): Dados do município

    Returns:
            dict: Dicionário tipado do processo JT

    """

    id: int
    idProcesso: int
    atividade: AtividadeDict
    municipio: MunicipioDict


class ProcessoJudicialDict(TypedDict):
    """Defina os campos do processo judicial conforme estrutura do JSON.

    Args:
            id (int): Identificador do processo
            numero (str): Número do processo
            classeJudicial (ClasseJudicialDict): Dados da classe judicial
            autuadoEm (str): Data de autuação
            numeroIdentificacaoJustica (int): Número de identificação da justiça
            distribuidoEm (str): Data de distribuição
            valorDaCausa (float): Valor da causa
            codigoClasseJudicialInicial (str): Código da classe judicial inicial
            labelClasseJudicialInicial (str): Rótulo da classe judicial inicial
            codigoStatusProcesso (str): Código do status do processo
            labelStatusProcesso (str): Rótulo do status do processo
            segredoDeJustica (bool): Indica se é segredo de justiça
            justicaGratuita (bool): Indica se é justiça gratuita
            tutelaOuLiminar (bool): Indica se há tutela ou liminar
            juizoDigital (bool): Indica se é juízo digital
            instancia (int): Instância
            localizacaoInicial (LocalizacaoInicialDict): Dados da localização inicial
            codigoApreciadoSegredo (str): Código apreciado segredo
            labelApreciadoSegredo (str): Rótulo apreciado segredo
            orgaoJulgador (OrgaoJulgadorDict): Dados do órgão julgador
            orgaoJulgadorCargo (OrgaoJulgadorCargoDict): Dados do cargo do órgão julgador
            jurisdicao (JurisdicaoDict): Dados da jurisdição
            apreciadoTutelaLiminar (bool): Indica se apreciou tutela liminar
            codigoApreciadoSigilo (str): Código apreciado sigilo
            labelApreciadoSigilo (str): Rótulo apreciado sigilo
            mandadoDevolvido (bool): Indica se mandado foi devolvido
            codigoFaseProcessual (int): Código da fase processual
            labelFaseProcessual (str): Rótulo da fase processual
            dataInicio (str): Data de início
            usuarioCadastroProcesso (UsuarioCadastroProcessoDict): Usuário de cadastro
            selecionadoPauta (bool): Indica se selecionado em pauta
            revisado (bool): Indica se revisado
            outraInstancia (bool): Indica se é outra instância
            selecionadoJulgamento (bool): Indica se selecionado para julgamento
            apreciadoJusticaGratuita (bool): Indica se apreciou justiça gratuita
            incidente (bool): Indica se é incidente
            deveMarcarAudiencia (bool): Indica se deve marcar audiência
            inRevisao (bool): Indica se está em revisão
            faseProcessual (str): Fase processual
            transitoEmJulgado (str): Data do trânsito em julgado
            processoJT (ProcessoJTDict): Dados do processo JT
            temAssociacao (bool): Indica se tem associação

    Returns:
            dict: Dicionário tipado do processo judicial

    """

    id: int
    numero: str
    classeJudicial: ClasseJudicialDict
    autuadoEm: str
    numeroIdentificacaoJustica: int
    distribuidoEm: str
    valorDaCausa: float
    codigoClasseJudicialInicial: str
    labelClasseJudicialInicial: str
    codigoStatusProcesso: str
    labelStatusProcesso: str
    segredoDeJustica: bool
    justicaGratuita: bool
    tutelaOuLiminar: bool
    juizoDigital: bool
    instancia: int
    localizacaoInicial: LocalizacaoInicialDict
    codigoApreciadoSegredo: str
    labelApreciadoSegredo: str
    orgaoJulgador: OrgaoJulgadorDict
    orgaoJulgadorCargo: OrgaoJulgadorCargoDict
    jurisdicao: JurisdicaoDict
    apreciadoTutelaLiminar: bool
    codigoApreciadoSigilo: str
    labelApreciadoSigilo: str
    mandadoDevolvido: bool
    codigoFaseProcessual: int
    labelFaseProcessual: str
    dataInicio: str
    usuarioCadastroProcesso: UsuarioCadastroProcessoDict
    selecionadoPauta: bool
    revisado: bool
    outraInstancia: bool
    selecionadoJulgamento: bool
    apreciadoJusticaGratuita: bool
    incidente: bool
    deveMarcarAudiencia: bool
    inRevisao: bool
    faseProcessual: str
    transitoEmJulgado: str
    processoJT: ProcessoJTDict
    temAssociacao: bool


class Endereco(TypedDict, total=False):
    """Definição do endereço utilizado nos dados do processo judicial.

    Args:
        logradouro (str): Nome da rua ou avenida.
        numero (str): Número do endereço.
        complemento (str): Complemento do endereço.
        bairro (str): Bairro do endereço.
        municipio (str): Município do endereço.
        estado (str): Estado do endereço.
        cep (str): Código postal.

    Returns:
        Endereco: Dicionário com informações do endereço.


    """

    logradouro: str
    numero: str
    complemento: str
    bairro: str
    municipio: str
    estado: str
    cep: str


class Papel(TypedDict):
    """Define o papel de uma pessoa no processo.

    Args:
        id (int): Identificador do papel.
        nome (str): Nome do papel.
        identificador (str): Código identificador do papel.

    Returns:
        Papel: Dicionário com informações do papel.

    """

    id: int
    nome: str
    identificador: str


class Representante(TypedDict):
    """Define o representante de uma parte no processo.

    Args:
        id (int): Identificador do representante.
        idPessoa (int): Identificador da pessoa.
        nome (str): Nome do representante.
        login (str): Login do representante.
        tipo (str): Tipo de representante.
        documento (str): Documento do representante.
        tipoDocumento (str): Tipo do documento.
        endereco (Endereco): Endereço do representante.
        polo (str): Polo do representante.
        situacao (str): Situação do representante.
        papeis (List[Papel]): Lista de papéis do representante.
        utilizaLoginSenha (bool): Indica se utiliza login e senha.

    Returns:
        Representante: Dicionário com informações do representante.

    """

    id: int
    idPessoa: int
    nome: str
    login: str
    tipo: str
    documento: str
    tipoDocumento: str
    endereco: Endereco
    polo: str
    situacao: str
    papeis: list[Papel]
    utilizaLoginSenha: bool


class Polo(TypedDict):
    """Define uma parte (polo) do processo judicial.

    Args:
        id (int): Identificador do polo.
        idPessoa (int): Identificador da pessoa.
        nome (str): Nome do polo.
        login (str): Login do polo.
        tipo (str): Tipo do polo.
        documento (str): Documento do polo.
        tipoDocumento (str): Tipo do documento.
        endereco (Endereco): Endereço do polo.
        polo (str): Polo (ativo/passivo).
        situacao (str): Situação do polo.
        representantes (List[Representante]): Lista de representantes.
        utilizaLoginSenha (bool): Indica se utiliza login e senha.

    Returns:
        Polo: Dicionário com informações do polo.

    """

    id: int
    idPessoa: int
    nome: str
    login: str
    tipo: str
    documento: str
    tipoDocumento: str
    endereco: Endereco
    polo: str
    situacao: str
    representantes: list[Representante]
    utilizaLoginSenha: bool


class Assunto(TypedDict):
    """Define o assunto do processo judicial.

    Args:
        id (int): Identificador do assunto.
        codigo (str): Código do assunto.
        descricao (str): Descrição do assunto.
        principal (bool): Indica se é o assunto principal.

    Returns:
        Assunto: Dicionário com informações do assunto.

    """

    id: int
    codigo: str
    descricao: str
    principal: bool


class Anexo(TypedDict):
    """Define um anexo relacionado ao processo.

    Args:
        id (int): Identificador do anexo.
        idUnicoDocumento (str): ID único do documento.
        titulo (str): Título do anexo.
        tipo (str): Tipo do anexo.
        tipoConteudo (str): Tipo do conteúdo.
        data (str): Data do anexo.
        ativo (bool): Indica se está ativo.
        documentoSigiloso (bool): Indica se é sigiloso.
        usuarioPerito (bool): Indica se é usuário perito.
        documento (bool): Indica se é documento.
        publico (bool): Indica se é público.
        poloUsuario (Optional[str]): Polo do usuário.
        usuarioJuntada (str): Usuário que juntou o anexo.
        usuarioCriador (int): Usuário criador do anexo.
        instancia (Optional[str]): Instância do anexo.

    Returns:
        Anexo: Dicionário com informações do anexo.

    """

    id: int
    idUnicoDocumento: str
    titulo: str
    tipo: str
    tipoConteudo: str
    data: str
    ativo: bool
    documentoSigiloso: bool
    usuarioPerito: bool
    documento: bool
    publico: bool
    poloUsuario: str | None
    usuarioJuntada: str
    usuarioCriador: int
    instancia: str | None


class ItemProcesso(TypedDict, total=False):
    """Define um item do processo judicial.

    Args:
        id (int): Identificador do item.
        idUnicoDocumento (str): ID único do documento.
        titulo (str): Título do item.
        tipo (str): Tipo do item.
        tipoConteudo (str): Tipo do conteúdo.
        data (str): Data do item.
        ativo (bool): Indica se está ativo.
        documentoSigiloso (bool): Indica se é sigiloso.
        usuarioPerito (bool): Indica se é usuário perito.
        documento (bool): Indica se é documento.
        publico (bool): Indica se é público.
        mostrarHeaderData (bool): Indica se mostra header de data.
        usuarioJuntada (str): Usuário que juntou o item.
        usuarioCriador (int): Usuário criador do item.
        instancia (str): Instância do item.
        anexos (List[Anexo]): Lista de anexos.
        poloUsuario (str): Polo do usuário.

    Returns:
        ItemProcesso: Dicionário com informações do item do processo.

    """

    id: int
    idUnicoDocumento: str
    titulo: str
    tipo: str
    tipoConteudo: str
    data: str
    ativo: bool
    documentoSigiloso: bool
    usuarioPerito: bool
    documento: bool
    publico: bool
    mostrarHeaderData: bool
    usuarioJuntada: str
    usuarioCriador: int
    instancia: str
    anexos: list[Anexo]
    poloUsuario: str


class Expediente(TypedDict, total=False):
    """Define um expediente do processo judicial.

    Args:
        destinatario (str): Destinatário do expediente.
        tipo (str): Tipo do expediente.
        meio (str): Meio de envio.
        dataCriacao (str): Data de criação.
        dataCiencia (str): Data de ciência.
        fechado (bool): Indica se está fechado.

    Returns:
        Expediente: Dicionário com informações do expediente.

    """

    destinatario: str
    tipo: str
    meio: str
    dataCriacao: str
    dataCiencia: str
    fechado: bool
