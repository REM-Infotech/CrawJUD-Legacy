import crawjud2 from "~/assets/img/crawjud2.png";

class CrawJUDNotification {
  constructor() {}

  show(args = { title: "CrawJUD" } as KeywordArgs) {
    args.options["icon"] = crawjud2;

    new Notification(args.title || "CrawJUD", args.options);
  }
}

export default new CrawJUDNotification();
