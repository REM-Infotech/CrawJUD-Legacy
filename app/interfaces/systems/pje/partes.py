"""Estruturas TypedDict para o Json de Partes do PJe.

Estas classes tipadas representam os dados de partes conforme extraídos do PJe.
"""

from __future__ import annotations

from typing import TypedDict


class EstadoDict(TypedDict):
    """Defina os campos obrigatórios para um estado conforme estrutura do PJe.

    Args:
            id (int): Identificador único do estado.
            sigla (str): Sigla do estado.
            descricao (str): Descrição do estado.

    Returns:
            TypedDict: Estrutura tipada representando um estado do PJe.

    """

    id: int
    sigla: str
    descricao: str


class PaisDict(TypedDict):
    """Defina os campos obrigatórios para um país conforme estrutura do PJe.

    Args:
            id (int): Identificador único do país.
            codigo (str): Código do país.
            descricao (str): Descrição do país.

    Returns:
            TypedDict: Estrutura tipada representando um país do PJe.

    """

    id: int
    codigo: str
    descricao: str


class EnderecoDict(TypedDict, total=False):
    """Defina os campos obrigatórios para um endereço conforme estrutura do PJe.

    Args:
            id (int): Identificador único do endereço.
            logradouro (str): Logradouro do endereço.
            numero (str): Número do endereço.
            bairro (str): Bairro do endereço.
            idMunicipio (int): Identificador do município.
            municipio (str): Nome do município.
            municipioIbge (str): Código IBGE do município.
            estado (EstadoDict): Estado do endereço.
            pais (PaisDict): País do endereço.
            nroCep (str): CEP do endereço.
            idPessoa (int): Identificador da pessoa associada.
            correspondencia (bool): Indica se é endereço de correspondência.
            situacao (str): Situação do endereço.
            idUsuarioCadastrador (int): ID do usuário que cadastrou.
            dtAlteracao (str): Data de alteração.
            complemento (str): Complemento do endereço.
            motivo (str): Motivo da situação.

    Returns:
            TypedDict: Estrutura tipada representando um endereço do PJe.

    """

    id: int
    logradouro: str
    numero: str
    bairro: str
    idMunicipio: int
    municipio: str
    municipioIbge: str
    estado: EstadoDict
    pais: PaisDict
    nroCep: str
    idPessoa: int
    correspondencia: bool
    situacao: str
    idUsuarioCadastrador: int
    dtAlteracao: str
    complemento: str | None
    motivo: str | None


class PessoaFisicaDict(TypedDict):
    """Defina os campos obrigatórios para pessoa física conforme estrutura do PJe.

    Args:
            id (int): Identificador único da pessoa física.
            nome (str): Nome completo.
            situacao (bool): Situação ativa ou não.
            login (str): Login da pessoa física.
            codigoSexo (str): Código do sexo.
            sexo (str): Sexo.
            dataNascimento (str): Data de nascimento.
            nomeGenitora (str): Nome da genitora.
            podeUsarCelularParaMensagem (bool): Permissão para uso de celular.

    Returns:
            TypedDict: Estrutura tipada representando uma pessoa física do PJe.

    """

    id: int
    nome: str
    situacao: bool
    login: str
    codigoSexo: str
    sexo: str
    dataNascimento: str
    nomeGenitora: str
    podeUsarCelularParaMensagem: bool


class PessoaJuridicaDict(TypedDict, total=False):
    """Defina os campos obrigatórios para pessoa jurídica conforme estrutura do PJe.

    Args:
            id (int): Identificador único da pessoa jurídica.
            nomeFantasia (str): Nome fantasia.
            nome (str): Razão social.
            cnpj (str): CNPJ da empresa.
            numeroCpfResponsavel (str): CPF do responsável.
            dataAbertura (str): Data de abertura.
            dataFimAtividade (str): Data de fim de atividade.
            nomeResponsavel (str): Nome do responsável.
            orgaoPublico (bool): Indica se é órgão público.
            tipoPessoaCodigo (str): Código do tipo de pessoa.
            tipoPessoaLabel (str): Rótulo do tipo de pessoa.
            tipoPessoaTipoValidacaoReceita (str): Tipo de validação Receita.
            situacao (bool): Situação ativa ou não.
            dsTipoPessoa (str): Descrição do tipo de pessoa.
            dsRamoAtividade (str): Ramo de atividade.
            oficial (bool): Indica se é oficial.
            dsTpPrazoExpedienteAutomatico (str): Prazo expediente automático.
            login (str): Login da empresa.
            porteCodigo (int): Código do porte.
            porteLabel (str): Rótulo do porte.

    Returns:
            TypedDict: Estrutura tipada representando uma pessoa jurídica do PJe.

    """

    id: int
    nomeFantasia: str
    nome: str
    cnpj: str
    numeroCpfResponsavel: str
    dataAbertura: str
    dataFimAtividade: str
    nomeResponsavel: str
    orgaoPublico: bool
    tipoPessoaCodigo: str
    tipoPessoaLabel: str
    tipoPessoaTipoValidacaoReceita: str
    situacao: bool
    dsTipoPessoa: str
    dsRamoAtividade: str
    oficial: bool
    dsTpPrazoExpedienteAutomatico: str
    login: str
    porteCodigo: int
    porteLabel: str


class RepresentanteDict(TypedDict, total=False):
    """Defina os campos obrigatórios para um representante conforme estrutura do PJe.

    Args:
            id (int): Identificador único do representante.
            polo (str): Polo do representante.
            principal (bool): Indica se é principal.
            enderecoDesconhecido (bool): Endereço desconhecido.
            tipo (str): Tipo do representante.
            idTipoParte (int): ID do tipo de parte.
            nome (str): Nome do representante.
            documento (str): Documento do representante.
            tipoDocumento (str): Tipo do documento.
            numeroOab (str): Número da OAB.
            situacaoOab (str): Situação da OAB.
            emails (List[str]): Lista de e-mails.
            idPessoa (int): ID da pessoa.
            tipoPessoa (str): Tipo de pessoa.
            dataHabilitacao (str): Data de habilitação.
            status (str): Status do representante.
            situacao (str): Situação do representante.
            cpf (str): CPF do representante.
            autoridade (bool): Indica se é autoridade.
            sexo (str): Sexo.
            dddCelular (str): DDD do celular.
            numeroCelular (str): Número do celular.
            email (str): E-mail principal.

    Returns:
            TypedDict: Estrutura tipada representando um representante do PJe.

    """

    id: int
    polo: str
    principal: bool
    enderecoDesconhecido: bool
    tipo: str
    idTipoParte: int
    nome: str
    documento: str
    tipoDocumento: str
    numeroOab: str
    situacaoOab: str
    emails: list[str]
    idPessoa: int
    tipoPessoa: str
    dataHabilitacao: str
    status: str
    situacao: str
    cpf: str
    autoridade: bool
    sexo: str
    dddCelular: str
    numeroCelular: str
    email: str


class ParteDict(TypedDict, total=False):
    """Defina os campos obrigatórios para uma parte conforme estrutura do PJe.

    Args:
            id (int): Identificador único da parte.
            polo (str): Polo da parte.
            principal (bool): Indica se é principal.
            enderecoDesconhecido (bool): Endereço desconhecido.
            tipo (str): Tipo da parte.
            idTipoParte (int): ID do tipo de parte.
            nome (str): Nome da parte.
            documento (str): Documento da parte.
            tipoDocumento (str): Tipo do documento.
            representantes (List[RepresentanteDict]): Lista de representantes.
            idPessoa (int): ID da pessoa.
            tipoPessoa (str): Tipo de pessoa.
            status (str): Status da parte.
            situacao (str): Situação da parte.
            endereco (EnderecoDict): Endereço da parte.
            cpf (str): CPF da parte.
            ordem (int): Ordem da parte.
            autoridade (bool): Indica se é autoridade.
            pessoaFisica (PessoaFisicaDict): Dados de pessoa física.
            pessoaJuridica (PessoaJuridicaDict): Dados de pessoa jurídica.
            sexo (str): Sexo da parte.
            emails (List[str]): Lista de e-mails.

    Returns:
            TypedDict: Estrutura tipada representando uma parte do PJe.

    """

    id: int
    polo: str
    principal: bool
    enderecoDesconhecido: bool
    tipo: str
    idTipoParte: int
    nome: str
    documento: str
    tipoDocumento: str
    representantes: list[RepresentanteDict]
    idPessoa: int
    tipoPessoa: str
    status: str
    situacao: str
    endereco: EnderecoDict
    cpf: str
    ordem: int
    autoridade: bool
    pessoaFisica: PessoaFisicaDict
    pessoaJuridica: PessoaJuridicaDict
    sexo: str
    emails: list[str]


class PartesJsonDict(TypedDict):
    """Defina os campos obrigatórios para o JSON de partes do PJe.

    Args:
            ATIVO (List[ParteDict]): Lista de partes ativas.
            PASSIVO (List[ParteDict]): Lista de partes passivas.
            TERCEIROS (List[ParteDict]): Lista de terceiros.

    Returns:
            TypedDict: Estrutura tipada representando o JSON de partes do PJe.

    """

    ATIVO: list[ParteDict]
    PASSIVO: list[ParteDict]
    TERCEIROS: list[ParteDict]
