import { type Component } from "vue";

// Importação centralizada de todos os componentes do formulário
import CourtInputView from "@/views/botform/setup/formbot/components/principalForm/courtinput/CourtInputView.vue";
import AnotherFilesInputView from "@/views/botform/setup/formbot/components/principalForm/files/AnotherFilesInputView.vue";
import PrincipalFileInputView from "@/views/botform/setup/formbot/components/principalForm/files/PrincipalFileInputView.vue";
import ClasseParteSelectView from "@/views/botform/setup/formbot/components/principalForm/inputs/busca_processo/ClasseParteSelectView.vue";
import DocumentParteInputView from "@/views/botform/setup/formbot/components/principalForm/inputs/busca_processo/DocumentParteInputView.vue";
import ParteNameInputView from "@/views/botform/setup/formbot/components/principalForm/inputs/busca_processo/ParteNameInputView.vue";
import ConfirmInputView from "@/views/botform/setup/formbot/components/principalForm/inputs/ConfirmInputView.vue";
import TokenInputView from "@/views/botform/setup/formbot/components/principalForm/inputs/TokenInputView.vue";
import DataFimView from "@/views/botform/setup/formbot/components/principalForm/inputs/data_inputs/DataFimView.vue";
import DataInicioView from "@/views/botform/setup/formbot/components/principalForm/inputs/data_inputs/DataInicioView.vue";
import SelectClientView from "@/views/botform/setup/formbot/components/principalForm/selects/SelectClientView.vue";
import SelectCredentialsView from "@/views/botform/setup/formbot/components/principalForm/selects/SelectCredentialsView.vue";
import SelectStateView from "@/views/botform/setup/formbot/components/principalForm/selects/SelectStateView.vue";
import EnableScheduleView from "@/views/botform/setup/formbot/components/scheduleForm/EnableScheduleView.vue";
import ScheduleTaskFormView from "@/views/botform/setup/formbot/components/scheduleForm/ScheduleTaskFormView.vue";

/**
 * Interface que define todos os componentes disponíveis no formulário do bot
 */
export interface BotFormComponents {
  CourtInputView: Component;
  AnotherFilesInputView: Component;
  PrincipalFileInputView: Component;
  ClasseParteSelectView: Component;
  DocumentParteInputView: Component;
  ParteNameInputView: Component;
  ConfirmInputView: Component;
  TokenInputView: Component;
  DataFimView: Component;
  DataInicioView: Component;
  SelectClientView: Component;
  SelectCredentialsView: Component;
  SelectStateView: Component;
  EnableScheduleView: Component;
  ScheduleTaskFormView: Component;
}

/**
 * Composable que centraliza o registro de todos os componentes do formulário do bot
 *
 * Esta abordagem:
 * - Centraliza todas as importações em um local
 * - Facilita a manutenção e organização
 * - Torna claro quais componentes estão disponíveis
 * - Permite tree-shaking eficiente
 *
 * @returns Objeto contendo todos os componentes do formulário
 */
export function useBotFormComponents(): BotFormComponents {
  return {
    CourtInputView,
    AnotherFilesInputView,
    PrincipalFileInputView,
    ClasseParteSelectView,
    DocumentParteInputView,
    ParteNameInputView,
    ConfirmInputView,
    TokenInputView,
    DataFimView,
    DataInicioView,
    SelectClientView,
    SelectCredentialsView,
    SelectStateView,
    EnableScheduleView,
    ScheduleTaskFormView,
  };
}
