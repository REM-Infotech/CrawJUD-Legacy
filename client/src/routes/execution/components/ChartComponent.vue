<template>
  <div class="row">
    <div class="col-xl-6">
      <div class="card mb-4">
        <div class="card-header">
          <i class="fas fa-chart-bar me-1"></i>
          Bar Chart Example
        </div>
        <div class="card-body">
          <canvas id="myBarChart" width="100%" height="40"></canvas>
        </div>
      </div>
    </div>
    <div class="col-xl-6">
      <div class="card mb-4">
        <div class="card-header">
          <i class="fas fa-chart-area me-1"></i>
          Area Chart Example
        </div>
        <div class="card-body">
          <canvas id="myAreaChart" width="100%" height="40"></canvas>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Chart } from "chart.js/auto";
import jQuery from "jquery";
import { onMounted } from "vue";
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const $ = jQuery;

// Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.font.family =
  '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.color = "#292b2c";

onMounted(() => {
  var ctx1 = (document.getElementById("myAreaChart") as HTMLCanvasElement)?.getContext("2d");

  if (!ctx1) return;
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  var myLineChart = new Chart(ctx1, {
    type: "line",
    data: {
      labels: [
        "Mar 1",
        "Mar 2",
        "Mar 3",
        "Mar 4",
        "Mar 5",
        "Mar 6",
        "Mar 7",
        "Mar 8",
        "Mar 9",
        "Mar 10",
        "Mar 11",
        "Mar 12",
        "Mar 13",
      ],
      datasets: [
        {
          label: "Sessions",
          tension: 0.3,
          backgroundColor: "rgba(2,117,216,0.2)",
          borderColor: "rgba(2,117,216,1)",
          pointRadius: 5,
          pointBackgroundColor: "rgba(2,117,216,1)",
          pointBorderColor: "rgba(255,255,255,0.8)",
          pointHoverRadius: 5,
          pointHoverBackgroundColor: "rgba(2,117,216,1)",
          pointHitRadius: 50,
          pointBorderWidth: 2,
          data: [
            10000, 30162, 26263, 18394, 18287, 28682, 31274, 33259, 25849, 24159, 32651, 31984,
            38451,
          ],
        },
      ],
    },
    options: {
      scales: {
        x: {
          time: {
            unit: "day",
          },
          grid: {
            display: false,
          },
          ticks: {
            maxTicksLimit: 7,
          },
        },
        y: {
          ticks: {
            minRotation: 0,
            maxRotation: 40000,
            maxTicksLimit: 5,
          },
          grid: {
            color: "rgba(0, 0, 0, .125)",
          },
        },
      },
    },
  });

  var ctx2 = (document.getElementById("myBarChart") as HTMLCanvasElement)?.getContext("2d");
  if (!ctx2) return;
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  var myBarChart = new Chart(ctx2, {
    type: "bar",
    data: {
      labels: ["January", "February", "March", "April", "May", "June"],
      datasets: [
        {
          label: "Revenue",
          backgroundColor: "rgba(2,117,216,1)",
          borderColor: "rgba(2,117,216,1)",
          data: [4215, 5312, 6251, 7841, 9821, 14984],
        },
      ],
    },
    options: {
      scales: {
        x: {
          time: {
            unit: "month",
          },
          grid: {
            display: false,
          },
          ticks: {
            maxTicksLimit: 6,
          },
        },
        y: {
          ticks: {
            minRotation: 0,
            maxRotation: 15000,
            maxTicksLimit: 5,
          },
          grid: {
            display: true,
          },
        },
      },
    },
  });

  // $.ajax({
  //   url: "/most_executed",
  //   type: "GET",
  //   success: function (data) {
  //     most_executed.data.labels = data.labels;
  //     most_executed.data.datasets[0].data = data.values;
  //     most_executed.update();
  //   },
  // });
  // $.ajax({
  //   url: "/PerMonth",
  //   type: "GET",
  //   success: function (data) {
  //     month_chart.data?.labels?.forEach((item, pos) => {
  //       for (const label of data.labels) {
  //         if (
  //           month_chart.data.labels &&
  //           month_chart.data.labels[pos].toLowerCase() === label.toLowerCase()
  //         ) {
  //           month_chart.data.datasets[0].data[pos] = data.values[pos];
  //           break;
  //         }
  //       }
  //     });
  //     month_chart.update();
  //   },
  // });
});
</script>
