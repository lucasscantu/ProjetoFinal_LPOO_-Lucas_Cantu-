# Documentação do Projeto — Sistema de Catraca Eletrônica

Artefatos de Análise e Projeto de Sistemas (APS — Parte 1) referentes ao Sistema de Catraca Eletrônica, desenvolvido para a disciplina de LPOO (2026/1).

---

## 1. Escopo

O sistema controla o **acesso físico** de pessoas por meio de catracas eletrônicas em uma instituição (ex.: academia). Ele permite cadastrar os usuários e as catracas, simular tentativas de acesso aplicando regras de autorização específicas por tipo de usuário, e manter um histórico auditável de todas as tentativas (autorizadas ou negadas).

**Fora do escopo:** integração com hardware físico real de catracas, biometria, cobrança/financeiro e autenticação de operadores.

---

## 2. Requisitos

### Requisitos Funcionais
- **RF01** — Cadastrar, consultar, alterar e excluir usuários (Aluno, Funcionário, Visitante).
- **RF02** — Cadastrar, consultar, alterar e excluir catracas.
- **RF03** — Validar o CPF do usuário (dígitos verificadores) e o código da catraca (formato `CAT-NN`).
- **RF04** — Simular um acesso informando CPF e código da catraca, decidindo entre autorizar ou negar.
- **RF05** — Aplicar regras de autorização distintas por tipo de usuário.
- **RF06** — Impedir o acesso quando a catraca estiver em manutenção.
- **RF07** — Registrar no histórico **toda** tentativa de acesso, com data/hora, resultado e motivo.
- **RF08** — Listar e filtrar o histórico de acessos (por resultado e por CPF).
- **RF09** — Buscar usuários por nome ou CPF na tela de listagem.
- **RF10** — Exibir uma tela "Sobre" com informações do sistema e do autor.

### Requisitos Não Funcionais
- **RNF01** — Implementação em Python com interface gráfica em Tkinter.
- **RNF02** — Persistência em PostgreSQL através de uma camada DAO.
- **RNF03** — Aplicação de, no mínimo, dois padrões de projeto.
- **RNF04** — Organização do código em pacotes por responsabilidade (model, dao, control, view).
- **RNF05** — Integridade referencial garantida por chaves estrangeiras no banco.

---

## 3. Regras de negócio

| Regra  | Descrição                                                                                         |
|--------|---------------------------------------------------------------------------------------------------|
| RN01   | Catraca em **Manutenção** nega qualquer acesso, independentemente do usuário.                     |
| RN02   | **Aluno** acessa se estiver ativo, com plano válido, no horário entre 06h e 23h.                  |
| RN03   | **Funcionário** acessa se estiver ativo, sem restrição de horário (24h).                          |
| RN04   | **Visitante** acessa se estiver ativo, autorizado, no horário entre 08h e 18h.                    |
| RN05   | Ao autorizar, a catraca executa o ciclo físico liberar → bloquear (passagem única).               |
| RN06   | Toda tentativa (autorizada ou negada) é registrada no histórico com o respectivo motivo.          |
| RN07   | Um usuário ou catraca com acessos registrados não pode ser excluído (integridade do histórico).   |

---

## 4. Diagrama de classes

Ver imagem em [`docs/diagrama_classes.png`](docs/diagrama_classes.png).

O diagrama representa:
- A hierarquia de `Usuario` (abstrata) → `Aluno`, `Funcionario`, `Visitante`.
- A `Catraca` e seus estados (padrão **State**).
- As estratégias de validação de acesso (padrão **Strategy**).
- A `UsuarioFactory` (padrão **Factory**).
- A camada DAO (padrão **DAO**) com `GenericDAO` e DAOs concretos.
- A entidade associativa `Acesso`, ligando `Usuario` e `Catraca` por chaves estrangeiras (N..1 para cada lado).

---

## 5. Modelo de dados (mapeamento objeto-relacional)

| Tabela        | Colunas principais                                                                 |
|---------------|------------------------------------------------------------------------------------|
| `tb_usuarios` | `usu_cpf` (PK), `usu_nome`, `usu_tipo`, `usu_ativo`, `usu_validade`                 |
| `tb_catracas` | `cat_codigo` (PK), `cat_localizacao`, `cat_estado`                                  |
| `tb_acessos`  | `ace_id` (PK), `usu_cpf` (FK), `cat_codigo` (FK), `ace_data_hora`, `ace_tipo`, `ace_autorizado`, `ace_motivo` |

Relacionamento: `tb_acessos` é a **entidade associativa** que materializa o relacionamento N–N entre `tb_usuarios` e `tb_catracas`.

---

## 6. Decisões de projeto

- **Herança de usuário por tabela única** (coluna `usu_tipo`): simplifica o esquema; a subclasse correta é reconstruída pela `UsuarioFactory`.
- **State para a catraca:** modela explicitamente as transições válidas e impede operações inconsistentes (ex.: liberar uma catraca em manutenção).
- **Strategy para autorização:** isola as regras de cada perfil, facilitando a inclusão de novos tipos de usuário sem alterar o controlador.
- **Histórico imutável protegido por FK (`ON DELETE RESTRICT`):** preserva a rastreabilidade dos acessos.
