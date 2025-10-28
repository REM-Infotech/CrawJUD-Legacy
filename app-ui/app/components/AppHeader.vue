<template>
  <div class="heading p-2" data-bs-theme="dark">
    <Transition>
      <nav v-if="!isLogged" class="navbar navbar-expand-lg bg-dark rounded">
        <div class="container-fluid">
          <a class="navbar-brand" href="#">Navbar</a>
          <button
            class="navbar-toggler"
            type="button"
            data-bs-toggle="collapse"
            data-bs-target="#navbarSupportedContent"
            aria-controls="navbarSupportedContent"
            aria-expanded="false"
            aria-label="Toggle navigation"
          >
            <span class="navbar-toggler-icon"></span>
          </button>
          <div class="collapse navbar-collapse" id="navbarSupportedContent">
            <ul class="navbar-nav me-auto mb-2 mb-lg-0">
              <li class="nav-item">
                <NuxtLink class="nav-link" :to="{ name: 'dashboard' }" active-class="active">
                  Dashboard
                </NuxtLink>
              </li>
              <li class="nav-item">
                <NuxtLink class="nav-link" :to="{ name: 'bots' }" active-class="active">
                  Robôs
                </NuxtLink>
              </li>
              <li class="nav-item dropdown">
                <a
                  class="nav-link dropdown-toggle"
                  href="#"
                  role="button"
                  data-bs-toggle="dropdown"
                  aria-expanded="false"
                >
                  Dropdown
                </a>
                <ul class="dropdown-menu">
                  <li><a class="dropdown-item" href="#">Action</a></li>
                  <li><a class="dropdown-item" href="#">Another action</a></li>
                  <li><hr class="dropdown-divider" /></li>
                  <li><a class="dropdown-item" href="#">Something else here</a></li>
                </ul>
              </li>
              <li class="nav-item">
                <a class="nav-link disabled" aria-disabled="true">Disabled</a>
              </li>
            </ul>
            <form class="d-flex" role="search">
              <input
                class="form-control me-2"
                type="search"
                placeholder="Search"
                aria-label="Search"
              />
              <button class="btn btn-outline-success" type="submit">Search</button>
            </form>
          </div>
        </div>
      </nav>
    </Transition>
  </div>
</template>

<script setup lang="ts">
const route = useRoute();
const isLogged = computed(() => route.name === "login" || route.name === "index");
</script>

<style lang="css" scoped>
/* we will explain what these classes do next! */
/* Aplica transição suave de recolhimento vertical usando translateY */
.v-enter-active,
.v-leave-active {
  transition: transform 0.5s ease;
}

.v-enter-from,
.v-leave-to {
  transform: translateY(-60px) scaleY(0.2);
}

.v-enter-to,
.v-leave-from {
  transform: translateY(0) scaleY(1);
}

.p-menubar {
  background: var(--color-maroon-950);
}

.heading {
  position: fixed;
  width: 100%;
  top: 0;
  z-index: 1;
}
</style>
