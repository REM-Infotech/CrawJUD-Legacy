import CourtInputView from "../components/principalForm/courtinput/CourtInputView.vue";
import AnotherFilesInputView from "../components/principalForm/files/AnotherFilesInputView.vue";
import PrincipalFileInputView from "../components/principalForm/files/PrincipalFileInputView.vue";
import ClasseParteSelectView from "../components/principalForm/inputs/busca_processo/ClasseParteSelectView.vue";
import DocumentParteInputView from "../components/principalForm/inputs/busca_processo/DocumentParteInputView.vue";
import ParteNameInputView from "../components/principalForm/inputs/busca_processo/ParteNameInputView.vue";
import ConfirmInputView from "../components/principalForm/inputs/ConfirmInputView.vue";
import DataFimView from "../components/principalForm/inputs/data_inputs/DataFimView.vue";
import DataInicioView from "../components/principalForm/inputs/data_inputs/DataInicioView.vue";
import SelectClientView from "../components/principalForm/selects/SelectClientView.vue";
import SelectCredentialsView from "../components/principalForm/selects/SelectCredentialsView.vue";
import SelectStateView from "../components/principalForm/selects/SelectStateView.vue";
import EnableScheduleView from "../components/scheduleForm/EnableScheduleView.vue";
import ScheduleTaskFormView from "../components/scheduleForm/ScheduleTaskFormView.vue";

export default function () {
  return {
    CourtInputView,
    ClasseParteSelectView,
    AnotherFilesInputView,
    PrincipalFileInputView,
    DocumentParteInputView,
    ParteNameInputView,
    ConfirmInputView,
    DataFimView,
    DataInicioView,
    SelectClientView,
    SelectCredentialsView,
    SelectStateView,
    EnableScheduleView,
    ScheduleTaskFormView,
  };
}
