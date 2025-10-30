import crawjud2 from "~/assets/img/crawjud2.png";

console.log(crawjud2);

class CrawJUDNotification {
  constructor() {}

  show(args = { title: "CrawJUD" } as KeywordArgs) {
    new Notification(args.title || "CrawJUD", args.options);
  }
}

export default new CrawJUDNotification();
