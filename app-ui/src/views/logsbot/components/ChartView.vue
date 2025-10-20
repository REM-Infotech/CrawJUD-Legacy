<script setup lang="ts">
import { useStoreLogsBot } from "@/stores/bot/logs";
import {
  ArcElement,
  BarElement,
  CategoryScale,
  Chart as ChartJS,
  Legend,
  LinearScale,
  Title,
  Tooltip,
} from "chart.js";
import { storeToRefs } from "pinia";
import { computed } from "vue";
import { Doughnut } from "vue-chartjs";
import MaterialSymbolsPieChartOutline from "~icons/material-symbols/pie-chart-outline?width=24px&height=24px";
import setupLogsExec from "./setupLogsExec";

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale, ArcElement);

const { remainingLogs, totalSuccess, totalErrors } = storeToRefs(useStoreLogsBot());
const { CardContent, SizeCard, MinSizeCard } = setupLogsExec();

const computedData = computed(() => [remainingLogs.value, totalSuccess.value, totalErrors.value]);
</script>

<template>
  <div class="card mb-4 fixed-height-card">
    <div class="card-header">
      <div class="row justify-content-between align-items-center">
        <div class="col-md-5">
          <span class="fw-semibold">
            <MaterialSymbolsPieChartOutline class="me-2" />
          </span>
          <span class="fw-semibold"> Gráfico da execução </span>
        </div>
      </div>
    </div>
    <div class="card-body" style="min-height: 400px">
      <CardContent :SizeCard="SizeCard" :MinSizeCard="MinSizeCard">
        <Doughnut
          :options="{ responsive: true }"
          :data="{
            labels: ['EXECUTADOS', 'SUCESSOS', 'ERROS'],
            datasets: [
              {
                data: computedData,
                backgroundColor: ['#0096C7', '#42cf06', '#FF0000'],
              },
            ],
          }"
        />
      </CardContent>
    </div>
    <div class="card-footer small text-muted fw-semibold">
      <span id="remaining">Pendentes: {{ computedData[0] }}</span> |
      <span id="success">Sucessos: {{ computedData[1] }}</span> |
      <span id="error">Erros: {{ computedData[2] }}</span>
    </div>
  </div>
</template>

<style lang="css" scoped>
.card {
  height: 100%;
  max-height: calc(100% - 25px);
}
</style>
