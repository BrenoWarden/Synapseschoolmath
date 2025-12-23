import os
import sys
from colorama import init, Fore, Style
from core.brain import Brain
from core.memory import Memory
from config import USER_NAME, AI_NAME

# Inicializa cores
init(autoreset=True)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def security_check():
    clear_screen()
    print(Fore.RED + "🔒 SISTEMA DE SEGURANÇA ATIVADO 🔒")
    print("Identifique-se para acessar o núcleo da IA.")
    user = input(Fore.YELLOW + "Usuário: ").strip()
    
    if user.lower() == USER_NAME.lower():
        print(Fore.GREEN + f"Acesso concedido. Bem-vindo, Criador {USER_NAME}.")
        return True
    else:
        print(Fore.RED + "ACESSO NEGADO. INTRUSO DETECTADO.")
        print("Iniciando protocolos de defesa...")
        # Aqui poderia ter algo "engraçado" ou só fechar
        return False

def main():
    if not security_check():
        sys.exit(1)

    print(Fore.CYAN + f"\nIniciando {AI_NAME} v1.0...")
    print(Fore.CYAN + "Carregando módulos neurais... Python 3.xx Detectado.")
    print(Fore.CYAN + "Conectando ao núcleo gpt-oss-120b:free...")
    
    memory = Memory()
    brain = Brain(memory)
    
    print(Fore.GREEN + f"\n{AI_NAME} ESTÁ ONLINE. Às suas ordens, {USER_NAME}.\n")
    
    while True:
        try:
            user_input = input(Fore.WHITE + f"{USER_NAME}: ")
            if user_input.lower() in ['sair', 'exit', 'desligar']:
                print(Fore.RED + f"{AI_NAME}: Desligando sistemas. Até logo, Mestre.")
                break
            
            if not user_input:
                continue

            response = brain.think(user_input)
            
            # Remove a tag de busca da resposta final se ela sobrar (opcional, mas bom para limpeza)
            # A lógica do brain já deve ter lidado com isso, mas se a IA repetir o comando, limpamos.
            # (Simplificação: vamos imprimir direto)
            
            print(Fore.MAGENTA + f"{AI_NAME}: " + Fore.WHITE + response + "\n")
            
            # Salvar memória
            memory.add_interaction(user_input, response)

        except KeyboardInterrupt:
            print(Fore.RED + f"\n{AI_NAME}: Interrupção forçada detectada. Encerrando.")
            sys.exit(0)
        except Exception as e:
            print(Fore.RED + f"ERRO CRÍTICO: {e}")

if __name__ == "__main__":
    main()
