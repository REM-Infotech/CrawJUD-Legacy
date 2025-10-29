<script setup lang="ts">
const botList = ref<BotInfo[]>([]);
const filterBotList = computed(() => botList.value);
onMounted(async () => {
  botList.value = await bots.listagemBots();
});
</script>
<template>
  <div>
    <TransitionGroup name="fade" mode="out-in" tag="div" class="row">
      <BCol
        sm="12"
        md="6"
        lg="4"
        xl="3"
        v-for="(item, index) in filterBotList"
        :key="item.display_name"
        :data-index="index"
        class="p-4"
      >
        <div class="card border border-dark border-3 rounded" style="min-height: 460px">
          <h6 class="card-header bg-secondary bg-opacity-25 fw-bold">
            {{ item.display_name }}
          </h6>
          <img
            :src="bots.getLogo(item.sistema)"
            :alt="`Logo Sistema ${item.sistema?.toLowerCase()}`"
            :class="bots.getClassImgLogo(item.sistema)"
          />
          <div class="card-body bg-secondary bg-opacity-10">
            <h5 class="card-text">
              {{ item.descricao }}
            </h5>
          </div>
          <div
            class="card-footer d-flex align-items-center justify-content-between bg-secondary bg-opacity-25"
          >
            <button class="btn btn-success fw-semibold" @click="bots.handleBotSelected(item)">
              Acessar Robô
            </button>
          </div>
        </div>
      </BCol>
    </TransitionGroup>
  </div>
</template>
<style scoped lang="css">
.imgBot {
  min-height: 200px;
  object-fit: contain;
  width: 100%;
  height: 200px;
}
</style>
