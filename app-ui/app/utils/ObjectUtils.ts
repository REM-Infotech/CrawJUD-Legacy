class ObjectUtils {
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
}

export default ObjectUtils;
