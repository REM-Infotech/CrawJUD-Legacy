interface BotStartResponse extends AxiosResponse {
  data: {
    message?: string;
    pid?: string;
  };
}
