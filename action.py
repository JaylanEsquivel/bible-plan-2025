import json
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os

# Carregar variáveis do arquivo .env
load_dotenv()

# Configurações
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Base da URL
base_url = "https://www.bible.com/pt/reading-plans/5-chronological/day/"

# Função para extrair o conteúdo de um dia específico
def extrair_dia(dia):
    url = f"{base_url}{dia}"
    response = requests.get(url)
    mensagem = "Leitura da Bíblia plano"
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Captura o título da página
        titulo = soup.find("title").text.strip()
        mensagem += f" {titulo} \n \n"
        # Encontrar escrituras
        escrituras = soup.find_all(
            "a",
            class_="hover:no-underline items-center text-gray-50 border-gray-10 border-solid inline-flex justify-between plb-2 no-underline w-full border-b-small"
        )
        escrituras += soup.find_all(
            "a",
            class_="hover:no-underline items-center text-gray-50 border-gray-10 border-solid inline-flex justify-between plb-2 no-underline w-full border-b-0"
        )
        
        # Extrair os textos e links
        for escritura in escrituras:
            texto = escritura.find("p").text.strip()
            link = escritura["href"]
            mensagem += f"{texto} - [Link](https://www.bible.com{link}) \n"

        
        return mensagem
    else:
        return {"dia": dia, "erro": "Não foi possível acessar a página"}

# Função para registrar o dia atual
def registro_dia():
    try:
        # Verificar e carregar JSON
        with open("dados.json", "r") as f:
            try:
                dados = json.load(f)
            except json.JSONDecodeError:
                # Arquivo vazio ou corrompido, inicializar padrão
                dados = {"dia_atual": 0}
    except FileNotFoundError:
        # Arquivo não existe, inicializar padrão
        dados = {"dia_atual": 0}
    
    # Incrementar dia
    dados["dia_atual"] += 1
    dia = dados["dia_atual"]
    
    # Salvar JSON atualizado
    with open("dados.json", "w") as f:
        json.dump(dados, f, indent=4)
    
    return dia

# Processamento principal
dia = registro_dia()
# Extrair dados do dia
dados = extrair_dia(dia)

# Exibir resultados
print(dados)

# Enviar mensagem
url_telegram = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
requests.post(url_telegram, data={"chat_id": CHAT_ID, "text": dados, "parse_mode": "Markdown"})
