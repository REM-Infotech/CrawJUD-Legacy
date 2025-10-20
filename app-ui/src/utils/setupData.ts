export default function () {
  function getDate() {
    const currentDate = new Date();
    let day = currentDate.getDate().toString();
    let month: string | number = currentDate.getMonth();

    const year = currentDate.getFullYear();
    if (day.length === 1) day = `0${day}`;
    if (month.toString().length === 1) month = `0${month + 1}`;

    return `${year}-${month}-${day}`;
  }

  return { getDate };
}
