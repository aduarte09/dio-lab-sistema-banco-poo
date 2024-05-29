from abc import ABC, abstractmethod
from datetime import datetime
import textwrap


class PessoaFisica:
    def __init__(self, cpf, nome, data_nascimento):
        self._cpf = cpf
        self._nome = nome
        self._data_nascimento = data_nascimento

    @property
    def nome(self):
        return self._nome
    
    @property
    def cpf(self):
        return self._cpf

class Cliente(PessoaFisica):
    def __init__(self, cpf, nome, data_nascimento, endereco):
        super().__init__(cpf, nome, data_nascimento)
        self._endereco = endereco
        self._contas = []

    @property
    def contas(self):
        return self._contas

    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self._contas.append(conta)

class Historico:
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes
    
    def adicionar_transacao(self, transacao):
        self._transacoes.append({
                "Tipo": transacao.__class__.__name__,
                "Valor": transacao.valor,
                "Data": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            })

class Conta:
    def __init__(self, cliente, numero_conta):
        self._saldo = 0
        self._numero_conta = numero_conta
        self._agencia = "0001"
        self._cliente = cliente 
        self._historico = Historico()

    @property
    def saldo(self):
        return self._saldo
    
    @property
    def numero_conta(self):
        return self._numero_conta
    
    @property
    def agencia(self):
        return self._agencia
    
    @property
    def cliente(self):
        return self._cliente

    @property
    def historico(self):
        return self._historico
    
    @classmethod
    def nova_conta(cls, cliente, numero_conta):
        return cls(cliente, numero_conta)
    
    def sacar(self, valor):
        if valor > self.saldo:
            print("Saque não realizado. Saldo insuficiente.\n")
        elif valor < 0:
            print("Saque não realizado. Valor inválido.\n")
        else:
            self._saldo -= valor
            print("Saque realizado com sucesso.\n")
            return True
        return False

    def depositar(self, valor):
        if valor < 0:
            print("Depósito não realizado. Valor inválido.\n")
        else:
            self._saldo += valor
            print("Depósito realizado com sucesso.\n")
            return True
        return False

class ContaCorrente(Conta):
    def __init__(self, cliente, numero_conta, limite = 500, limite_saques = 3):
        super().__init__(cliente, numero_conta)
        self._limite = limite
        self._limite_saques = 3
        self._numero_saques = 0

    def __str__(self):
        return f'''
        Agência:\t{self.agencia}
        C/C:\t\t{self.numero_conta}
        Titular:\t{self.cliente.nome}
        '''
    
    @property
    def limite(self):
        return self._limite
    
    @property
    def limite_saques(self):
        return self._limite_saques
    
    @property
    def numero_saques(self):
        return self._numero_saques

    def sacar(self, valor):
        if self.numero_saques >= self.limite_saques:
            print("Saque não realizado. Número máximo de saques excedido.\n")
        elif valor > self.saldo:
            print("Saque não realizado. Saldo insuficiente.\n")
        elif valor < 0 or valor > self.limite:
            print("Saque não realizado. Valor inválido.\n")
        else:
            self._saldo -= valor
            self._numero_saques += 1
            print("Saque realizado com sucesso.\n")
            return True
        return False

class Transacao(ABC):
    @property 
    @abstractmethod
    def valor(self):
        pass

    @abstractmethod
    def registrar(self, conta):
        pass

class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor
    
    @property
    def valor(self):
        return self._valor
    
    def registrar(self, conta):
        retorno_transacao = conta.sacar(self.valor)
        if retorno_transacao:
            conta._historico.adicionar_transacao(self)

class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor
    
    @property
    def valor(self):
        return self._valor
    
    def registrar(self, conta):
        retorno_transacao = conta.depositar(self.valor)
        if retorno_transacao:
            conta._historico.adicionar_transacao(self)


def menu():
    menu = '''
MENU
(1) Sacar
(2) Depositar
(3) Extrato
(4) Novo usuário
(5) Nova conta
(6) Exibir contas cadastradas
(0) Sair

Opção escolhida: '''
    return int(input(menu))

def filtrar_cliente(cpf, clientes):
    clientes_filtrados = [cliente for cliente in clientes if cliente.cpf == cpf]
    return clientes_filtrados[0] if clientes_filtrados else None

def recuperar_conta_cliente(cliente):
    if not cliente.contas:
        print("Cliente não possui conta.\n")
        return
    elif len(cliente.contas) > 1:
        numero_contas = len(cliente.contas)
        conta_escolhida = int(input(f"Qual conta deseja escolher? (1-{numero_contas})"))
        if conta_escolhida > 0 and conta_escolhida <= numero_contas:
            return cliente.contas[conta_escolhida - 1]
        else:
            print("Essa conta não existe.\n")
            return
    return cliente.contas[0]

def depositar(clientes):
    cpf = input("Digite o CPF: ")
    cliente = filtrar_cliente(cpf, clientes)
    if not cliente:
        print("Cliente não encontrado.\n")
        return
    valor = float(input("Digite o valor do depósito: "))
    transacao = Deposito(valor)
    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return
    cliente.realizar_transacao(conta, transacao)

def sacar(clientes):
    cpf = input("Digite o CPF: ")
    cliente = filtrar_cliente(cpf, clientes)
    if not cliente:
        print("Cliente não encontrado.\n")
        return
    valor = float(input("Digite o valor do saque: "))
    transacao = Saque(valor)
    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return
    cliente.realizar_transacao(conta, transacao)

def exibir_extrato(clientes):
    cpf = input("Digite o CPF: ")
    cliente = filtrar_cliente(cpf, clientes)
    if not cliente:
        print("Cliente não encontrado.\n")
        return
    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return
    print("\n================ EXTRATO ================")
    transacoes = conta.historico.transacoes
    extrato = ""
    if not transacoes:
        extrato = "Não foram realizadas movimentações."
    else:
        for transacao in transacoes:
            extrato += f"\n{transacao['Tipo']}:\tR$ {transacao['Valor']:.2f}"
    print(extrato)
    print(f"\nSaldo:\tR$ {conta.saldo:.2f}")
    print("==========================================")

def criar_cliente(clientes):
    cpf = input("Digite o CPF (somente número): ")
    cliente = filtrar_cliente(cpf, clientes)
    if cliente:
        print("CPF já cadastrado.\n")
        return
    nome = input("Digite seu nome: ")
    data_nascimento = input("Digite sua data de nascimento (DD/MM/AAAA): ")
    endereco = input("Digite seu endereço (logradouro, número - bairro - cidade / sigla do estado): ")
    cliente = Cliente(cpf, nome, data_nascimento, endereco)
    clientes.append(cliente)
    print("Cliente cadastrado com sucesso.\n")

def criar_conta(numero_conta, clientes, contas):
    cpf = input("Digite o CPF: ")
    cliente = filtrar_cliente(cpf, clientes)
    if not cliente:
        print("Cliente não encontrado.\n")
        return
    conta = ContaCorrente.nova_conta(cliente, numero_conta)
    contas.append(conta)
    cliente.contas.append(conta)
    print("Conta criada com sucesso.\n")

def listar_contas(contas):
    for conta in contas:
        print("=" * 100)
        print(textwrap.dedent(str(conta)))


def main():
    clientes = []
    contas = []

    while True:
        opcao = menu()

        if opcao == 1:
            sacar(clientes)

        elif opcao == 2:
            depositar(clientes)

        elif opcao == 3:
            exibir_extrato(clientes)

        elif opcao == 4:
            criar_cliente(clientes)

        elif opcao == 5:
            numero_conta = len(contas) + 1
            criar_conta(numero_conta, clientes, contas)

        elif opcao == 6:
            listar_contas(contas)

        elif opcao == 0:
            print("Programa encerrado.\n")
            break

        else:
            print("Opção inválida.\n")


main()