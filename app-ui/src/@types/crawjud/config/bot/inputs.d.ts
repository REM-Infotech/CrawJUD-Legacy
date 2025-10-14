interface TypeFormBot {
  bot_id: bot_id;
  xlsx: FileInputType;
  creds: TextInput;
  parte_name: TextInput;
  doc_parte: TextInput;
  data_inicio: DateTextInput;
  data_fim: DateTextInput;
  polo_parte: TextInpu;
  state: TextInput;
  varas: TextListInput;
  client: TextInput;
  otherfiles: FileInputType;
  confirm_fields: BooleanInput;
  periodic_task: BooleanInput;
  days_task: TextListInput;
  task_hour_minute: DateTextInput;
  task_name: TextInput;
  email_notify: TextInput;
  token: TextInput;
}
