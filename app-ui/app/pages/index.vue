<script setup lang="jsx">
// Define o estado do formulário de login
const FormLogin = reactive({
  login: "",
  password: "",
  remember: false,
});

// Executa o login ao submeter o formulário
async function onSubmitted(ev) {
  ev.preventDefault();
  const form = new FormData();
  Object.entries(FormLogin).forEach(([key, val]) => form.append(key, String(val)));
  await auth.login(form);
}
</script>

<template>
  <BContainer class="mt-auto mb-auto">
    <div class="card">
      <div class="card-body">
        <div class="d-flex justify-content-center align-items-center">
          <BForm @submit="onSubmitted">
            <BFormFloatingLabel label="Email address" label-for="floatingEmail" class="my-2">
              <BFormInput id="floatingEmail" type="text" placeholder="Email address" />
            </BFormFloatingLabel>
            <BFormFloatingLabel label="Password" label-for="floatingPassword" class="my-2">
              <BFormInput id="floatingPassword" type="password" placeholder="Password" />
            </BFormFloatingLabel>
            <BButton type="submit">Ok</BButton>
          </BForm>
        </div>
      </div>
    </div>
  </BContainer>
</template>

<style lang="css" scoped>
.container {
  margin-top: auto;
  margin-bottom: auto;
}

.card {
  height: 100%;
  max-height: 500px;
  width: 100%;
}
</style>
