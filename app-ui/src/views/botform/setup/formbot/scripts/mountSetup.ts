import { onBeforeMount, onMounted, onUnmounted, type Reactive, type Ref } from "vue";
import { type Router } from "vue-router";
import formConfig from "../json/formconfig.json";
import varas from "../json/varas.json";

export default function (
  router: Router,
  bot: Ref<BotRecord | null>,
  EnabledInputs: Reactive<TypeEnabledInputs>,
  courtOptions: Ref<selectCourts[]>,
) {
  onMounted(() => {
    if (bot.value === null) {
      router.push({ name: "bots" });
    }
  });
  onUnmounted(() => {
    bot.value = null;
  });
  onBeforeMount(() => {
    if (!bot.value?.classification || !bot.value.form_cfg) return;

    const classification = bot.value.classification as Classification;
    const formcfg = bot.value.form_cfg as FormConfig;
    const formconfigClass = formConfig[classification] as FormConfigRecord;
    const formconfigList = formconfigClass[formcfg];

    Object.entries(EnabledInputs).map(([key, value]) => {
      const isKey = Array.from(formconfigList).find((val) => val === key);

      if (isKey) {
        EnabledInputs[key] = !value;
      }
    });
  });
  onBeforeMount(() => {
    if (!(bot.value?.system || bot.value?.state)) return;
    if (bot.value.state.toLowerCase() !== "EVERYONE".toLowerCase()) {
      const varasRecord = varas as unknown as JsonVaras;
      const courts: selectCourts[] = [];

      const system = bot.value?.system.toUpperCase() as unknown as keySystems;
      const state = bot.value?.state.toUpperCase() as unknown as keyStates;

      const courtsJson = varasRecord[system][state];

      Object.entries(courtsJson).map(([key, value], index) => {
        courts.push({ value: key, text: value, id: index });
      });
      courtOptions.value.push(...courts);
    }
  });
  onUnmounted(() => {
    Object.entries(EnabledInputs).forEach(([key]) => {
      EnabledInputs[key] = false;
    });
    bot.value = null;
  });
}
