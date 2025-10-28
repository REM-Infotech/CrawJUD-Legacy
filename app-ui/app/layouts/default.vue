<template>
  <AppHeader />
  <div style="background: var(--color-violet-eggplant-600)">
    <div class="content p-5 d-flex flex-column container-fluid overflow-y-auto">
      <slot />
    </div>
  </div>
</template>

<style lang="css" scoped>
.content {
  width: 100dvw;
  height: calc(100dvh - 70px);
  min-width: 100%;
  min-height: 100%;
}
</style>
