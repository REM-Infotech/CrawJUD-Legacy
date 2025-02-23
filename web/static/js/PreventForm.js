$(document).ready(function () {
  // Seleciona o formulário e previne o envio ao pressionar Enter
  $("form").on("keydown", function (event) {
    if (event.key === "Enter") {
      event.preventDefault(); // Previne o envio do formulário
    }
  });
});
