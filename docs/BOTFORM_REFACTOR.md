# Refatoração do Formulário do Bot - Guia de Migração

## Resumo das Mudanças

Este projeto foi refatorado para tornar as importações e dependências mais claras e coesas, facilitando o desenvolvimento e manutenção.

## Problemas Resolvidos

### Antes da Refatoração
- **Dependências circulares**: Componentes importavam `formSetup` que importava todos os componentes
- **Lógica fragmentada**: Setup dividido em múltiplos arquivos sem organização clara
- **Imports desnecessários**: Componentes importavam o setup completo para acessar apenas o formulário
- **Arquitetura não coesa**: Difícil entender o que cada componente precisava

### Após a Refatoração
- **Dependências explícitas**: Uso de provide/inject para compartilhar estado
- **Composables organizados**: Separação clara de responsabilidades
- **Imports específicos**: Componentes injetam apenas o que precisam
- **Arquitetura coesa**: Fácil entender e manter

## Nova Estrutura

### Composables Criados

#### 1. `useBotFormState.ts`
**Responsabilidade**: Gerenciar todo o estado reativo do formulário

```typescript
// Funções principais:
- useBotFormState() // Para uso direto
- provideBotFormState() // Para prover estado aos filhos
- useBotFormStateInjected() // Para injetar estado
- useBotFormRefsInjected() // Para injetar referências
- useBotFormOptionsInjected() // Para injetar opções
```

**Benefícios**:
- Estado centralizado e tipado
- Injeção específica do que cada componente precisa
- Eliminação de dependências circulares

#### 2. `useBotFormSetup.ts`
**Responsabilidade**: Orquestrar a lógica principal do formulário

```typescript
// Funções principais:
- useBotFormSetup(formState, formRefs, formOptions)
- handleSubmit() // Submissão do formulário
- Lifecycle hooks (onMounted, onBeforeMount, onUnmounted)
```

**Benefícios**:
- Lógica de setup centralizada
- Separação clara de responsabilidades
- Reutilizável e testável

#### 3. `useBotFormComponents.ts`
**Responsabilidade**: Centralizar importação de todos os componentes

```typescript
// Retorna todos os componentes:
- CourtInputView, TokenInputView, etc.
```

**Benefícios**:
- Imports centralizados
- Tree-shaking eficiente
- Fácil manutenção

## Como Usar

### Para Componentes Principais (BotForm.vue)

```vue
<script setup lang="ts">
import { provideBotFormState } from "@/composables/useBotFormState";
import { useBotFormSetup } from "@/composables/useBotFormSetup";
import { useBotFormComponents } from "@/composables/useBotFormComponents";

// 1. Prover estado para componentes filhos
const formState = provideBotFormState();

// 2. Setup principal
const { handleSubmit } = useBotFormSetup(/* parâmetros */);

// 3. Componentes
const { TokenInputView, ConfirmInputView, /* ... */ } = useBotFormComponents();
</script>
```

### Para Componentes Filhos

```vue
<script setup lang="ts">
import { useBotFormStateInjected } from "@/composables/useBotFormState";

// Injeta apenas o que precisa
const { form } = useBotFormStateInjected();
</script>
```

## Compatibilidade

### Componentes Existentes
Os componentes existentes continuam funcionando através de um **bridge de compatibilidade** no arquivo `formSetup.ts` legado.

### Migração Gradual
1. **Imediato**: Componente principal usa novos composables
2. **Futuro**: Componentes filhos podem ser migrados gradualmente
3. **Depreciação**: Setup legado será removido quando todos os componentes forem migrados

## Padrões de Injeção

### Estado Principal
```typescript
const { form, bot, enabledInputs } = useBotFormStateInjected();
```

### Referências
```typescript
const { progressBar, overlayFormSubmit } = useBotFormRefsInjected();
```

### Opções Computadas
```typescript
const { queryCourtOptionsCourt, stateOptions } = useBotFormOptionsInjected();
```

## Benefícios da Nova Arquitetura

1. **Clareza**: Imports explícitos e dependências rastreáveis
2. **Manutenibilidade**: Fácil entender o que cada parte faz
3. **Testabilidade**: Composables podem ser testados isoladamente
4. **Performance**: Tree-shaking mais eficiente
5. **Escalabilidade**: Fácil adicionar novos componentes e funcionalidades
6. **Padrões Vue 3**: Segue as melhores práticas do Composition API

## Próximos Passos

1. **Validação**: Testar todos os fluxos do formulário
2. **Migração Gradual**: Atualizar componentes restantes para usar injeção
3. **Documentação**: Atualizar documentação dos componentes
4. **Limpeza**: Remover arquivos legados quando não utilizados
5. **Testes**: Adicionar testes unitários para os composables

## Exemplos de Migração

### Antes
```vue
<script setup lang="ts">
import formSetup from "@/views/botform/setup/formbot/scripts/formSetup";

const { form, bot, progressBar, handleSubmit, /* ... */ } = formSetup();
</script>
```

### Depois
```vue
<script setup lang="ts">
import { useBotFormStateInjected } from "@/composables/useBotFormState";

// Injeta apenas o que precisa
const { form } = useBotFormStateInjected();
</script>
```

Esta refatoração torna o código mais limpo, maintível e fácil de entender para qualquer desenvolvedor.