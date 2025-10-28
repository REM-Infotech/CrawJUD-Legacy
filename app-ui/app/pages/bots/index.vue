<script setup lang="ts">
const bot_card_class = ref("col-md-3 p-4");
const botList = ref<BotInfo[]>([]);
const filterBotList = computed(() => botList.value);
onMounted(async () => {
  botList.value = await bots.listagemBots();
});

console.log(window);
</script>
<template>
  <div>
    <BRow>
      <TransitionGroup name="fade" mode="out-in">
        <BCol
          sm="12"
          md="6"
          lg="4"
          xl="3"
          v-for="(bot, index) in filterBotList"
          :key="bot.display_name"
          :data-index="index"
          class="p-4"
        >
          <div class="card border border-dark border-3 rounded" style="min-height: 460px">
            <h6 class="card-header bg-secondary bg-opacity-25 fw-bold">
              {{ bot.display_name }}
            </h6>
            <img
              :src="bots.getLogo(bot.system)"
              :alt="`Logo Sistema ${bot.system?.toLowerCase()}`"
              :class="bots.getClassImgLogo(bot.system)"
            />
            <div class="card-body bg-secondary bg-opacity-10">
              <h5 class="card-text">
                {{ bot.descricao }}
              </h5>
            </div>
            <div
              class="card-footer d-flex align-items-center justify-content-between bg-secondary bg-opacity-25"
            >
              <button class="btn btn-success fw-semibold" @click="bots.handleBotSelected(bot)">
                Acessar Robô
              </button>
            </div>
          </div>
        </BCol>
      </TransitionGroup>
    </BRow>
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
