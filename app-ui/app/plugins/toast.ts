export default defineNuxtPlugin((_) => {
  const toast = useToast();

  return {
    provide: {
      toast,
    },
  };
});
