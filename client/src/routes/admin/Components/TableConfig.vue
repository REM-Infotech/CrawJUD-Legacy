<script setup>
import UsersComponent from "../pages/UsersComponent.vue";
</script>

<template>
  <div class="container-fluid bg-dark rounded rounded-4 bg-opacity-75">
    <ul class="nav nav-tabs" id="TabConfig" role="tablist">
      <li class="nav-item" role="presentation">
        <button
          class="nav-link active"
          id="users-tab"
          data-bs-toggle="tab"
          data-bs-target="#users-tab-pane"
          type="button"
          role="tab"
          aria-controls="users-tab-pane"
          aria-selected="true"
        >
          Usuários
        </button>
      </li>
      <li class="nav-item" role="presentation">
        <button
          class="nav-link"
          id="profile-tab"
          data-bs-toggle="tab"
          data-bs-target="#profile-tab-pane"
          type="button"
          role="tab"
          aria-controls="profile-tab-pane"
          aria-selected="false"
        >
          Profile
        </button>
      </li>
      <li class="nav-item" role="presentation">
        <button
          class="nav-link"
          id="contact-tab"
          data-bs-toggle="tab"
          data-bs-target="#contact-tab-pane"
          type="button"
          role="tab"
          aria-controls="contact-tab-pane"
          aria-selected="false"
        >
          Contact
        </button>
      </li>
    </ul>
    <div class="tab-content" id="TabConfigContent">
      <div
        class="tab-pane fade p-4 show active"
        id="users-tab-pane"
        role="tabpanel"
        aria-labelledby="users-tab"
        tabindex="0"
      >
        <UsersComponent />
      </div>
      <div
        class="tab-pane fade"
        id="profile-tab-pane"
        role="tabpanel"
        aria-labelledby="profile-tab"
        tabindex="0"
      >
        ...
      </div>
      <div
        class="tab-pane fade"
        id="contact-tab-pane"
        role="tabpanel"
        aria-labelledby="contact-tab"
        tabindex="0"
      >
        ...
      </div>
    </div>
  </div>
</template>
