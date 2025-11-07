$(document).ready(function () {
  var url_Profile = $("#urlProfile").text();
  const src_profiles = [$("#NavProfilePIC"), $("#ProfilePIC")];

  if (url_Profile) {
    $.get(url_Profile)
      .done(function () {
        SetProfile(url_Profile, src_profiles);
      })
      .fail(function () {
        // Captura o erro, como o 500
        var url_Profile =
          "https://cdn-icons-png.flaticon.com/512/3135/3135768.png";
        SetProfile(url_Profile, src_profiles);
      });
  }
});

function SetProfile(url, arrSrc) {
  for (srcSetter of arrSrc) {
    srcSetter.attr("src", url);
  }
}

window.addEventListener("DOMContentLoaded", (event) => {
  var ModalMessage = document.getElementById("ModalMessage");
  if (ModalMessage != null) {
    $(document).ready(function () {
      $("#ModalMessage").modal("show");
    });
  }

  // Toggle the side navigation
  const sidebarToggle = document.body.querySelector("#sidebarToggle");
  if (sidebarToggle) {
    // Uncomment Below to persist sidebar toggle between refreshes
    // if (localStorage.getItem('sb|sidebar-toggle') === 'true') {
    //     document.body.classList.toggle('sb-sidenav-toggled');
    // }
    sidebarToggle.addEventListener("click", (event) => {
      event.preventDefault();
      document.body.classList.toggle("sb-sidenav-toggled");
      localStorage.setItem(
        "sb|sidebar-toggle",
        document.body.classList.contains("sb-sidenav-toggled")
      );
    });
  }
});

// Função para filtrar os cards
function filterCards(element) {
  // Pegar o valor digitado no campo de busca
  var input = element;
  var filter = input.value.toUpperCase();

  // Pegar todos os cards
  var cards = document.getElementsByClassName("col-md-3");
  // Loop através dos cards e esconder aqueles que não correspondem à pesquisa
  for (var i = 0; i < cards.length; i++) {
    var title = cards[i].getElementsByClassName("card-header")[0];
    if (title) {
      var titleText = title.textContent || title.innerText;
      if (titleText.toUpperCase().indexOf(filter) > -1) {
        cards[i].style.display = "";
      } else {
        cards[i].style.display = "none";
      }
    }
  }
}

$(document).ready(function () {
  var seletors = $("select");
  if (seletors.length > 0) {
    $("select").select2({
      theme: "bootstrap-5",
      width: $("select").data("width")
        ? $("select").data("width")
        : $("select").hasClass("w-100")
        ? "100%"
        : "style",
      placeholder: $("select").data("placeholder"),
    });

    // Limpar todas as opções do segundo select
    var allOptions = $("#varas").html();
    $("#varas").empty();

    // Função para mostrar ou ocultar as opções do segundo select
    $("#state").on("change", function () {
      setTimeout(() => {
        $("#modalLoading").modal("show");
      }, 250);
      var selectedCategory = $(this).val(); // Obter a categoria selecionada

      // Re-adicionar as opções correspondentes à categoria selecionada
      $(allOptions).each(function () {
        var optionCategory = $(this).data("juizado_estado");
        if (optionCategory === selectedCategory) {
          $("#varas").append($(this)).trigger("change"); // Re-adicionar a opção
        } else if (optionCategory !== selectedCategory) {
          $("#varas").empty();
        }
      });

      // Atualizar o Select2
      $("#varas").val(null).trigger("change"); // Limpar a seleção atual

      // Ocultar os itens não correspondentes no Select2
      $("#varas").on("select2:open", function () {
        $(".select2-results__option").each(function () {
          var optionCategory = $(this).data("category");
          if (optionCategory !== selectedCategory) {
            $(this).hide(); // Esconder as opções que não correspondem à categoria
          }
        });
      });
      setTimeout(() => {
        $("#modalLoading").modal("hide");
      }, 1000);
    });
  }
});

function authMethodChange(element) {
  let div_cert = document.querySelector('div[id="cert"]');
  let div_pw = document.querySelector('div[id="pw"]');

  if (element.value === "cert") {
    div_cert.style.display = "block";
    div_pw.style.display = "none";
  } else if (element.value === "pw") {
    div_cert.style.display = "none";
    div_pw.style.display = "block";
  }
}

function showLoad() {
  setTimeout(() => {
    $("#modalLoading").modal("show");
  }, 500);
}
