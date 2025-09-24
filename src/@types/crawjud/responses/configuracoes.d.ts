interface ResponseUsers extends AxiosResponse {
  data: {
    database?: UsersRecord[];
  };
}
