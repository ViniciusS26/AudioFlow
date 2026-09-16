# Sistema Cliente/Servidor em Camadas para Processamento de Áudio

## Descrição do projeto

Este projeto implementa um sistema em três camadas para envio, processamento e armazenamento de arquivos de áudio. O cliente é uma interface gráfica em PySide6, o servidor é um backend em FastAPI com processamento via FFmpeg e o banco de dados é PostgreSQL com SQLAlchemy.

A solução permite:

- selecionar um arquivo de áudio no cliente;
- enviar o arquivo para o servidor via HTTP;
- processar o áudio com operações como normalização, conversão para mono, alteração de velocidade, ajuste de bitrate e conversão de formato;
- armazenar o áudio original e processado em diretórios organizados por data e UUID;
- registrar metadados no PostgreSQL;
- gerar uma imagem da forma de onda automaticamente;
- consultar o histórico de arquivos enviados;
- reproduzir os arquivos no cliente e na interface web do servidor.

## Arquitetura utilizada

- Cliente: PySide6, Python
- Servidor: FastAPI, FFmpeg
- Banco: PostgreSQL
- ORM: SQLAlchemy
- Storage: diretórios organizados por data e UUID

Fluxo:

1. O cliente escolhe um arquivo de áudio.
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

## Prints e demonstração

Para a entrega final, adicione os prints na pasta `docs/screenshots/` e atualize os caminhos abaixo:

- cliente principal
- seleção de arquivo
- envio e processamento
- histórico consultado
- organização dos arquivos no servidor
- página web do servidor

## Observações

- O ambiente precisa ter o FFmpeg instalado e acessível no PATH.
- O PostgreSQL deve estar em execução antes do servidor iniciar.
- A aplicação salva dados reais de áudio e metadados em disco e no banco de dados.

## Autor

Projeto desenvolvido como atividade prática de arquitetura cliente/servidor em camadas para processamento de áudio.
