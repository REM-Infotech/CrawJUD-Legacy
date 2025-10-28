<template>
  <Transition>
    <div v-if="isLogged" class="header-content">
      <BNavbar v-b-color-mode="'dark'" toggleable="lg" variant="secondary" class="rounded">
        <BNavbarBrand href="#navbar-overview">NavBar</BNavbarBrand>
        <BNavbarToggle target="nav-collapse" />
        <BCollapse id="nav-collapse" is-nav>
          <BNavbarNav>
            <BNavItem href="#navbar-overview">Link</BNavItem>
            <BNavItem href="#navbar-overview" disabled>Disabled</BNavItem>
          </BNavbarNav>
          <!-- Right aligned nav items -->
          <BNavbarNav class="ms-auto mb-2 mb-lg-0">
            <BNavItemDropdown text="Lang" right>
              <BDropdownItem>EN</BDropdownItem>
              <BDropdownItem>ES</BDropdownItem>
              <BDropdownItem>RU</BDropdownItem>
              <BDropdownItem>FA</BDropdownItem>
            </BNavItemDropdown>
            <BNavItemDropdown right>
              <!-- Using 'button-content' slot -->
              <template #button-content>
                <em>User</em>
              </template>
              <BDropdownItem>Profile</BDropdownItem>
              <BDropdownItem>Sign Out</BDropdownItem>
            </BNavItemDropdown>
          </BNavbarNav>
          <BNavForm class="d-flex">
            <BFormInput class="me-2" placeholder="Search" />
            <BButton type="submit" variant="outline-success">Search</BButton>
          </BNavForm>
        </BCollapse>
      </BNavbar>
    </div>
  </Transition>
</template>

<script setup lang="ts">
const route = useRoute();
const isLogged = computed(() => route.name !== "index");
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
  padding: 5px;
}

.header-content {
  height: 100%;
  max-height: 70px;
  padding: 0.3em;
}
</style>
