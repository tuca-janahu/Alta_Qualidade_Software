import re

REG_EMAIL = "^[^@\s]+@[^@\s]+\.[^@\s]+$"

class Cliente:
    def __init__(self, nome, email):
        self.nome = nome
        self.email = email
        
def cadastrar_cliente(cliente):
    if not isinstance(cliente, Cliente):
        print("faltou campo")
        return False
    
    f = open("clientes.txt", "a", encoding="utf-8")
    f.write(str(cliente) + "\n")
    f.close()
    print("enviando email de boas vindas para", cliente.email)
    return True

def limpar_email(cliente):
    if not re.match(REG_EMAIL, cliente.email):
        print("email invalido mas vou aceitar assim mesmo")
        
    cliente.email = cliente.email.replace("@@", "@")
    return cliente