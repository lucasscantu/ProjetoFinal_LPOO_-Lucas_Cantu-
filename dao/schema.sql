-- =====================================================================
-- Esquema do banco de dados do Sistema de Catraca Eletrônica
-- SGBD: PostgreSQL
--
-- Para criar o banco antes (uma vez):
--   CREATE DATABASE lpoo_projeto_[Lucas_Cantu];
-- Depois conecte-se a ele e execute este script:
--   \c lpoo_projeto_[Lucas_Cantu]
--   \i schema.sql
-- =====================================================================

-- ---------------------------------------------------------------------
-- Tabela de administradores (operadores do sistema, com perfil de acesso)
--   ADMIN     -> acesso total (cadastros + operação + admins)
--   OPERADOR  -> apenas operação (simular acesso + histórico)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS tb_administradores (
    adm_id        SERIAL       PRIMARY KEY,
    adm_login     VARCHAR(30)  NOT NULL UNIQUE,
    adm_nome      VARCHAR(120) NOT NULL,
    adm_senha     VARCHAR(128) NOT NULL,   -- SHA-256 hex (64) ou maior
    adm_perfil    VARCHAR(15)  NOT NULL
                  CHECK (adm_perfil IN ('ADMIN', 'OPERADOR')),
    adm_ativo     BOOLEAN      NOT NULL DEFAULT TRUE
);

-- Administrador padrão (login: admin / senha: admin123).
-- Senha em SHA-256 do texto "admin123":
--   240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9
INSERT INTO tb_administradores (adm_login, adm_nome, adm_senha, adm_perfil, adm_ativo)
VALUES ('admin', 'Administrador do Sistema',
        '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9',
        'ADMIN', TRUE)
ON CONFLICT (adm_login) DO NOTHING;

-- ---------------------------------------------------------------------
-- Tabela de usuários (Aluno / Funcionario / Visitante via usu_tipo)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS tb_usuarios (
    usu_cpf       VARCHAR(11)  PRIMARY KEY,
    usu_nome      VARCHAR(120) NOT NULL,
    usu_tipo      VARCHAR(20)  NOT NULL
                  CHECK (usu_tipo IN ('ALUNO', 'FUNCIONARIO', 'VISITANTE')),
    usu_ativo     BOOLEAN      NOT NULL DEFAULT TRUE,
    usu_validade  DATE
);

-- ---------------------------------------------------------------------
-- Tabela de catracas (estado controlado pelo padrão State)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS tb_catracas (
    cat_codigo       VARCHAR(10)  PRIMARY KEY,
    cat_localizacao  VARCHAR(120) NOT NULL,
    cat_estado       VARCHAR(20)  NOT NULL DEFAULT 'Bloqueada'
                     CHECK (cat_estado IN ('Bloqueada', 'Liberada', 'Manutencao'))
);

-- ---------------------------------------------------------------------
-- Tabela de acessos (entidade associativa N–N entre usuário e catraca)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS tb_acessos (
    ace_id          SERIAL       PRIMARY KEY,
    usu_cpf         VARCHAR(11)  NOT NULL,
    cat_codigo      VARCHAR(10)  NOT NULL,
    ace_data_hora   TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ace_tipo        VARCHAR(10)  NOT NULL
                    CHECK (ace_tipo IN ('ENTRADA', 'SAIDA')),
    ace_autorizado  BOOLEAN      NOT NULL,
    ace_motivo      VARCHAR(200),

    CONSTRAINT fk_acesso_usuario
        FOREIGN KEY (usu_cpf)
        REFERENCES tb_usuarios (usu_cpf)
        ON DELETE RESTRICT,

    CONSTRAINT fk_acesso_catraca
        FOREIGN KEY (cat_codigo)
        REFERENCES tb_catracas (cat_codigo)
        ON DELETE RESTRICT
);

-- Índices úteis para consultas/filtros de histórico
CREATE INDEX IF NOT EXISTS idx_acessos_usuario ON tb_acessos (usu_cpf);
CREATE INDEX IF NOT EXISTS idx_acessos_catraca ON tb_acessos (cat_codigo);
CREATE INDEX IF NOT EXISTS idx_acessos_data    ON tb_acessos (ace_data_hora);
