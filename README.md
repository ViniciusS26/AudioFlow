# Sistema Cliente/Servidor em Camadas para Processamento de Áudio

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688?logo=fastapi&logoColor=white)
![PySide6](https://img.shields.io/badge/PySide6-GUI-41CD52?logo=qt&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-4169E1?logo=postgresql&logoColor=white)
![FFmpeg](https://img.shields.io/badge/FFmpeg-Processing-0078D4?logo=ffmpeg&logoColor=white)

## Descrição do projeto

Este projeto implementa um sistema em três camadas para envio, processamento e armazenamento de arquivos de áudio. O cliente é uma interface gráfica em PySide6, o servidor é um backend em FastAPI com processamento via FFmpeg e o banco de dados é PostgreSQL com SQLAlchemy.

A solução permite:

- selecionar e validar um arquivo de áudio no cliente;
- enviar o arquivo para o servidor via HTTP;
- processar o áudio com operações como normalização, conversão para mono, alteração de velocidade, ajuste de bitrate e conversão de formato;
- armazenar o áudio original e processado em diretórios organizados por data e UUID;
- registrar metadados no PostgreSQL;
- gerar automaticamente uma imagem da forma de onda;
- consultar o histórico de arquivos enviados;
- reproduzir os arquivos no cliente e na interface web do servidor.

## Arquitetura do sistema

O sistema foi estruturado em camadas para separar responsabilidades e facilitar manutenção e extensão.

```text
┌──────────────────────────────┐
│          Cliente             │
│      PySide6 / Python        │
│  - seleção de arquivo        │
│  - token de autenticação     │
│  - upload e reprodução       │
└──────────────┬───────────────┘
               │ HTTP/REST
               ▼
┌──────────────────────────────┐
│          Servidor            │
│       FastAPI + FFmpeg       │
│  - autenticação por token    │
│  - processamento de áudio    │
│  - organização de arquivos   │
│  - geração de waveform       │
└──────────────┬───────────────┘
               │ ORM / SQL
               ▼
┌──────────────────────────────┐
│          Banco de dados      │
│       PostgreSQL + SQLAlchemy│
│  - metadados dos áudios      │
│  - histórico e registros     │
└──────────────────────────────┘
```

Fluxo principal:

1. O cliente seleciona um arquivo de áudio.
2. O cliente envia o arquivo e o tipo de processamento.
3. O servidor gera um UUID e organiza os arquivos em pastas por data.
4. O servidor processa o áudio com FFmpeg.
5. O servidor grava metadados em PostgreSQL.
6. O servidor salva a representação gráfica da onda.
7. O cliente consulta o histórico por API e reproduz os arquivos.

## Estrutura do repositório

```text
.
├── client/
│   └── app.py
├── database/
│   └── init.sql
├── docs/
│   └── screenshots/
├── server/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── audio_service.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   └── storage.py
│   └── run_server.py
├── docker-compose.yml
├── requirements.txt
├── .gitignore
├── .env
├── README.md
└── tools/
```

## Requisitos

- Python 3.10+
- FFmpeg instalado e acessível no PATH
- Docker e Docker Compose (opcional, para PostgreSQL)
- Ambiente virtual recomendado

## Como executar

### 1) Clone o repositório

```bash
git clone https://github.com/seu-usuario/seu-repositorio.git
cd seu-repositorio
```

### 2) Crie e ative o ambiente virtual

```bash
python -m venv .venv
```

Windows:

```bash
.\.venv\Scripts\activate
```

Linux/macOS:

```bash
source .venv/bin/activate
```

### 3) Instale as dependências

```bash
pip install -r requirements.txt
```

### 4) Configure o ambiente

O projeto usa um arquivo `.env` com as configurações de banco, token e caminhos do sistema. Ajuste os valores conforme o ambiente local.

Para executar o cliente e o servidor em máquinas diferentes, configure o `.env` da máquina do servidor com `SERVER_HOST=0.0.0.0`, mantenha o banco e o FFmpeg nessa máquina e libere a porta TCP `8000` no firewall. Descubra o IPv4 da máquina do servidor (por exemplo, `192.168.1.50`) e crie `client/.env` na máquina do cliente com:

```env
API_BASE_URL=http://192.168.1.50:8000
API_TOKEN=audio-demo-token
```

O valor de `API_TOKEN` precisa ser igual ao configurado no `.env` do servidor. O cliente só precisa das dependências Python e não precisa ter PostgreSQL, FFmpeg ou a pasta `server/storage`.

### 5) Inicie o banco de dados

```bash
docker compose up -d postgres
```

### 6) Execute o servidor

```bash
cd server
python run_server.py
```

A API ficará disponível em:

- http://localhost:8000
- http://localhost:8000/docs
- http://localhost:8000/api/audios

Em outra máquina da mesma rede, substitua `localhost` pelo IP do servidor, por exemplo `http://192.168.1.50:8000`.

### 7) Execute o cliente

Em outro terminal, a partir da pasta raiz:

```bash
python client/app.py
```

## Processamentos disponíveis

Os processamentos implementados são:

- `normalize` – normalização de volume
- `mono` – conversão para mono
- `speed` – alteração da velocidade de reprodução
- `bitrate` – redução de bitrate
- `format` – conversão de formato
- `noise_reduce` – redução de ruído
- `compress` – compactação dinâmica do áudio
- `fade` – entrada e saída com fade
- `trim` – corte do áudio

Exemplo de uso via API:

```bash
curl -X POST "http://localhost:8000/api/upload" \
  -F "file=@/caminho/arquivo.wav" \
  -F "processing_type=normalize"
```

## Organização dos arquivos no servidor

Os arquivos ficam armazenados em estrutura de diretórios:

```text
server/storage/
└── 2026/
    └── 09/
        └── 16/
            └── <uuid>/
                ├── audio.wav
                ├── audio_processed.wav
                ├── waveform.png
                └── meta.json
```

Os metadados do arquivo incluem:

- checksum SHA256;
- tamanho do arquivo;
- duração;
- taxa de amostragem;
- canais;
- bitrate;
- tipo de processamento;
- caminhos dos arquivos original e processado.

## Interface web do servidor

A rota raiz da API exibe uma página simples com a lista de áudios armazenados, permitindo acesso direto aos arquivos para reprodução no navegador.



## Observações

- O ambiente precisa ter o FFmpeg instalado e acessível no PATH.
- O PostgreSQL deve estar em execução antes do servidor iniciar.
- A aplicação salva dados reais de áudio e metadados em disco e no banco de dados.
- O token de autenticação deve estar consistente entre o cliente e o servidor.



## Estrutura do repositório

```text
.
├── client/
│   └── app.py
├── database/
│   └── init.sql
├── server/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── audio_service.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   └── storage.py
│   └── run_server.py
├── docker-compose.yml
├── requirements.txt
├── .gitignore
└── README.md
```

## Requisitos

- Python 3.10+
- FFmpeg instalado e disponível no PATH
- Docker e Docker Compose (opcional, para PostgreSQL)

## Instalação

1. Clone o repositório.
2. Crie um ambiente virtual:

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.\.venv\Scripts\activate  # Windows
```

3. Instale as dependências:

```bash
pip install -r requirements.txt
```

4. Verifique a instalação do FFmpeg:

```bash
ffmpeg -version
```

## Configuração do banco de dados

A opção mais simples é usar o PostgreSQL em contêiner via Docker Compose:

```bash
docker compose up -d postgres
```

O arquivo `docker-compose.yml` cria banco `audio_db`, usuário `audio_user` e senha `audio_pass`.

A URL padrão do banco usada pela aplicação é:

```text
postgresql+psycopg2://audio_user:audio_pass@localhost:5432/audio_db
```

Se necessário, ajuste a variável `DATABASE_URL` antes de iniciar o servidor.

## Execução do servidor

A partir da pasta raiz do projeto:

```bash
cd server
python run_server.py
```

A API ficará disponível em:

- http://localhost:8000
- http://localhost:8000/docs
- http://localhost:8000/api/audios

## Execução do cliente

Em outro terminal, a partir da pasta raiz:

```bash
python client/app.py
```

A interface permite:

- selecionar arquivo de áudio;
- escolher tipo de processamento;
- enviar para o servidor;
- visualizar histórico;
- reproduzir o áudio original e processado.

## Processamentos disponíveis

Os processamentos implementados são:

- `normalize` – normalização de volume
- `mono` – conversão para mono
- `speed` – alteração da velocidade de reprodução
- `bitrate` – redução de bitrate
- `format` – conversão de formato

Exemplos de uso via API:

```bash
curl -X POST "http://localhost:8000/api/upload" \
  -F "file=@/caminho/arquivo.wav" \
  -F "processing_type=normalize"
```

## Organização dos arquivos no servidor

Os arquivos ficam armazenados em estrutura de diretórios:

```text
server/storage/
└── 2026/
    └── 09/
        └── 16/
            └── <uuid>/
                ├── audio.wav
                ├── audio_processed.wav
                ├── waveform.png
                └── meta.json
```

Os metadados do arquivo incluem:

- checksum SHA256;
- tamanho do arquivo;
- duração;
- taxa de amostragem;
- canais;
- bitrate;
- tipo de processamento;
- caminhos dos arquivos original e processado.

## Interface web do servidor

A rota raiz da API exibe uma página simples com a lista de áudios armazenados, permitindo acesso direto aos arquivos para reprodução no navegador.

## Resultados obtidos

A seguir estão os principais resultados visuais do sistema em operação:

### Interface principal do cliente

![Interface principal do cliente](docs/screenshots/Captura%20de%20tela%202026-09-16%20125330.png)

### Seleção do arquivo de áudio

![Seleção do arquivo de áudio](docs/screenshots/Captura%20de%20tela%202026-09-16%20125343.png)

### Navegador de arquivos do sistema

![Escolha do arquivo](docs/screenshots/Captura%20de%20tela%202026-09-16%20125357.png)

### Upload e processamento no servidor

![Upload e processamento](docs/screenshots/Captura%20de%20tela%202026-09-16%20125431.png)

### Histórico e reprodução do áudio processado

![Histórico e reprodução](docs/screenshots/Captura%20de%20tela%202026-09-16%20125454.png)

Essas imagens demonstram o fluxo completo do projeto: seleção, upload, processamento, armazenamento no servidor e reprodução das versões original e processada.
## Observações

- O ambiente precisa ter o FFmpeg instalado e acessível no PATH.
- O PostgreSQL deve estar em execução antes do servidor iniciar.
- A aplicação salva dados reais de áudio e metadados em disco e no banco de dados.
