$(document).ready(function () {
  var TipoUser = $("select[id='tipo_user']");
  var DivLicenses = $("div[id='licenses']");
  var licensesOptions = $("select[id='licenses']");

  // Armazena a primeira opção
  var optionFirst = licensesOptions.find("option:nth-child(2)");
  var lastOption = optionFirst.clone(); // Clona a primeira opção
  var lastOptionValue = optionFirst.val(); // Armazena o valor da primeira opção

  // Remove a primeira opção inicialmente
  licensesOptions.find("option:nth-child(2)").remove();

  TipoUser.change(function () {
    if (TipoUser.val() === "admin") {
      // Remove a primeira opção apenas se ela for igual a lastOption
      if (
        licensesOptions.find("option:first").val() === lastOptionValue &&
        TipoUser.val() !== "default_user"
      ) {
        licensesOptions.find("option:first").remove();
      }

      licensesOptions.find("option").prop("disabled", false);
      // Atualiza o Select2 para refletir a alteração
      licensesOptions.trigger("change.select2");
    } else if (TipoUser.val() === "supersu") {
      // Adiciona novamente a opção se ela não estiver presente
      if (
        licensesOptions.find(`option[value="${lastOptionValue}"]`).length === 0
      ) {
        licensesOptions.prepend(lastOption);
        licensesOptions.trigger("change.select2"); // Atualiza o Select2
      }

      // Desabilitar todas as outras opções e selecionar a única habilitada
      licensesOptions
        .find("option")
        .not(`option[value="${lastOptionValue}"]`)
        .prop("disabled", true);

      // Seleciona a única opção habilitada
      licensesOptions.val(lastOptionValue).trigger("change.select2");
    } else if (TipoUser.val() === "default_user") {
      // Reabilita todas as opções caso o TipoUser seja alterado de "supersu" para outro
      licensesOptions.find("option").prop("disabled", false);
    }

    // Limpar a seleção atual para outros tipos de usuário
    if (TipoUser.val() !== "supersu") {
      licensesOptions.val(null).trigger("change");
    }
  });
});
