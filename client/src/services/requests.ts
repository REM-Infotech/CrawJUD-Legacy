import { useModal } from "bootstrap-vue-next";
import { $, api } from "../main";

export async function getExecutions() {
  const { show: show_message } = useModal("ModalMessage");

  api
    .get("/executions", {
      headers: {
        "Content-Type": "application/json",
      },
      withCredentials: true,
      withXSRFToken: true,
    })
    .then((response) => {
      const data = response.data.data;
      const items = data.map((item) => {
        const status: string = item.status;
        let link_file = item.file_output;
        const link_log = item.pid;
        if (status.toLowerCase() === "em execução") {
          link_file = `<a class="btn btn-sm btn-success disabled m-1" href="${link_file}" target="_blank" aria-disabled="true">Baixar Arquivo</a>
                    <a class="btn btn-sm btn-primary m-1" href="/logs/${link_log}" target="_blank">Ver Log</a>`;
        }

        if (status.toLowerCase() !== "em execução") {
          link_file = `<a class="btn btn-sm btn-success m-1" href="${link_file}" target="_blank">Baixar Arquivo</a>
                      <a class="btn btn-sm btn-primary m-1 disabled" href="/logs/${link_log}" target="_blank" aria-disabled="true">Ver Log</a>`;
        }

        return [
          item.pid,
          item.user,
          item.botname,
          item.xlsx,
          item.start_date,
          item.status,
          item.stop_date,
          link_file,
        ];
      });

      return items;
    })
    .catch((response) => {
      // check if response >= 400 and < 500 and response not 404
      if (response.status >= 400 && response.status < 500 && response.status !== 404) {
        $("#message").text("Sessão expirada, faça login novamente!");
        show_message();
      }
    });
}
