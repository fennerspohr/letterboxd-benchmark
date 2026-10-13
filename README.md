## Resumo do que foi feito — Letterboxd Benchmark

O projeto consiste em uma API CRUD para filmes, utilizando dados do Letterboxd, com o objetivo de realizar testes de carga e comparar o desempenho do banco de dados em diferentes cenários.

### Ferramentas utilizadas
- **Python:** implementação da API e scripts para preparação e importação dos dados.
- **FastAPI:** criação dos endpoints da API REST.
- **MongoDB 7.0:** banco de dados NoSQL utilizado nos experimentos.
- **Docker e Docker Compose:** execução e gerenciamento do MongoDB em um contêiner.
- **Apache JMeter 5.6.3:** execução dos testes de carga.
- **Java 21:** ambiente necessário para executar o JMeter.
- **Pydantic:** validação e estruturação dos dados recebidos e retornados pela API.
- **PyMongo:** comunicação entre a API Python e o MongoDB.

### O que foi implementado
- Preparação e normalização dos dados do Letterboxd.
- Geração de dois conjuntos de dados: um com **20 mil filmes** e outro com **50 mil filmes**.
- Implementação de uma API CRUD com operações para criar, consultar, atualizar e excluir filmes.
- Implementação de filtros nas consultas, incluindo ano e avaliação mínima.
- Criação de endpoints administrativos para adicionar e remover um índice secundário sobre o campo `date` no MongoDB.
- Configuração do ambiente de testes com Docker Compose.
- Criação de um plano de testes no JMeter com requisições de leitura e escrita.

### Como foram realizados os testes
Os testes foram executados com o JMeter, utilizando um grupo de 10 usuários virtuais, rampa de inicialização de 5 segundos e duração de 60 segundos.

O plano contempla dois tipos principais de operações:
- **Leituras:** consultas à lista de filmes.
- **Escritas:** criação, atualização e exclusão de filmes. Essas operações são executadas em sequência, utilizando o identificador retornado pela criação para atualizar e excluir o mesmo registro.

Foram consideradas três distribuições de carga:
- **50% de leituras e 50% de escritas**;
- **75% de leituras e 25% de escritas**;
- **25% de leituras e 75% de escritas**.

### Experimentos realizados com MongoDB
Foram realizados testes combinando diferentes tamanhos de conjuntos de dados, proporções de leitura e escrita e configurações de índices.

| Tamanho do conjunto | Índice secundário | Distribuições testadas |
|---|---|---|
| 20 mil filmes | Sem índice | 50% leitura / 50% escrita |
| 20 mil filmes | Com índice | 50% / 50%, 75% / 25% e 25% / 75% |
| 50 mil filmes | Sem índice | 50% / 50%, 75% / 25% e 25% / 75% |
| 50 mil filmes | Com índice | 50% / 50%, 75% / 25% e 25% / 75% |

Os resultados foram coletados pelo JMeter, que permite observar métricas como tempo de resposta, vazão (*throughput*) e taxa de erros.
