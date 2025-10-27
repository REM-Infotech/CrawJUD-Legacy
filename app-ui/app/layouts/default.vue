<template>
  <div class="bg-surface-50 dark:bg-surface-950">
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
  margin-top: 20px;
  overflow-y: hidden;
  display: flex;
  flex-direction: column;

  padding: 2.5rem;
}
</style>
