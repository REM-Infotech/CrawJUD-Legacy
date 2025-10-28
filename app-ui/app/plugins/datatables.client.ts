import DataTablesCore from "datatables.net-bs5";
import DataTable from "datatables.net-vue3";
import jQuery from "jquery";

// Adiciona as propriedades jQuery e $ ao tipo Window
declare global {
  interface Window {
    jQuery: typeof jQuery;
    $: typeof jQuery;
  }
}

export default defineNuxtPlugin(() => {
  // Garante que o jQuery está no window
  window.jQuery = jQuery;
  window.$ = jQuery;

  DataTable.use(DataTablesCore);
  return {
    provide: {
      DataTable: DataTable,
    },
  };
});
