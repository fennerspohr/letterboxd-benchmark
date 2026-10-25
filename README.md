# Resumo do Projeto — Letterboxd Benchmark

O projeto consiste em uma API CRUD para filmes, utilizando dados do Letterboxd, com o objetivo de realizar testes de carga e comparar o desempenho do banco de dados em diferentes cenários.

## Ferramentas utilizadas

- **Python:** implementação da API e scripts para preparação e importação dos dados.
- **FastAPI:** criação dos endpoints da API REST.
- **MongoDB 7.0:** banco de dados NoSQL utilizado nos experimentos.
- **Docker e Docker Compose:** execução e gerenciamento do MongoDB em um contêiner.
- **Apache JMeter 5.6.3:** execução dos testes de carga.
- **Java 21:** ambiente necessário para executar o JMeter.
- **Pydantic:** validação e estruturação dos dados recebidos e retornados pela API.
- **PyMongo:** comunicação entre a API Python e o MongoDB.

## O que foi implementado

- Preparação e normalização dos dados do Letterboxd.
- Geração de dois conjuntos de dados: um com **20 mil filmes** e outro com **50 mil filmes**.
- Implementação de uma API CRUD com operações para criar, consultar, atualizar e excluir filmes.
- Implementação de filtros nas consultas, incluindo ano e avaliação mínima.
- Criação de endpoints administrativos para adicionar e remover um índice secundário sobre o campo `date` no MongoDB.
- Configuração do ambiente de testes com Docker Compose.
- Criação de um plano de testes no JMeter com requisições de leitura e escrita.

## Como foram realizados os testes

Os testes de carga foram realizados com o Apache JMeter. A configuração inicial utilizava 10 usuários virtuais, rampa de inicialização de 5 segundos e duração de 60 segundos.

Após a realização dos experimentos iniciais, foi definida uma configuração com maior carga para uma nova rodada de testes:

- **Usuários virtuais:** 100 threads.
- **Ramp-up:** 10 segundos.
- **Duração:** 180 segundos.
- **Limite de resultados das consultas:** 1.000 filmes por requisição, utilizando o parâmetro `limit=1000` no endpoint `GET /movies`.

O plano contempla dois tipos principais de operações:

- **Leituras:** consultas à lista de filmes.
- **Escritas:** criação, atualização e exclusão de filmes. Essas operações são executadas em sequência, utilizando o identificador retornado pela criação para atualizar e excluir o mesmo registro.

Foram consideradas três distribuições de carga:

- **50% de leituras e 50% de escritas**;
- **75% de leituras e 25% de escritas**;
- **25% de leituras e 75% de escritas**.

## Experimentos realizados com MongoDB

Os experimentos iniciais combinaram diferentes tamanhos de conjuntos de dados, proporções de leitura e escrita e configurações de índices.

| Tamanho do conjunto | Índice secundário | Distribuições testadas |
|---|---|---|
| 20 mil filmes | Sem índice | 50% leitura / 50% escrita |
| 20 mil filmes | Com índice | 50% / 50%, 75% / 25% e 25% / 75% |
| 50 mil filmes | Sem índice | 50% / 50%, 75% / 25% e 25% / 75% |
| 50 mil filmes | Com índice | 50% / 50%, 75% / 25% e 25% / 75% |

O índice secundário utilizado nos experimentos foi criado sobre o campo `date`, correspondente ao ano do filme.

### Nova rodada de testes

Para aumentar a carga de trabalho e investigar diferenças de desempenho mais expressivas, foi definida uma nova configuração com:

- **50 mil filmes**;
- **100 usuários virtuais**;
- **Ramp-up de 10 segundos**;
- **Duração de 180 segundos**;
- **Consultas com `limit=1000`**;
- **Comparação entre as configurações com e sem índice secundário**;
- **Manutenção das três distribuições de leitura e escrita**.

A nova rodada busca avaliar o comportamento da API e do banco de dados sob maior concorrência e com maior volume de dados retornados por consulta.

## Métricas coletadas

Os resultados são coletados pelo JMeter e incluem:

- **Tempo de resposta (latência):** tempo necessário para concluir as requisições.
- **Throughput:** quantidade de requisições processadas por unidade de tempo.
- **Taxa de erros:** proporção de requisições que falharam durante os testes.

Essas métricas permitem comparar o comportamento do sistema nos diferentes cenários de carga e configurações de índice.

# T2
| Componente | Alteração |
|---|---|
| `scripts/import_dataset.py` | Mantido como importador direto para o MongoDB |
| `scripts/import_dataset_http.py` | Criado para importar por HTTP |
| `app/main.py` | Nenhuma alteração necessária no endpoint `POST /movies` |
| Nginx | Utilizado como ponto de entrada das requisições |
| MongoDB | Recebe os dados por meio das instâncias da API |