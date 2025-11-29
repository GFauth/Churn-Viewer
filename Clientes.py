import csv
import os
import math


# =----- ÁRVORE B -----=

class NoB:
    def __init__(self, folha=False):
        self.folha = folha
        self.chaves = []  # Lista de chaves (IDs)
        self.valores = [] # lista de clientes correspondentes às chaves
        self.filhos = []  # lista de referências para nós filhos

class ArvoreB:
    def __init__(self, grau_minimo):
        self.raiz = NoB(folha=True)
        self.t = grau_minimo  # grau mínimo 

    def buscar(self, chave, no=None):
        if no is None:
            no = self.raiz
        
        i = 0
        while i < len(no.chaves) and chave > no.chaves[i]:
            i += 1
        
        
        if i < len(no.chaves) and chave == no.chaves[i]: #se encontrou a chave neste nó, retorna o valor
            return no.valores[i]
        
        
        if no.folha:
            return None
        
        
        return self.buscar(chave, no.filhos[i])

    def inserir(self, chave, valor):
        raiz = self.raiz
        # Se a raiz estiver cheia, a árvore cresce em altura
        if len(raiz.chaves) == (2 * self.t) - 1:
            nova_raiz = NoB(folha=False)
            nova_raiz.filhos.append(self.raiz)
            self._dividir_filho(nova_raiz, 0)
            self.raiz = nova_raiz
            self._inserir_nao_cheio(self.raiz, chave, valor)
        else:
            self._inserir_nao_cheio(raiz, chave, valor)

    def _inserir_nao_cheio(self, no, chave, valor):
        i = len(no.chaves) - 1
        
        if no.folha:
            # Encontra a posição correta e insere
            no.chaves.append(None) # Expande lista
            no.valores.append(None) 
            while i >= 0 and chave < no.chaves[i]:
                no.chaves[i + 1] = no.chaves[i]
                no.valores[i + 1] = no.valores[i]
                i -= 1
            no.chaves[i + 1] = chave
            no.valores[i + 1] = valor
        else:
            # Encontra o filho para descer
            while i >= 0 and chave < no.chaves[i]:
                i -= 1
            i += 1
            
            # Se o filho estiver cheio, divide antes de descer
            if len(no.filhos[i].chaves) == (2 * self.t) - 1:
                self._dividir_filho(no, i)
                if chave > no.chaves[i]:
                    i += 1
            self._inserir_nao_cheio(no.filhos[i], chave, valor)

    def _dividir_filho(self, pai, indice):
        t = self.t
        filho = pai.filhos[indice]
        novo_no = NoB(folha=filho.folha)
        
        # Move a metade superior das chaves/valores para o novo nó
        pai.chaves.insert(indice, filho.chaves[t-1])
        pai.valores.insert(indice, filho.valores[t-1])
        pai.filhos.insert(indice + 1, novo_no)
        
        novo_no.chaves = filho.chaves[t:]
        novo_no.valores = filho.valores[t:]
        
        filho.chaves = filho.chaves[:t-1]
        filho.valores = filho.valores[:t-1]
        
        if not filho.folha:
            novo_no.filhos = filho.filhos[t:]
            filho.filhos = filho.filhos[:t]

    def coletar_todos(self, no=None, lista_resultados=None):
        """Método auxiliar para percorrer a árvore e coletar todos os objetos (para filtros/médias)"""
        if lista_resultados is None:
            lista_resultados = []
        if no is None:
            no = self.raiz
            
        i = 0
        for i in range(len(no.chaves)):
            if not no.folha:
                self.coletar_todos(no.filhos[i], lista_resultados)
            lista_resultados.append(no.valores[i])
        
        if not no.folha:
            self.coletar_todos(no.filhos[i+1], lista_resultados)
            
        return lista_resultados


# =---- Classe do Cliente ----=

class Cliente: 
    #esses foram os dados que eu ahei mais importantes de começo
    def __init__(self, id_cliente, genero, cancelou, cobranca_mensal, contrato):
        self.id_cliente = id_cliente
        self.genero = genero #booleano a principio
        self.cancelou = cancelou #booleano
        self.cobranca_mensal = float(cobranca_mensal)
        self.contrato = contrato
        self.meses = int(meses)

    def __repr__(self):
        return f"[{self.id_cliente}] {self.genero} | {self.contrato} | R${self.cobranca_mensal:.2f} | Cancelou: {self.cancelou}"


# =---- Classe do gerenciador ----=

class SistemaDeAnalise:
    def __init__(self):
        #inicializa a árvore com grau mínimo 3 
        self.arvore_clientes = ArvoreB(grau_minimo=3)

    #função que pega os dados do arquivo .csv
    def carregar_dados(self, nome_arquivo):
        print(f"Iniciando leitura de {nome_arquivo} e inserção na Árvore B...")
        try:
            with open(nome_arquivo, mode='r', encoding='utf-8') as arquivo:
                leitor = csv.DictReader(arquivo) #arquivos em python são muito bizarros
                contador = 0

                
                #para adicionar mais dados tem que editar [aqui]
                for linha in leitor:
                    try:
                        valor_mensal = float(linha['MonthlyCharges'])
                    except ValueError:
                        valor_mensal = -1.0

                    try:
                        meses = int(linha['tenure'])
                    except ValueError:
                        valor_mensal = -1

                    novo_cliente = Cliente( 
                        id_cliente=linha['customerID'],
                        genero=linha['gender'],
                        cancelou=linha['Churn'],
                        cobranca_mensal=valor_mensal,
                        contrato=linha['Contract']
                    )
                    
                    # =--- INSERÇÃO NA ÁRVORE B ---=
                    self.arvore_clientes.inserir(novo_cliente.id_cliente, novo_cliente) #usa o ID como chave e o objeto cliente como valor
                    
                    contador += 1
                
                print(f"Leitura finalizada. {contador} registros inseridos na Árvore B.")
        
        except FileNotFoundError:
            print("Arquivo CSV não encontrado.")
        except Exception as erro:
            print(f"Erro inesperado: {erro}")

    def buscar_id(self, id_busca):
        # --- Utiliza a busca da Árvore B -----
        return self.arvore_clientes.buscar(id_busca)

    def filtro(self, status_cancelamento, tipo_contrato):
        # Para filtrar ela percorre todos os itmes
        todos_clientes = self.arvore_clientes.coletar_todos()
        resultados = []
        
        for cliente in todos_clientes:
            if cliente.cancelou == status_cancelamento and cliente.contrato == tipo_contrato:
                resultados.append(cliente)
                
        return resultados

    # --- Percorre a árvore para calcular estatísticas ----
    def calcular_media(self, status_cancelamento):
        todos_clientes = self.arvore_clientes.coletar_todos()
        soma = 0.0
        conta = 0
        
        for cliente in todos_clientes:
            if cliente.cancelou == status_cancelamento:
                soma += cliente.cobranca_mensal
                conta += 1
        
        if conta == 0:
            return 0.0
        return soma / conta


# =------- (MENU) -------=

def menu():
    sistema = SistemaDeAnalise()
    nome_arquivo = 'WA_Fn-UseC_-Telco-Customer-Churn.csv' #arquivo padrão do Kaggle, é procurado na mesma pasta em que está o programa do python
    
    if not os.path.exists(nome_arquivo):
        print(f"O arquivo padrão '{nome_arquivo}' não foi encontrado.")
        nome_arquivo = input("Por favor, digite o nome do arquivo CSV: ") #precisa conter o .csv

    sistema.carregar_dados(nome_arquivo)

    while True:
        print("\n" + "="*40)
        print(" SISTEMA DE ANÁLISE DE CLIENTES")
        print("="*40)
        print("1. Buscar Cliente por ID")
        print("2. Filtrar por Contrato e Status")
        print("3. Calcular Média de Gasto Mensal")
        print("4. Sair")
        print("-" *35)
        opcao = input("Escolha uma opção: ")

        if opcao == '1':
            id_digitado = input(f"Digite o ID do Cliente (ex: 0000-AAAAA): ")
            cliente = sistema.buscar_id(id_digitado)
            if cliente:
                print(f"\n Encontrado na Árvore: {cliente}")
            else:
                print("\n Cliente não encontrado.")
                
 #eu queria separar os dois filtros (pesquisar apenas contrato ou cancelou) mas enquanto não adiconamos mais opções de filtros
 #vou deixar juntos porque é menos trabalho
        elif opcao == '2': 
            contrato = input("Tipo de Contrato (ex: Month-to-month, One year, Two year): ")
            status = input("Cancelou? (Yes/No): ")
            res = sistema.filtro(status, contrato)
            if res:
                print(f"\n {len(res)} clientes encontrados.")
                for c in res[:3]: print(c) #exibe os 3 primeiros como exemplo
                if len(res) > 3: print("...")
            else:
                print("\n Nenhum registro encontrado.")

        elif opcao == '3': #teste pra ver se pesquisa e operações na árvore funcionam
            media_churn = sistema.calcular_media("Yes")
            media_ativos = sistema.calcular_media("No")
            print(f"\n---- Médias ----\n")
            print(f"Cancelados: R${media_churn:.2f}")
            print(f"Ativos    : R${media_ativos:.2f}")

        elif opcao == '4':
            break
            exit()

if __name__ == "__main__": 
    menu()
