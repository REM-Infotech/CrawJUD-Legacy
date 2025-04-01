<script setup>
import ModalMessage from "./components/ModalMessage.vue";
</script>

<template>
    <ModalMessage />

    <RouterView />
    <BModal
        centered
        id="modal-load"
        no-footer
        no-header
        size="sm"
        body-class="bg-transparent"
        content-class="bg-transparent border-0"
    >
        <div class="text-center">
            <div class="spinner-border text-white" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
        </div>
    </BModal>
</template>

<style>
.hide-content {
    background-color: rgba(255, 255, 255, 0);
}
</style>
