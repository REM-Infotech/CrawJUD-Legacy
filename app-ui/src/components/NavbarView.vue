<script setup lang="ts">
import logoCrawjud from "@/assets/img/crawjud.png";
import MaterialSymbolsMenuRounded from "~icons/material-symbols/menu-rounded?width=24px&height=24px";
</script>

<template>
  <nav class="navbar navbar-expand-lg bg-body-tertiary rounded-bottom fixed-top">
    <div class="container-fluid">
      <a
        class="navbar-brand d-flex justify-content-center nav-link"
        data-bs-toggle="offcanvas"
        href="#offCanvasCrawJUD"
        role="button"
        aria-controls="offCanvasCrawJUD"
      >
        <span class="nav-link-icon text-white">
          <MaterialSymbolsMenuRounded />
        </span>
        <span class="text text-white fs-4"> Menu </span>
      </a>
      <div class="me-auto ms-auto d-flex gap-2">
        <img :src="logoCrawjud" alt="Logo CrawJUD" height="35" style="margin-right: 205px" />
      </div>
    </div>
  </nav>
</template>

<style lang="css" scoped>
.menu-heading {
  padding: 1.4rem 1rem 0.75rem;
  font-size: 0.75rem;
  font-weight: bold;
  text-transform: uppercase;
  color: rgba(46, 46, 46, 0.726);
  @media (prefers-color-scheme: dark) {
    color: rgba(255, 255, 255, 0.514);
  }
}

.nav-link-icon {
  font-size: 0.95rem;
  margin-right: 0.5rem;
  font-weight: bold;
}
.nav-link {
  display: flex;
  position: relative;
  align-items: center;
  color: #000000e1;
  @media (prefers-color-scheme: dark) {
    color: rgba(255, 255, 255, 0.795);
  }
}

.text {
  font-weight: 500;
}
</style>
