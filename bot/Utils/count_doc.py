def count_doc(doc: str) -> str | None:

    tipo_doc = None
    numero = "".join(filter(str.isdigit, doc))

    if len(numero) == 11:
        tipo_doc = "cpf"

    elif len(numero) == 14:
        tipo_doc = "cnpj"

    return tipo_doc
