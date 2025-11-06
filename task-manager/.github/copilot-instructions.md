"""
<Breve descrição da função.>

Args:
    <param1> (<type>): <descrição>
    <param2> (<type>): <descrição>

Returns:
    <type>: <descrição do valor retornado>

Raises:
    <ExceptionType>: <descrição> (opcional)

"""

- Ao corrigir uma docstring, priorize fazer do zero.
- O texto da docstring precisa ser em português.
- Docstrings devem respeitar o limite de 65 caracteres.
- A primeira palavra do sumário precisa ser em modo imperativo.
- Caso funções/classes não tenham comentários, inclua comentários para explicar o código sempre.
- Corrija erros do tipo "Missing type annotation".
- As funções devem ter seus parâmetros e retornos tipados.
- Ao tipar, evite usar o `Any` Builtin do `Typing` criando um novo any usando `type AnyType = Any`
- Caso a função nao retorne nada, evite inserir Raises/Returns
