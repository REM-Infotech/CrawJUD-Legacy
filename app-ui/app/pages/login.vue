<script setup lang="ts">
// Define o estado do formulário de login
const FormAuth = reactive({
  login: "",
  password: "",
  remember: false,
});

// Executa o login ao submeter o formulário
async function onSubmitted(ev: Event) {
  ev.preventDefault();
  const form = new FormData();
  Object.entries(FormAuth).forEach(([key, val]) => form.append(key, String(val)));
  await auth.login(form);
}
</script>

<template>
  <BContainer class="mt-auto mb-auto">
    <div class="card card-login">
      <div class="card-body align-self-center">
        <BForm class="form-signin" @submit="onSubmitted">
          <img
            class="mb-4"
            src="../assets/brand/bootstrap-logo.svg"
            alt=""
            width="72"
            height="57"
          />
          <h1 class="h3 mb-3 fw-normal">Please sign in</h1>
          <div class="form-floating">
            <input
              name="login"
              v-model="FormAuth.login"
              class="form-control"
              id="floatingInput"
              placeholder="name@example.com"
            />
            <label for="floatingInput">Email address</label>
          </div>
          <div class="form-floating">
            <input
              v-model="FormAuth.password"
              name="password"
              type="password"
              class="form-control"
              id="floatingPassword"
              placeholder="Password"
            />
            <label for="floatingPassword">Password</label>
          </div>
          <div class="form-check text-start my-3">
            <input
              v-model="FormAuth.remember"
              class="form-check-input"
              type="checkbox"
              :value="false"
              id="checkDefault"
            />
            <label class="form-check-label" for="checkDefault"> Remember me </label>
          </div>
          <button class="btn btn-primary w-100 py-2" type="submit">Sign in</button>
          <p class="mt-5 mb-3 text-body-secondary">&copy; 2017–2025</p>
        </BForm>
      </div>
    </div>
  </BContainer>
</template>

<style lang="css">
.form-signin {
  min-width: 330px;
  padding: 1rem;
}

.form-signin .form-floating:focus-within {
  z-index: 2;
}

.form-signin input[name="login"] {
  margin-bottom: -1px;
  border-bottom-right-radius: 0;
  border-bottom-left-radius: 0;
}

.form-signin input[name="password"] {
  margin-bottom: 10px;
  border-top-left-radius: 0;
  border-top-right-radius: 0;
}

.container {
  max-width: 420px;
}

.card-login {
  background-color: #240135cb;
}
</style>
