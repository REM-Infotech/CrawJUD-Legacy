class ProductService {
  constructor() {}

  getProductsMini() {
    return {
      data: [
        {
          id: 1,
          name: "teste",
          category: "teste",
          quantity: 1,
        },
      ],
    };
  }
}

export default new ProductService();
