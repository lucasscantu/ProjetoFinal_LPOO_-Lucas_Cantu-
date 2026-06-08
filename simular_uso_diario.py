"""
Simulador de uso diário do Sistema de Catraca Eletrônica.

A cada segundo, gera uma tentativa aleatória de passagem (usuário + catraca
+ sentido) e dispara a validação real — passando pelos padrões State (estado
da catraca) e Strategy (regra por tipo de usuário). Cada tentativa é
PERSISTIDA no histórico, exatamente como aconteceria no uso real.

Interrompa com Ctrl+C para ver as estatísticas da rodada.

Uso:
    python simular_uso_diario.py

Pré-requisitos:
    - Banco populado (rode antes:  python seed_data.py)
"""
import ctypes
import os
import random
import sys
import time
from datetime import datetime

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from control.acesso_controller import AcessoController
from control.catraca_controller import CatracaController
from control.usuario_controller import UsuarioController


# Intervalo entre tentativas (segundos). Altere se quiser ritmo diferente.
INTERVALO_SEG = 1.0


# ---------------------------------------------------------------------------
# Cores ANSI — funciona em terminais Linux/macOS e no Windows Terminal /
# PowerShell 7+ / VS Code. Em cmd.exe antigo, cai automaticamente para
# saída sem cor.
# ---------------------------------------------------------------------------
def _habilitar_cores() -> bool:
    if not sys.stdout.isatty():
        return False
    if os.name == "nt":
        try:
            kernel32 = ctypes.windll.kernel32
            # ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x4
            handle = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
            modo = ctypes.c_ulong()
            kernel32.GetConsoleMode(handle, ctypes.byref(modo))
            kernel32.SetConsoleMode(handle, modo.value | 0x4)
        except Exception:
            return False
    return True


CORES = _habilitar_cores()

def verde(s):    return f"\033[32m{s}\033[0m" if CORES else s
def vermelho(s): return f"\033[31m{s}\033[0m" if CORES else s
def amarelo(s):  return f"\033[33m{s}\033[0m" if CORES else s
def cinza(s):    return f"\033[90m{s}\033[0m" if CORES else s
def negrito(s):  return f"\033[1m{s}\033[0m"  if CORES else s


# ---------------------------------------------------------------------------
def imprimir_cabecalho(qtd_usuarios: int, qtd_catracas: int):
    print("=" * 78)
    print(negrito(" Simulador de Uso Diário — Catraca Eletrônica"))
    print("=" * 78)
    print(f" População do banco:   {qtd_usuarios} usuário(s)   "
          f"|   {qtd_catracas} catraca(s)")
    print(f" Ritmo:                 1 tentativa a cada {INTERVALO_SEG:.0f}s")
    print(f" Encerrar:              Ctrl+C  (mostra estatísticas)")
    print("=" * 78)
    print()


def imprimir_resumo(autorizados: int, negados: int, por_motivo: dict,
                    inicio: datetime):
    total = autorizados + negados
    duracao = (datetime.now() - inicio).total_seconds()

    print()
    print("=" * 78)
    print(negrito(" Encerrado — Estatísticas da Rodada"))
    print("=" * 78)
    print(f"  Duração:              {duracao:6.1f} s")
    print(f"  Total de tentativas:  {total}")
    if total:
        print(f"  {verde('Autorizadas')}:        {autorizados:>4}   "
              f"({autorizados * 100 / total:5.1f}%)")
        print(f"  {vermelho('Negadas')}:           {negados:>4}   "
              f"({negados * 100 / total:5.1f}%)")
    if por_motivo:
        print()
        print("  Motivos de negação (mais frequentes primeiro):")
        for motivo, qtd in sorted(por_motivo.items(), key=lambda x: -x[1]):
            print(f"    {qtd:>3}x  {motivo}")
    print("=" * 78)


# ---------------------------------------------------------------------------
def main():
    acesso_ctrl  = AcessoController()
    usuario_ctrl = UsuarioController()
    catraca_ctrl = CatracaController()

    usuarios = usuario_ctrl.listar_usuarios() or []
    catracas = catraca_ctrl.listar_catracas() or []

    if not usuarios or not catracas:
        print(vermelho("ERRO: o banco está vazio (sem usuários e/ou catracas)."))
        print()
        print("  Rode primeiro:")
        print("      python seed_data.py")
        sys.exit(1)

    imprimir_cabecalho(len(usuarios), len(catracas))

    autorizados = 0
    negados = 0
    por_motivo: dict[str, int] = {}
    inicio = datetime.now()

    try:
        while True:
            u = random.choice(usuarios)
            c = random.choice(catracas)
            sentido = random.choice(["ENTRADA", "SAIDA"])

            ok, motivo = acesso_ctrl.processar_acesso(u.cpf, c.codigo, sentido)

            hora = datetime.now().strftime("%H:%M:%S")
            if ok:
                autorizados += 1
                rotulo = verde("✔ AUTORIZADO")
            else:
                negados += 1
                por_motivo[motivo] = por_motivo.get(motivo, 0) + 1
                rotulo = vermelho("✘ NEGADO    ")

            # Trunca nomes longos para alinhar a coluna
            nome  = (u.nome[:22]).ljust(22)
            tipo  = u.tipo.value.ljust(11)
            sent  = sentido.ljust(7)

            print(f"{cinza('[' + hora + ']')}  {rotulo}  "
                  f"{nome}  {tipo}  → {c.codigo}  {sent}  "
                  f"{cinza(motivo)}")

            time.sleep(INTERVALO_SEG)

    except KeyboardInterrupt:
        imprimir_resumo(autorizados, negados, por_motivo, inicio)


if __name__ == "__main__":
    main()
