<script setup lang="ts">
import { faPieChart } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
</script>

<template>
  <div class="card fixed-height-card border-4 rounded rounded-4 border-black" style="height: 35rem">
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
    <div class="card-body bg-black overflow-auto">
      <div class="container-fluid">
        <ul id="messages" class="list-group list-group-flush over overflow-hidden"></ul>
      </div>
    </div>
    <div class="card-footer small text-muted fw-semibold">
      <span id="status">Status: Em Execução | Total: </span>
    </div>
  </div>
</template>
