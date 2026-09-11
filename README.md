# Tela de Termos (Conciliação & Faturamento)

## 1. Visão Geral e Finalidade

A Tela de Termos funciona como um painel operacional e gerencial projetado para centralizar o acompanhamento dos termos de faturamento e sua respectiva conciliação com os dados de medição.

**Objetivo Central:** Transformar registros brutos de faturamento em decisões de trabalho organizadas, identificando divergências, responsáveis, ações pendentes e filas operacionais.

## Dashboard - Termos

![Dashboard - Termos](imagens/termos/01_dashboard.png)

## Detalhamento de Termos

![Detalhamento de Termos](imagens/termos/02_detalhamento_termos.png)

## Principais Capacidades da Tela

- **Importação & Exportação:** Carga de planilhas `.xlsx` de termos e exportação dos dados consolidados e conciliados.
- **Conciliação Automatizada:** Relação bidirecional entre dados do termo (origem) e dados da medição (destino).
- **Gestão Operacional:** Mapeamento de pendências, definição de executores (Stefanini vs. Prodesp) e direcionamento para filas operacionais.
- **Análise de Impacto:** Monitoramento de divergências financeiras e identificação de gargalos por status e prioridades.

## 2. Conceitos-Chave da Regra de Negócio

Para garantir a correta interpretação do painel, os conceitos do domínio estão estruturados abaixo:

### Unidades de Informação

- **Termo:** Registro inicial representando o período de competência, Ordem de Serviço (OS) externa, projeto, unidade cliente, horas atreladas, valor previsto e status.
- **Medição:** Dados de confirmação do faturamento informando ID da medição, valor medido, horas medidas e status da medição.
- **Conciliação:** O cruzamento efetuado entre Termo e Medição que determina o estado operacional do faturamento.

## 3. Arquitetura e Divisão de Responsabilidades

O sistema adota uma separação estrita de responsabilidades entre Front-end e Back-end. O Front-end não calcula regras de negócio ou divergências; apenas consome e apresenta os dados tratados pela API.

## Exemplo de Payload Retornado pela API

![Exemplo de Payload Retornado pela API](imagens/termos/03_payload_api.png)

## 4. Fluxo de Importação e Exportação

![Fluxo de Importação](imagens/termos/04_fluxo_importacao.png)

### Importação (.xlsx)

- **Validação de Formato:** Apenas arquivos `.xlsx` são permitidos via explorador ou drag-and-drop. Outros formatos são rejeitados no cliente.
- **Processamento:** Exibe estado de carregamento (*loading*) enquanto o backend processa a planilha.
- **Tratamento de Erros:** Caso ocorram falhas técnicas não amigáveis da API, o sistema exibe uma mensagem genérica orientando a revisão dos dados.

### Exportação de Planilha Conciliada

- **Ação:** O usuário aciona "Exportar Planilha de Conciliação".
- **Comportamento da UI:** O botão é bloqueado durante o download para evitar requisições duplicadas.
- **Arquivo Retornado:** `Planilha_de_Conciliacao.xlsx`.
- **Notificação:** Toast lateral informa os status: Em andamento, Concluído ou Erro.

## 5. Estrutura da Interface e Dashboard

A interface é dividida em três blocos funcionais: Cabeçalho & Ações, Dashboard Gerencial e Detalhamento dos Termos.

## Dashboard

![Dashboard](imagens/termos/05_dashboard.png)

## Detalhamento

![Detalhamento](imagens/termos/06_detalhamento.png)

### 5.1 KPIs Principais

- **Resultado da Importação:** Define a escala do lote analisado (Qtd. Termos, Horas Totais, Valor Financeiro).
- **Associação:** Mede termos pareados com uma medição.
- **Associado:** Campo `medicaoId` preenchido.
- **Não encontrado:** Ausência de medição associada. *(Nota: Não significa divergência)*.
- **Divergências:** Filtra a volumetria onde existe divergência. Clicar no KPI aplica o filtro diretamente na tabela de detalhamento.

### 5.2 Status Prioritários

- Painel dinâmico cujas categorias são extraídas dos dados da API.
- **Ordenação:** Por maior Valor Total acumulado (critério primário) e Quantidade de Registros (critério de desempate).
- **Exibição:** Apresenta quantidade, valor financeiro total, posição e participação percentual.

### 5.3 Filas Operacionais

Agrupamento de tarefas por responsável ou providência necessária:

![Filas Operacionais](imagens/termos/07_filas_operacionais.png)

- **Ações da Stefanini:** Demandas cujo executor é a equipe Stefanini.
- **Aguardando Prodesp:** Demandas sob responsabilidade da Prodesp.
- **Documentação e Validação:** Concentra termos não alocados, divergentes ou com executores não classificados.
- **Ação Padrão para não alocado:** Validar alocação do Termo.
- **Sem Pendências:** Agrupa registros considerados no Conforme (sem ações operacionais pendentes no momento).

## 6. Atributos da Conciliação e Regras de Exibição

## 7. Detalhamento e Regras de Negócio da Tabela

A aba de detalhamento apresenta os termos individualmente após o processamento dos dados, permitindo consultar registros, aplicar filtros combinados e gerenciar ações pendentes.

![Detalhamento e Regras de Negócio da Tabela - Parte 1](imagens/termos/08_detalhamento_tabela_1.png)

![Detalhamento e Regras de Negócio da Tabela - Parte 2](imagens/termos/09_detalhamento_tabela_2.png)

### 7.1 Consolidação de Registros Repetidos

O back-end fica responsável por realizar a junção da tabela termos com medições, categorias e ações. Se um status possui múltiplas ações associadas, no resultado pode retornar mais de uma linha para o mesmo `itemTermoId`.

Para evitar itens duplicados na listagem, o front-end executa uma consolidação preventiva:

- Mapeia os registros utilizando `itemTermoId` como chave única.
- Em duplicidades, aplica a seguinte regra de precedência:
  - **Prioridade 1:** O registro marcado com `divergente = true`.
  - **Prioridade 2:** Caso ambos tenham a mesma situação de divergência, mantém o registro com maior completude de dados (`medicaoId`, `statusMedicao`, `executorAcao`, `proximaAcao`, `statusTermos`).
- Converte o mapa consolidado em lista para consumo do Dashboard e da Tabela.

![Função de Consolidação de Termos por ID](imagens/termos/10_consolidar_termos.png)

> **Atenção:** Múltiplos registros vindos da API no mesmo `itemTermoId` são consolidados. Porém, um termo com múltiplas pendências operacionais (ex: Não Alocado e Divergência) aparecerá de forma intencional nos dois grupos de ação do Dashboard sem duplicar a tabela final.

### 7.2 Distribuição nas Filas Operacionais

Após a consolidação, o front-end categoriza os termos em quatro filas operacionais.

### 7.3 Agrupamento por Ação

Dentro de cada fila, os itens são agrupados por ações operacionais específicas (ex: *Validar alocação do Termo*, *Divergência*, *Sem Ação*):

- Quantidade total de termos;
- Valor financeiro acumulado;
- Volume total de horas;
- Descrição da próxima ação.

Ao selecionar uma ação ou fila no Dashboard, a tabela de detalhamento abre automaticamente aplicando esse contexto.

### 7.4 Filtros Disponíveis na Tabela

> **Regra de Ouro:** O frontend nunca calcula a divergência comparando valores ou horas. Ele consome estritamente o booleano `divergente` retornado pelo back-end.

### 7.5 Paginação e Comportamento

- **Tamanho fixo:** 20 registros por página.
- **Cálculo dinâmico:** Atualiza o total de registros filtrados, quantidade de páginas e limites de exibição (*slice*).
- **Reset de Página:** Qualquer alteração em filtros, busca ou seleção de filas no Dashboard reinicia a tabela automaticamente na primeira página.

### 7.6 Resumo das Matrizes de Estado

Para evitar interpretações errôneas no desenvolvimento e na operação, considere que estes atributos representam dimensões diferentes e podem coexistir:

- **Não alocado:** Pendência na alocação do profissional é diferente de Divergência.
- **Sem medição:** Termo não associado é diferente de Divergência.
- **Fluxo Conforme:** Processo sem travamento operacional pendente (mas que pode possuir divergência financeira).
- **Próxima Ação vs. Status:** Status é a etapa do processo; Próxima Ação é a providência a ser tomada.

## Detalhamento Final