// Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.global.defaultFontFamily =
  '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = "#292b2c";

$(document).ready(function () {
  var Pages = 0;
  var pid = $("#pid").text();

  let fullUrl = window.location.href;
  var pid = fullUrl.split("/").filter(Boolean).pop();

  $.get(`/url_server/${pid}`).done(function (data_front) {
    var socketAddress = data_front["url_server"];
    var ul = document.getElementById("messages"); // Elemento <ul> onde as mensagens de log são exibidas
    var percent_progress = document.getElementById("progress_info");

    var ctx = document.getElementById("LogsBotChart");
    var LogsBotChart = new Chart(ctx, {
      type: "doughnut",
      data: {
        labels: ["RESTANTES", "SUCESSOS", "ERROS"],
        datasets: [
          {
            data: [0.1, 0.1, 0.1],
            backgroundColor: ["#0096C7", "#42cf06", "#FF0000"],
          },
        ],
      },
    });

    var socket = io(socketAddress + "/log", {
      extraHeaders: {
        pid: pid
      }
    });


    $("#stop_execut").on("click", () => {
      socket.emit("terminate_bot", { pid: pid });

      let msg = "Parando execução";
      var li = document.createElement("li");

      li.style.fontWeight = "bold";
      li.style.color = "orange";

      li.innerHTML = msg.replace(/\n/g, "<br>");
      ul.appendChild(li);

      var randomId = `id_${Math.random().toString(36).substring(2, 9)}`;

      li.setAttribute("id", randomId);
      document
        .getElementById(randomId)
        .scrollIntoView({ behavior: "smooth", block: "end" });

      window.location.reload();
    });

    socket.on("connect", function () {
      socket.emit("join", { pid: pid });
    });

    socket.on("log_message", function (data) {
      var messagePid = data.pid;
      var pos = parseInt(data.pos);
      var typeLog = data.type;

      updateElements(data);

      if (messagePid === pid) {
        var msg = data.message;

        if (msg === null) {
          var msg = data.last_log;
        }

        if (msg != null) {
          var li = document.createElement("li");

          li.style.fontWeight = "bold";
          li.style.color = "#d3e3f5";

          if (typeLog === "error") {
            li.style.fontWeight = "bold";
            li.style.color = "RED";
          } else if (typeLog === "success") {
            li.style.color = "#42cf06";
            li.style.fontWeight = "bold";
          } else if (typeLog === "info") {
            li.style.color = "orange";
            li.style.fontWeight = "bold";
          }

          if (/\n/.test(msg)) {
            li.style.color = "white";
          }

          li.innerHTML = msg.replace(/\n/g, "<br>");
          ul.appendChild(li);

          var randomId = `id_${Math.random().toString(36).substring(2, 9)}`;

          li.setAttribute("id", randomId);
          document
            .getElementById(randomId)
            .scrollIntoView({ behavior: "smooth", block: "end" });
        }

        if (msg.toLowerCase().includes("fim da execução")) {
          console.log("parado!!");

          var progress = 100;
          var percent_progress = document.getElementById("progress_info");
          var textNode = document.createTextNode(progress.toFixed(2) + "%");

          $("#progress_info").removeClass("bg-info");

          percent_progress.innerHTML = "";
          percent_progress.appendChild(textNode);
          percent_progress.style.width = progress + "%";

          $("#progress_info").addClass("bg-success");
          checkStatus();
        }
      }
    });
    // Função para extrair o número da posição da mensagem de log
    function checkStatus() {
      fetch(`/status/${pid}`)
        .then((response) => {
          if (response.ok) {
            return response.json();
          }
        })
        .then((data) => {
          if (data && data.document_url) {
            const downloadButton = document.getElementById("download-button");
            downloadButton.href = data.document_url;
            downloadButton.classList.remove("disabled");
            downloadButton.classList.remove("btn-outline-success");
            downloadButton.classList.add("btn-success");
            downloadButton.setAttribute("aria-disabled", "false");
          } else {
            console.warn("Invalid data:", data);
          }
        })
        .catch((error) => {
          console.error("Erro de rede:", error);
        });
    }
    function updateElements(data) {
      var typeLog = String(data.type);
      var total = parseInt(data.total);
      var remaining = parseInt(data.remaining);
      var success = parseInt(data.success);
      var errors = parseInt(data.errors);
      var status = data.status;
      var executed = success + errors;

      var CountErrors = document.querySelector('span[id="errors"]');
      var Countremaining = document.querySelector('span[id="remaining"]');
      var CountSuccess = document.querySelector('span[id="success"]');
      var TextStatus = document.querySelector('span[id="status"]');
      var lastRemainign = parseInt(LogsBotChart.data.datasets[0].data[0]);

      if (typeLog === "info") {
        Pages = Pages + 1;
        console.log(typeLog);
      }

      if (remaining < 0) {
        remaining = 0;
      }

      if (remaining === 0) {
        remaining = Pages;
      }

      CountErrors.innerHTML = `Erros: ${errors}`;
      Countremaining.innerHTML = `Restantes: ${remaining}`;
      TextStatus.innerHTML = `Status: ${status} | Total: ${total}`;

      var progress = (executed / total) * 100;
      var textNode = document.createTextNode(progress.toFixed(2) + "%");

      var chartType = LogsBotChart.config.type;
      var grafMode = data.graphicMode;

      if (status !== "Finalizado") {
        CountSuccess.innerHTML = `Sucessos: ${success}`;
        LogsBotChart.data.datasets[0].data = [remaining, success, errors];
      }

      if (grafMode !== undefined && grafMode !== chartType) {
        LogsBotChart.config.type = grafMode;
        LogsBotChart.data.datasets[0].data;
        LogsBotChart.data.labels[0] = "PÁGINAS";
        Countremaining.innerHTML = `Páginas: ${remaining}`;
      }

      if (parseInt(data.remaining) > 0) {
        percent_progress.innerHTML = "";
        percent_progress.appendChild(textNode);
        percent_progress.style.width = progress + "%";
      }

      LogsBotChart.update();
    }

    socket.on("connect_error", (err) => {
      // the reason of the error, for example "xhr poll error"
      console.log(err.message);

      // some additional description, for example the status code of the initial HTTP response
      console.log(err.description);

      // some additional context, for example the XMLHttpRequest object
      console.log(err.context);
    });
  });
});
