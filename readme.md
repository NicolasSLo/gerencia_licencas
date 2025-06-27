
# Gerência de Licenças

Este projeto é uma aplicação Python para gerenciamento e controle de licenças de software, buscando dados do site arpasistemas.com.br, com persistência em banco de dados PostgreSQL e registro de logs.

## 📁 Estrutura do Projeto

```
gerencia_licencas/
├── main.py           # Script principal
├── connect.py        # Conexão com banco de dados PostgreSQL
├── .env              # Variáveis de ambiente
├── logs/
│   ├── logs.txt      # Log da aplicação
│   └── baretail.exe  # Visualizador de logs (Windows)
```

## Pré-requisitos

- Python 3.8+
- PostgreSQL
- `pip` (gerenciador de pacotes Python)
- Base de dados "gerencia_licencas" de acordo com a documentação .pdf

## ⚙️ Instalação e Execução

1. **Clone ou extraia o projeto:**
   ```bash
   git clone https://github.com/seu_usuario/gerencia_licencas.git
   cd gerencia_licencas
   ```

2. **Crie e ative um ambiente virtual (opcional, mas recomendado):**
   ```bash
   python -m venv venv
   # Linux/macOS:
   source venv/bin/activate
   # Windows:
   venv\Scripts\activate
   ```

3. **Instale as dependências:**
   ```bash
   pip install requests python-dotenv psycopg2-binary argparse
   ```

4. **Configure o arquivo `.env`:**

   Altere o arquivo chamado `.env` na raiz do projeto com os dados do seu banco e login do site.

   ```env
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=estoque_licencas (database recomendada)
   DB_USER=seu_usuario
   DB_PASSWORD=sua_senha
   ```

5. **Execute a aplicação:**
   ```bash
   python main.py
   ```

   Os logs da execução são salvos em `logs/logs.txt`. Se estiver no Windows, você pode usar `logs/baretail.exe` para monitoramento em tempo real.
