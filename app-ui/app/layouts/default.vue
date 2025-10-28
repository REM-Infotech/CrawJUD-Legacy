<template>
  <div style="background: var(--color-violet-eggplant-600)">
    <AppHeader />
    <div class="content p-5 d-flex flex-column container-fluid">
      <slot />
    </div>
  </div>
</template>

<style lang="css" scoped>
.content {
  width: calc(100dvw - 30px);
  height: 100dvh;
  min-width: 100%;
  min-height: 100%;
}
</style>
