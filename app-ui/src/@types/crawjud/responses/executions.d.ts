interface ExecutionsResponse extends AxiosResponse {
  data: {
    data?: ExecutionDataRecord[];
  };
}
