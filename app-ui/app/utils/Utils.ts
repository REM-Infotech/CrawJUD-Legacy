class Utils {
  /**
   * Converte uma string em CamelCase para snake_case.
   *
   * @param {string} name - String no formato CamelCase.
   * @returns {string} String convertida para snake_case.
   */
  static camelToSnake(name: string): string {
    const s1 = name.replace(/(.)([A-Z][a-z]+)/g, "$1_$2");
    return s1.replace(/([a-z0-9])([A-Z])/g, "$1_$2").toLowerCase();
  }

  /**
   * Separa uma string em CamelCase inserindo espaços entre as palavras.
   *
   * @param {string} name - String no formato CamelCase.
   * @returns {string} String com espaços entre as palavras.
   *
   * @example
   * // Retorna "Meu Nome Completo"
   * camelToWords("MeuNomeCompleto");
   */
  static camelToWords(name: string): string {
    return name
      .replace(/([a-z])([A-Z])/g, "$1 $2") // separa transições a→A
      .replace(/([A-Z])([A-Z][a-z])/g, "$1 $2"); // separa blocos de maiúsculas (ex: "userIDNumber")
  }

  static isInstance(value: any, type: any): boolean {
    return value instanceof type;
  }

  /**
   * Normaliza uma string removendo acentos e caracteres "inseguros",
   * e retorna as palavras separadas por um único espaço.
   *
   * Comportamento inspirado na versão Python que usa:
   *   normalized = "".join([c for c in normalize("NFKD", s) if not combining(c)])
   *   secure_filename(...)
   *   .replace("-", "")
   *   .replace("_", " ")
   *   .split()
   *   .join(" ")
   *
   * @param {string} input - String de entrada (pode conter acentos e caracteres especiais).
   * @returns {string} String formatada com palavras separadas por espaços simples.
   *
   * @example
   * formatString("áçẽu-Nome_test") // "aceu Nome test"
   */

  static formatString(input: string): string {
    if (input == null) return "";

    // 1) Normaliza (NFKD) para decompor caracteres com acento
    const normalized = input.normalize?.("NFKD") ?? input;

    // 2) Remove marcas combinantes (diacríticos).
    // Usa Unicode property escape \p{M} quando suportado; senão, fallback para intervalo comum.
    let withoutDiacritics: string;
    try {
      // Tenta usar \p{M} (requer ES2018+ / Unicode property escapes)
      withoutDiacritics = normalized.replace(/\p{M}/gu, "");
    } catch {
      // Fallback quando o engine não suporta \p{} — cobre os diacríticos mais comuns
      withoutDiacritics = normalized.replace(/[\u0300-\u036f]/g, "");
    }

    // 3) "secure_filename"-like sanitization:
    //    - manter letras, dígitos, ponto, hífen e underscore (similar ao secure_filename)
    //    - tudo o que não for isso vira espaço (para evitar juntar palavras indevidas)
    //
    // Observação: o código Python depois remove '-' e troca '_' por espaço,
    // então aqui já convertemos caracteres permitidos em espaços em seguida.
    const sanitized = withoutDiacritics.replace(/[^0-9A-Za-z.\-_]+/g, " ");

    // 4) remover '-' (hífen), transformar '_' em espaço e compactar múltiplos espaços
    const removedHyphen = sanitized.replace(/-/g, "");
    const underscoresToSpace = removedHyphen.replace(/_/g, " ");

    // 5) split + join para normalizar espaços (trim + compact)
    const finalStr = underscoresToSpace
      .split(/\s+/) // separa por qualquer sequência de espaços
      .filter(Boolean) // remove entradas vazias
      .join(" ");

    return finalStr;
  }
}

export default Utils;
