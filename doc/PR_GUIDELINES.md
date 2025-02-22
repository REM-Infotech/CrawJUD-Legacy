# Diretrizes para Pull Requests

## Boas Práticas Gerais

- Mantenha PRs pequenos e focados em uma única funcionalidade/correção
- Use títulos descritivos e claros
- Inclua uma descrição detalhada das mudanças
- Referencie issues relacionadas usando #numero_da_issue
- Certifique-se que todos os testes passam antes de submeter
- Mantenha o histórico de commits limpo e organizado

## Formatação e Estilo

- Siga o padrão de código do projeto
- Inclua comentários quando necessário
- Remova código comentado e logs de debug
- Atualize a documentação quando relevante

## Processo de Revisão

1. Solicite review de pelo menos um mantenedor do projeto
2. Responda aos comentários de forma construtiva
3. Faça as alterações solicitadas em novos commits
4. Faça squash dos commits após aprovação

## Limites dos Workflows

Os workflows do projeto possuem os seguintes limites:

- Tamanho máximo do PR: 300 arquivos alterados
- Limite de linhas alteradas: 1000 linhas
- Tempo máximo de execução dos testes: 15 minutos

### Quando os Limites São Excedidos

Se seu PR exceder algum dos limites acima:

1. **Tamanho do PR**
   - Divida o PR em múltiplos PRs menores
   - Foque cada PR em uma funcionalidade específica
   - Crie uma issue de tracking para coordenar os PRs relacionados

2. **Limite de Linhas**
   - Revise se há código duplicado que possa ser refatorado
   - Considere criar bibliotecas compartilhadas para código comum
   - Divida as alterações em PRs menores

3. **Tempo de Execução**
   - Verifique se há testes que podem ser otimizados
   - Considere mover testes longos para uma suite separada
   - Consulte a equipe para avaliar a necessidade de ajustes na infraestrutura

## Checklist Final

- [ ] PR tem título e descrição claros
- [ ] Código segue os padrões do projeto
- [ ] Testes foram adicionados/atualizados
- [ ] Documentação foi atualizada
- [ ] PR está dentro dos limites estabelecidos
- [ ] Revisores foram assignados
