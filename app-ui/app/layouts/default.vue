<template>
  <div class="content">
    <slot />
  </div>
</template>

<style lang="css" scoped>
.content {
  width: calc(100dvw - 30px);
  height: 100dvh;
  min-width: 100%;
  min-height: 100%;
  align-items: center;

  overflow-y: hidden;

  justify-content: center;
  display: flex;
  flex-direction: column;
}
</style>
