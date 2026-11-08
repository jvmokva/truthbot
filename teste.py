


def valid_input(user_argument):
    user_argument = user_argument.strip()
    if len(user_argument) < 8:
        return False
    if len(user_argument) > 2000:
        return False
    if not any(char.isalpha() for char in user_argument):
        return False
    if not user_argument.isprintable():
        return False
    return True


def fact_check(user_argument):
    if valid_input(user_argument):
        print("Aguarde, fazendo a checagem de fatos...")
    else:
        print("Você não forneceu argumentos suficientes para uma checagem, por favor tente novamente.")
        
if __name__ == "__main__":
    user_argument = input(str(" "))
    fact_check(user_argument)     
