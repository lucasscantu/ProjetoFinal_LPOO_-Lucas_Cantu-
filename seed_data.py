"""
Seed do banco de dados — popula o sistema com administradores, usuários e
catracas de exemplo, para facilitar testes e a apresentação.

É idempotente: rodar várias vezes não duplica nem quebra nada (entradas já
existentes são reportadas como "[já há]").

Uso:
    python seed_data.py

Pré-requisitos:
    - PostgreSQL em execução com o schema aplicado (dao/schema.sql).
    - Admin padrão presente (login=admin, senha=admin123), criado pelo schema.
"""
import os
import random
import sys
from datetime import date, timedelta

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from control.administrador_controller import AdministradorController
from control.catraca_controller import CatracaController
from control.usuario_controller import UsuarioController


# Sementes fixas: rodar duas vezes produz os mesmos CPFs.
random.seed(42)


# ---------------------------------------------------------------------------
def cpf_valido() -> str:
    """Gera um CPF com dígitos verificadores corretos (passa na validação)."""
    n = [random.randint(0, 9) for _ in range(9)]
    s1 = sum(n[i] * (10 - i) for i in range(9))
    d1 = 0 if s1 % 11 < 2 else 11 - (s1 % 11)
    n.append(d1)
    s2 = sum(n[i] * (11 - i) for i in range(10))
    d2 = 0 if s2 % 11 < 2 else 11 - (s2 % 11)
    n.append(d2)
    return "".join(map(str, n))


def fmt(d: date) -> str:
    return d.strftime("%d/%m/%Y")


# ---------------------------------------------------------------------------
def seed_admins(ctrl: AdministradorController):
    print("\n[Administradores]")
    extras = [
        # login,   nome,                senha,      perfil,     ativo
        ("carlos", "Carlos Mendes",     "admin123", "ADMIN",    True),
        ("maria",  "Maria Operadora",   "op12345",  "OPERADOR", True),
        ("joao",   "João Noturno",      "op12345",  "OPERADOR", True),
    ]
    for login, nome, senha, perfil, ativo in extras:
        ok, msg = ctrl.salvar_administrador(login, nome, senha, perfil, ativo)
        marca = "[novo ]" if ok else "[já há]"
        print(f"  {marca}  {login:<8}  {perfil:<8}  {nome}")


def seed_catracas(ctrl: CatracaController):
    print("\n[Catracas]")
    items = [
        ("CAT-01", "Entrada Principal — Bloco A"),
        ("CAT-02", "Saída do Estacionamento"),
        ("CAT-03", "Acesso aos Laboratórios"),
        ("CAT-04", "Biblioteca Central"),
        ("CAT-05", "Ginásio Esportivo"),
        ("CAT-06", "Refeitório"),
    ]
    for codigo, local in items:
        ok, msg = ctrl.salvar_catraca(codigo, local)
        marca = "[novo ]" if ok else "[já há]"
        print(f"  {marca}  {codigo}  {local}")

    # Coloca uma catraca em manutenção para deixar a base com variedade.
    cat = ctrl.buscar_por_codigo("CAT-05")
    if cat and cat.nome_estado() != "Manutencao":
        ok, msg = ctrl.alternar_manutencao("CAT-05")
        print(f"  [estado] {msg}")
    else:
        print("  [estado] CAT-05 já estava em Manutenção (ou não existe)")


def seed_usuarios(ctrl: UsuarioController):
    print("\n[Usuários]")
    hoje = date.today()

    pessoas = [
        # Nome,                tipo,          ativo, validade (None p/ funcionário)
        ("Ana Souza",          "Aluno",       True,  hoje + timedelta(days=90)),
        ("Bruno Lima",         "Aluno",       True,  hoje + timedelta(days=180)),
        ("Carla Mendonça",     "Aluno",       True,  hoje + timedelta(days=30)),
        ("Diego Castro",       "Aluno",       True,  hoje + timedelta(days=200)),
        ("Eduarda Reis",       "Aluno",       True,  hoje + timedelta(days=60)),
        ("Felipe Marinho",     "Aluno",       True,  hoje + timedelta(days=15)),
        ("Gabriela Pinto",     "Aluno",       False, hoje + timedelta(days=10)),  # inativo
        ("Henrique Alves",     "Aluno",       True,  hoje - timedelta(days=5)),   # plano vencido
        ("Isabela Cardoso",    "Funcionario", True,  None),
        ("José Carvalho",      "Funcionario", True,  None),
        ("Karla Nunes",        "Funcionario", True,  None),
        ("Leandro Tavares",    "Funcionario", False, None),                      # afastado
        ("Mariana Pessoa",     "Visitante",   True,  hoje + timedelta(days=2)),
        ("Nilton Borges",      "Visitante",   True,  hoje + timedelta(days=1)),
        ("Olívia Ramos",       "Visitante",   True,  hoje - timedelta(days=1)),  # vencido
        ("Paulo Vinhas",       "Visitante",   False, hoje + timedelta(days=5)),  # inativo
    ]

    for nome, tipo, ativo, validade in pessoas:
        cpf = cpf_valido()
        val_str = fmt(validade) if validade else ""
        ok, msg = ctrl.salvar_usuario(cpf, nome, tipo, ativo, val_str)
        marca = "[novo ]" if ok else "[já há]"
        situacao = "ativo  " if ativo else "inativo"
        val_show = val_str if val_str else "—         "
        print(f"  {marca}  {cpf}  {tipo:<11}  {situacao}  val={val_show:<10}  {nome}")


# ---------------------------------------------------------------------------
def main():
    print("=" * 70)
    print(" SEED — Sistema de Catraca Eletrônica")
    print("=" * 70)

    adm = AdministradorController()
    usu = UsuarioController()
    cat = CatracaController()

    # Autentica como o admin padrão (criado pelo schema.sql).
    ok, msg, conta = adm.autenticar("admin", "admin123")
    if not ok:
        print(f"\nERRO: não foi possível autenticar como admin padrão.")
        print(f"  -> {msg}")
        print(f"  -> Verifique se aplicou o dao/schema.sql no banco.")
        sys.exit(1)

    print(f"\nLogado como: {conta.nome} ({conta.perfil.value})")

    seed_admins(adm)
    seed_catracas(cat)
    seed_usuarios(usu)

    print("\n" + "=" * 70)
    print(" Seed concluído.")
    print(" Próximo passo: rode  python simular_uso_diario.py")
    print("=" * 70)


if __name__ == "__main__":
    main()
