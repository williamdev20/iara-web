# IARA - Inteligência Assistiva de Reconhecimento Auditivo e gestual

> Esta é a versão web da IARA

## Introdução

A **IARA (Inteligência Assistiva de Reconhecimento Auditivo e Gestual)** é uma plataforma web que utiliza a webcam do usuário, acessada diretamente pelo navegador, para capturar sinais em Libras e enviá-los a um backend em Python. Nesse servidor, um modelo de visão computacional identifica os gestos e os converte em **fala em tempo real**.

O projeto busca reduzir barreiras comunicativas entre pessoas surdas e ouvintes, oferecendo uma solução **online, acessível e de baixo custo**, promovendo **autonomia e inclusão** tanto na interação cotidiana quanto no mercado de trabalho.

---

## Requisitos
- Node 19+
- npm 9
- Python 3.11
- Django 5
- Git
- Make (Linux/macOS; no Windows, use `make` via WSL ou rodar comandos manualmente)

---

## Como rodar localmente

Clone o repositório:
```
git clone https://github.com/williamdev20/iara-web.git
cd iara-web
```

Criar um ambiente virtual
```
python3 -m venv venv # Ou apenas python (ou ainda py) no Windows
source venv/bin/activate # Ou .\venv\Scripts\activate no Windows
```

Instale as dependências:
```
pip install -r requirements.txt
npm install
```

Gerar chave secreta Django
```
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

```

Configurar variáveis de ambiente
```
cp .env.example .env

#.env
SECRET_KEY=coloque_aqui_sua_chave_secreta_gerada
```


Execute as migrações:
```
python3 manage.py migrate # Ou apenas python (ou ainda py) no Windows
```

Execute com:
```
make run
```
Acesse em http://localhost:8000

---

## Rotas principais

- `/process-frame/` -> transforma o frame para base64 e retorna o sinal e a confiança do gesto capturado pela câmera.

    Exemplo de retorno:
    ```
    {
        confianca: 0.90,
        sinal: "AMOR"
    }
    ```

- `/tts/<str:sinal>` -> transforma o gesto capturado pela câmera em voz (Content-Type: audio/mpeg)

