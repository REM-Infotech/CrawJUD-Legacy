<script setup lang="ts">
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";

import {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  faMinus,
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  faMaximize,
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  faClose,
  faSun,
  faMoon,
  faCircleHalfStroke,
} from "@fortawesome/free-solid-svg-icons";
</script>

<template>
  <nav class="navbar navbar-expand-xl navbar-indigo" aria-label="Sixth navbar example">
    <div class="container-fluid">
      <a
        class="navbar-brand rounded"
        href="#"
        type="button"
        data-bs-toggle="offcanvas"
        data-bs-target="#offcanvasWithBothOptions"
        aria-controls="offcanvasWithBothOptions"
      >
        <img class="bi pe-none me-2" src="../assets/crawjud.png" alt="logo" width="40" />
        <span class="align-middle fw-bold">Menu</span>
      </a>
      <button
        class="navbar-toggler rounded"
        type="button"
        data-bs-toggle="collapse"
        data-bs-target="#navbarsExample06"
        aria-controls="navbarsExample06"
        aria-expanded="false"
        aria-label="Toggle navigation"
      >
        <span class="navbar-toggler-icon"></span>
      </button>

      <div class="collapse navbar-collapse" id="navbarsExample06">
        <ul class="navbar-nav me-auto mb-2 mb-xl-0"></ul>
        <!-- <ul class="navbar-nav me-auto mb-2 mb-xl-0">
          <li class="nav-item">
            <a class="nav-link rounded" href="#">Home</a>
          </li>
          <li class="nav-item">
            <a class="nav-link rounded" href="#">Link</a>
          </li>
        </ul> -->
        <!-- <button class="btn btn-secondary m-1" onclick="window.close()">
          <FontAwesomeIcon :icon="faMinus" />
        </button>
        <button class="btn btn-warning m-1">
          <FontAwesomeIcon :icon="faMaximize" />
        </button>
        <button class="btn btn-danger m-1">
          <FontAwesomeIcon :icon="faClose" />
        </button> -->
        <div class="dropdown ms-3 me-2" data-bs-theme="dark">
          <button
            class="btn btn-secondary dropdown-toggle"
            type="button"
            id="dropdownMenuButtonDark"
            data-bs-toggle="dropdown"
            aria-expanded="false"
          >
            <FontAwesomeIcon :icon="faSun" />
          </button>
          <ul class="dropdown-menu dropdown-menu-end mt-2" aria-labelledby="dropdownMenuButtonDark">
            <li>
              <button
                type="button"
                class="dropdown-item d-flex align-items-center"
                data-bs-theme-value="light"
                aria-pressed="false"
              >
                <FontAwesomeIcon :icon="faSun" class="me-2" />
                Claro
              </button>
            </li>
            <li>
              <button
                type="button"
                class="dropdown-item d-flex align-items-center"
                data-bs-theme-value="dark"
                aria-pressed="true"
              >
                <FontAwesomeIcon :icon="faMoon" class="me-2" />
                Escuro
              </button>
            </li>
            <li>
              <button
                type="button"
                class="dropdown-item d-flex align-items-center"
                aria-pressed="false"
              >
                <FontAwesomeIcon :icon="faCircleHalfStroke" class="me-2" />
                Auto
              </button>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </nav>
</template>
