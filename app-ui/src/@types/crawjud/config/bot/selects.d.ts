interface selectCourts {
  value: string | number | null;
  text: string;
  disabled?: boolean;
  id?: string | number;
}

interface SelectProperties {
  id: string;
  name: string;
  label: string;
}

type SelectCredentialsRefType = [
  { value?: string | null | boolean | number; text?: string; disabled?: boolean },
];
