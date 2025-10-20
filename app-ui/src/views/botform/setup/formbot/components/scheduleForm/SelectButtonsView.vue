<script setup lang="ts">
const props = defineProps({
  elements: {
    type: Array as () => SelectProperties[],
    default: () => [],
  },
  modelValue: {
    type: Array as () => string[],
    default: () => [],
  },
});

const emits = defineEmits(["update:modelValue"]);

function sendUpdate(event: Event) {
  const ev: HTMLInputElement = event.target as unknown as HTMLInputElement;

  const newValue = [...props.modelValue];
  const index = newValue.indexOf(ev.name);

  if (ev.checked) {
    if (index === -1) {
      newValue.push(ev.name);
    }
  } else {
    if (index !== -1) {
      newValue.splice(index, 1);
    }
  }

  emits("update:modelValue", newValue);
}
</script>

<template>
  <div
    class="btn-group overflow-x-auto"
    role="group"
    id="btnGroup"
    aria-label="Basic checkbox toggle button group"
  >
    <div class="p-1" v-for="item in props.elements" :key="item.id">
      <input
        type="checkbox"
        class="btn-check"
        :id="item.id"
        :name="item.name"
        autocomplete="off"
        @input="sendUpdate($event)"
      />
      <label class="btn btn-outline-primary" :for="item.id">{{ item.label }}</label>
    </div>
  </div>
</template>

<style scoped>
#btnGroup {
  width: 100%;
}
</style>
