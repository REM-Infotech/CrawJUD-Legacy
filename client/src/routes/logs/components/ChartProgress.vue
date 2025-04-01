<script setup lang="ts">
import { faPieChart } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
</script>

<template>
  <div
    class="card mb-4 fixed-height-card border-4 rounded rounded-4 border-black"
    style="height: 35rem"
  >
    <div class="card-header">
      <div class="row justify-content-between align-items-center">
        <div class="col-md-5">
          <span class="fw-semibold me-3">
            <i class="fas fa-chart-pie"></i>
            <FontAwesomeIcon :icon="faPieChart" />
          </span>
          <span class="fw-semibold">Logs </span>
        </div>
      </div>
    </div>
    <div class="card-body bg-success bg-opacity-50">
      <div class="container-fluid d-grid justify-content-xl-center w-50">
        <canvas id="LogsBotChart"></canvas>
      </div>
    </div>
    <div class="card-footer small text-muted fw-semibold">
      <span id="remaining">Restantes: -.- </span> | <span id="success">Sucessos: -.- </span> |
      <span id="errors">Erros: -.- </span>
    </div>
  </div>
</template>
