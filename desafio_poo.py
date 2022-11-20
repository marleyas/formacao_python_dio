from abc import ABC, abstractclassmethod, abstractproperty
from datetime import datetime
import textwrap


class Cliente:
    def __init__(self, endereco):
        self._endereco = endereco
        self._contas = []
    
    @property
    def endereco(self):
        return self._endereco

    @property
    def contas(self):
        return self._contas

    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self.contas.append(conta)


class PessoaFisica(Cliente):
    def __init__(self, nome, cpf, data_nascimento, endereco):
        super().__init__(endereco)
        self._nome = nome
        self._cpf = cpf
        self._data_nascimento = data_nascimento

    @property
    def nome(self):
        return self._nome

    @property
    def cpf(self):
        return self._cpf

    @property
    def data_nascimento(self):
        return self._data_nascimento


class Conta:
    def __init__(self, numero, cliente):
        self._saldo = 0.0
        self._numero = numero
        self._agencia = "0001"
        self._cliente = cliente
        self._historico = Historico()

    @property
    def saldo(self):
        return self._saldo

    @property
    def numero(self):
        return self._numero

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
    def nova_conta(cls, cliente, numero):
        return cls(numero, cliente)

    def sacar(self, valor):
        saldo = self.saldo
        excedeu_saldo = valor > saldo
        if excedeu_saldo:
            print("\nOperação falhou! Você não tem saldo suficiente.")
        elif valor > 0:
            self._saldo -= valor
            print("\nSaque realizado com sucesso!")
            return True
        else:
            print("\nOperação falhou! O valor informado é inválido.")
            return False
        return False

    def depositar(self, valor):
        if valor > 0:
            self._saldo += valor
            print("\nDepósito realizado com sucesso!")
            return True
        else:
            print("\nOperação falhou! O valor informado é inválido.")
            return False
        return True


class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite=500.0, limite_saques=3):
        super().__init__(numero, cliente)
        self._limite = limite
        self._limite_saques = limite_saques

    @property
    def limite(self):
        return self._limite
    
    @property
    def limite_saques(self):
        return self._limite_saques

    def sacar(self, valor):
        numero_saques = len(
            [transacao for transacao in self.historico.transacoes if transacao['tipo'] == Saque.__name__]
        )
        excedeu_saques = numero_saques >= self.limite_saques
        excedeu_limite = valor > self.limite
        if excedeu_limite:
            print("\nOperação falhou! O valor do saque excede o limite.")
            return False
        elif excedeu_saques:
            print("\nOperação falhou! Você excedeu o número máximo de saques.")
            return False
        else:
            return super().sacar(valor)

    def __str__(self):
        return f"""\
            Agência:\t{self.agencia}
            C/C:\t\t{self.numero}
            Titular:\n{self.cliente.nome}        
        """

    def depositar(self, valor):
        if valor > 0:
            self._saldo += valor
            print("\nDepósito realizado com sucesso!")
            return True
        else:
            print("\nOperação falhou! O valor informado é inválido.")
            return False
        return True


class Historico:
    def __init__(self):
        self._transacoes = []
    
    @property
    def transacoes(self):
        return self._transacoes
    
    def adicionar_transacao(self, transacao):
        self._transacoes.append(
            {
                "tipo": transacao.__class__.__name__,
                "valor": transacao.valor,
                "data": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            }
        )


class Transacao(ABC):

    @property
    @abstractproperty
    def valor(self):
        pass

    @abstractclassmethod
    def registrar(cls, conta):
        pass


class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor
    
    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        status_transacao = conta.sacar(self.valor)
        if status_transacao:
            conta.historico.adicionar_transacao(self)


class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor
    
    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        status_transacao = conta.depositar(self.valor)
        if status_transacao:
            conta.historico.adicionar_transacao(self)


def menu(contas = []):
    if len(contas):
        menu = """\n
        ================ MENU ================
        [l] Listar contas
        [d] Deposito
        [s] Saque
        [e] Extrato
        [c] Cadastrar conta
        [u] Cadastrar usuário
        [q] Sair
        => """
    else:
        menu = """\n
    ================ MENU ================
    [c] Cadastrar conta
    [u] Cadastrar cliente
    [q] Sair
    => """
    return input(menu)

def filtrar_cliente(cpf, clientes):
    clientes_filtrados = [cliente for cliente in clientes if cliente.cpf == cpf]
    return clientes_filtrados[0] if clientes_filtrados else None

def recuperar_conta_cliente(cliente):
    if not cliente.contas:
        print("O cliente não possui contas!")
        return
    return cliente.contas[0]

def depositar(clientes):
    cpf = input("Digite o CPF do cliente:")
    cliente = filtrar_cliente(cpf, clientes)
    if not cliente:
        print("Cliente não encontrado!")
        return
    valor = float(input("Informe o valor do depósito:"))
    transacao = Deposito(valor)
    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return
    cliente.realizar_transacao(conta, transacao)

def sacar(clientes):
    cpf = input("Digite o CPF do cliente:")
    cliente = filtrar_cliente(cpf, clientes)
    if not cliente:
        print("Cliente não encontrado!")
        return
    valor = float(input("Informe o valor do saque:"))
    transacao = Saque(valor)
    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return
    cliente.realizar_transacao(conta, transacao)

def  exibir_extrato(clientes):
    cpf = input("Digite o CPF do cliente:")
    cliente = filtrar_cliente(cpf, clientes)
    if not cliente:
        print("Cliente não encontrado!")
        return
    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return
    print("\n=============== EXTRATO ===============")
    transacoes = conta.historico.transacoes

    txt_extrato = ""
    if not transacoes:
        txt_extrato = "Não foram realizadas movimentações."
    else:
        for transacao in transacoes:
            txt_extrato += f"""\nData:\t{transacao['data']}\n{transacao['tipo']}:\tR$ {transacao['valor']:.2f}\n"""
    print(txt_extrato)
    print(f"\nSaldo:\tR$ {conta.saldo:.2f}")
    print("\n=======================================")

def criar_cliente(clientes):
    cpf = input("Informe o CPF do cliente:")
    cliente = filtrar_cliente(cpf, clientes)
    if cliente:
        print("Já existe cliente com esse CPF!")
        return
    nome = input("Informe o nome do cliente:")
    data_nascimento = input("Informe a data de nascimento (dd-mm-aaaa):")
    endereco = input("Informe o endereço:")
    cliente = PessoaFisica(nome=nome, cpf=cpf, data_nascimento=data_nascimento, endereco=endereco)
    clientes.append(cliente)
    print("Cliente criado com sucesso!")

def  criar_conta(numero_conta, clientes, contas):
    cpf = input("Digite o CPF do cliente:")
    cliente = filtrar_cliente(cpf, clientes)
    if not cliente:
        print("Cliente não encontrado, fluxo de ciração de conta encerrado!")
        return
    conta = ContaCorrente.nova_conta(cliente=cliente, numero=numero_conta)
    contas.append(conta)
    cliente.contas.append(conta)
    print("Conta criada com sucesso!")

def  listar_contas(contas):
    for conta in contas:
        print("=======================================")
        print(textwrap.dedent(str(conta)))

def main():
    clientes = []
    contas = []

    while True:
        opcao = menu(contas)
        if opcao in ['u', 'U']:
            criar_cliente(clientes)
        if opcao in ['d', 'D']:
            depositar(clientes)
        elif opcao in ['s', 'S']:
            sacar(clientes)
        elif opcao in ['e', 'E']:
            exibir_extrato(clientes)
        elif opcao in ['c', 'C']:
            numero_conta = len(contas) + 1
            criar_conta(numero_conta, clientes, contas)
        elif opcao in ['l', 'L']:
            listar_contas(contas)   
        elif opcao == "q":
            break

main()