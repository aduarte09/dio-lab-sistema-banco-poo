from abc import ABC, abstractmethod
from datetime import datetime


class PessoaFisica:
    def __init__(self, cpf, nome, data_nascimento):
        self._cpf = cpf
        self._nome = nome
        self._data_nascimento = data_nascimento

    @property
    def nome(self):
        return self._nome

class Cliente(PessoaFisica):
    def __init__(self, cpf, nome, data_nascimento, endereco):
        super().__init__(cpf, nome, data_nascimento)
        self._endereco = endereco
        self._contas = []

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
                "Data": datetime.now().strftime("%d-%m-%Y %H:%M:%s"),
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