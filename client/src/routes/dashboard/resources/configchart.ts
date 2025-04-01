import { AxiosResponse } from "axios";
import { api } from "../../../main";

export default async function () {
  async function getConfigSystem(): Promise<unknown> {
    const response: AxiosResponse = await api.get("/linechart_system");

    const config = {
      type: "line",
      data: response.data.dataset,
      options: {
        responsive: true,
        interaction: {
          mode: "index",
          intersect: false,
        },
        stacked: false,
        plugins: {
          title: {
            display: true,
            text: "Grafico de Execuções",
          },
        },
        scales: {
          y: {
            type: "linear",
            display: true,
            position: "left",
          },
          y1: {
            type: "linear",
            display: true,
            position: "right",

            // grid line settings
            grid: {
              drawOnChartArea: false, // only want the grid lines for one axis to show up
            },
          },
        },
      },
    };

    return config;
  }

  async function getConfigBot(): Promise<unknown> {
    const response: AxiosResponse = await api.get("/linechart_bot");

    const config = {
      type: "line",
      data: response.data.dataset,
      options: {
        responsive: true,
        interaction: {
          mode: "index",
          intersect: false,
        },
        stacked: false,
        plugins: {
          title: {
            display: true,
            text: "Grafico de Execuções",
          },
        },
        scales: {
          y: {
            type: "linear",
            display: true,
            position: "left",
          },
          y1: {
            type: "linear",
            display: true,
            position: "right",

            // grid line settings
            grid: {
              drawOnChartArea: false, // only want the grid lines for one axis to show up
            },
          },
        },
      },
    };

    return config;
  }

  const config_system = await getConfigSystem();
  const config_bot = await getConfigBot();

  return { config_system, config_bot };
}
