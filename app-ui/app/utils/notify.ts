import type { BaseColorVariant } from "bootstrap-vue-next";
import crawjud2 from "~/assets/img/crawjud2.png";

type messageColorVariant = Record<MessageType, keyof BaseColorVariant>;
const MessageColorVariant: messageColorVariant = {
  success: "success",
  error: "danger",
  info: "primary",
  warning: "warning",
};

class CrawJUDNotification {
  constructor() {}

  show(args: KeywordArgs) {
    const { $toast: toast } = useNuxtApp();
    toast.create({
      title: args.title,
      body: args.message,
      variant: MessageColorVariant[args.type],
      modelValue: args.duration,
    });

    new Notification(args.title, {
      body: args.message,
      icon: crawjud2,
    });
  }
}

export default new CrawJUDNotification();
