export default defineNuxtComponent({
  setup() {
    const { $router: router } = useNuxtApp();
    router.push({ name: "bots" });
  },
  render() {
    return <></>;
  },
});
