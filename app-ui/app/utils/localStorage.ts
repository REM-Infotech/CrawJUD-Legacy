class localStorage {
  public itemStore = ref<Record<string, any>>({});

  getItem(it: string) {
    return this.itemStore.value[it] || "";
  }

  setItem(name: string, value: string) {
    this.itemStore.value[name] = value;
  }
}

export default new localStorage();
