<template>
  <div style="background: var(--color-violet-eggplant-600)">
    <AppHeader />
    <div class="content">
      <slot></slot>
    </div>
  </div>
</template>

<style lang="css" scoped>
.content {
  width: calc(100dvw - 30px);
  height: 100dvh;
  min-width: 100%;
  min-height: 100%;
  overflow-x: hidden;
  display: flex;
  padding: 5px;
  margin-top:;
  flex-direction: column;
}
</style>
