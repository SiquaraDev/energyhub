-- Bancos por serviço (database-per-service, Fase 15) para o `docker compose`.
--
-- O entrypoint da imagem oficial do PostgreSQL executa os arquivos .sql/.sh de
-- /docker-entrypoint-initdb.d APENAS no PRIMEIRO init de um volume de dados vazio. Ou seja: num
-- clone novo, `docker compose up -d` cria estes bancos automaticamente; num volume já inicializado,
-- este script NÃO roda de novo — recrie com `docker compose down -v` (apaga os dados) para reexecutar.
--
-- O banco `energyhub` (usado pelo monólito `energyhub-api`) é criado pelo POSTGRES_DB do serviço
-- postgres; aqui criamos apenas os dos 5 microsserviços. Rodam como o superusuário `energyhub`
-- (POSTGRES_USER), então cada banco nasce com esse dono — que é o mesmo usuário das *_DATABASE_URL.
--
-- Sem estes bancos, cada microsserviço falha o `metadata.create_all` no startup
-- (asyncpg InvalidCatalogNameError) e entra em crash-loop.

CREATE DATABASE authdb;
CREATE DATABASE clientdb;
CREATE DATABASE contractdb;
CREATE DATABASE financialdb;
CREATE DATABASE auditdb;
