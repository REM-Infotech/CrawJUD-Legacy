interface ResponseCredentials extends AxiosResponse {
  data: {
    database?: CredentialsRecord[];
  };
}
