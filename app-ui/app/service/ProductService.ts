class ProductService {
  constructor() {}

  async getProductsMini() {
    return [
      {
        code: 1,
        name: "teste",
        category: "teste",
        quantity: 1,
      },
    ];
  }
}

export default new ProductService();
