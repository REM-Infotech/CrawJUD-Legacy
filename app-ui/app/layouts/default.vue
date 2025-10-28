<template>
  <AppHeader />
  <div>
    <div class="content p-5 d-flex flex-column container-fluid overflow-y-auto">
      <slot />
    </div>
  </div>
</template>

<style lang="css" scoped>
.content {
  width: 100dvw;
  margin-top: 50px;
  height: calc(100dvh - 70px);
  min-width: 100%;
  min-height: 100%;
}
</style>
