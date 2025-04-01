import moment from "moment";
import "moment/locale/pt-br";

moment.defineLocale("pt-br", {
  months: function (m: moment.Moment) {
    const lista_mes =
      "janeiro_fevereiro_março_abril_maio_junho_julho_agosto_setembro_outubro_novembro_dezembro".split(
        "_",
      );

    for (let i = 0; i < lista_mes.length; i++) {
      lista_mes[i] = lista_mes[i].charAt(0).toUpperCase() + lista_mes[i].slice(1);
    }

    return lista_mes[m.month()];
  },

  monthsShort: function (m: moment.Moment) {
    const lista_mes = "jan_fev_mar_abr_mai_jun_jul_ago_set_out_nov_dez".split("_");

    for (let i = 0; i < lista_mes.length; i++) {
      lista_mes[i] = lista_mes[i].charAt(0).toUpperCase() + lista_mes[i].slice(1);
    }

    return lista_mes[m.month()];
  },

  weekdays: function (m: moment.Moment) {
    const lista_dias_semana =
      "domingo_segunda-feira_terça-feira_quarta-feira_quinta-feira_sexta-feira_sábado".split("_");

    for (let i = 0; i < lista_dias_semana.length; i++) {
      lista_dias_semana[i] =
        lista_dias_semana[i].charAt(0).toUpperCase() + lista_dias_semana[i].slice(1);
    }

    return lista_dias_semana[m.day()];
  },
  weekdaysShort: "dom_seg_ter_qua_qui_sex_sáb".split("_"),
  weekdaysMin: "do_2ª_3ª_4ª_5ª_6ª_sá".split("_"),
  weekdaysParseExact: true,
  longDateFormat: {
    LT: "HH:mm",
    LTS: "HH:mm:ss",
    L: "DD/MM/YYYY",
    LL: "D [de] MMMM [de] YYYY",
    LLL: "D [de] MMMM [de] YYYY [às] HH:mm",
    LLLL: "dddd, D [de] MMMM [de] YYYY [às] HH:mm",
  },
  calendar: {
    sameDay: "[Hoje às] LT",
    nextDay: "[Amanhã às] LT",
    nextWeek: "dddd [às] LT",
    lastDay: "[Ontem às] LT",
    lastWeek: function () {
      return this.day() === 0 || this.day() === 6
        ? "[Último] dddd [às] LT" // Saturday + Sunday
        : "[Última] dddd [às] LT"; // Monday - Friday
    },
    sameElse: "L",
  },
  relativeTime: {
    future: "em %s",
    past: "há %s",
    s: "poucos segundos",
    ss: "%d segundos",
    m: "um minuto",
    mm: "%d minutos",
    h: "uma hora",
    hh: "%d horas",
    d: "um dia",
    dd: "%d dias",
    M: "um mês",
    MM: "%d meses",
    y: "um ano",
    yy: "%d anos",
  },
  dayOfMonthOrdinalParse: /\d{1,2}º/,
  ordinal: (n: number) => `${n}º`,
  invalidDate: "Data inválida",
});

moment.locale("pt-br");

export function convertDate(date: string) {
  return moment(date).format("L LTS");
}
