<script setup lang="ts">
import socketio from "@/resources/socketio";
import { BCard, BCardBody, BFormFile, BProgress } from "bootstrap-vue-next";
import { onMounted, reactive, ref, watch } from "vue";

const form = reactive({
  email: "",
  name: "",
  food: null,
  checked: [],
});
const show = ref(true);

const onSubmit = (event: Event) => {
  event.preventDefault();

  alert(JSON.stringify(form));
};

const onReset = (event: Event) => {
  event.preventDefault();
  // Reset our form values
  form.email = "";
  form.name = "";
  form.food = null;
  form.checked = [];
  // Trick to reset/clear native browser form validation state
  show.value = false;
};

const ProgressValue = ref(0);

const FileSocket = ref();

onMounted(() => {
  FileSocket.value = socketio.socket("/files", {});
});

const file = ref<File>();

watch(file, async (file) => {
  FileSocket.value.connect();
  if (!file) return;

  // Chunk Size

  const chunkSize = 8196;

  // Total de Chunks do Arquivo
  const totalChunks = Math.ceil(file.size / 1024);

  // Loop for para os chunks
  for (let i = 0; i < totalChunks; i++) {
    // Inicio do chunk
    const start = i * chunkSize;

    // Fim do chunk
    const end = Math.min(file.size, start + chunkSize);

    const chunk = file.slice(start, end);
    const arrayBuffer = await chunk.arrayBuffer();
    await new Promise<void>((resolve, reject) => {
      FileSocket.value.emit(
        "add_file",
        {
          name: file.name,
          index: i,
          chunksize: chunkSize,
          file_size: file.size,
          total: totalChunks,
          chunk: arrayBuffer,
          content_type: file.type,
        },
        (err: Error | null) => {
          if (err) reject(err);
          else resolve();
        },
      );
    });

    ProgressValue.value = Math.round(((i + 1) * 100) / totalChunks);
    console.log(ProgressValue.value);
  }

  setTimeout(() => {
    ProgressValue.value = 0;
  }, 1500);
});
</script>

<template>
  <div class="form">
    <BCard>
      <BCardBody class="d-flex gap-2">
        <BForm v-if="show" @submit="onSubmit" @reset="onReset">
          <BFormFile v-model="file" label="Hello!" />
          <BProgress :value="ProgressValue" />
        </BForm>
      </BCardBody>
    </BCard>
  </div>
</template>

<style lang="css" scoped>
.form {
  padding: 25px;
}
</style>
