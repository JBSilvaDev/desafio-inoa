# Desafio INOA - Monitoramento de Ativos Financeiros

Este projeto é uma aplicação web Django para monitorar ativos financeiros da B3, permitindo que usuários configurem limites de preço e recebam alertas por e-mail.

## Funcionalidades

*   **Autenticação de Usuários:** Cadastro, Login e Logout.
*   **Gestão de Ativos:**
    *   Adicionar ativos manualmente à sua lista de monitoramento.
    *   Marcar ativos como "Favoritos" ou "Em Carteira".
    *   Configurar limites de preço (superior e inferior) e frequência de verificação para cada ativo.
    *   Excluir ativos da sua lista de monitoramento com confirmação de senha.
*   **Visualização de Ativos:**
    *   Página "Home" (`/ativos_user/`) exibindo todos os ativos monitorados pelo usuário.
    *   Página "Minha Carteira" (`/ativos_user/carteira/`) exibindo apenas ativos marcados como "Em Carteira".
    *   Página "Meus Favoritos" (`/ativos_user/favoritos/`) exibindo apenas ativos marcados como "Favorito".
    *   Página de Detalhes do Ativo (`/ativos_user/detalhes/<id>/`) com informações atuais e um gráfico de histórico de preços.
*   **Monitoramento e Alertas:**
    *   Comando de gerenciamento (`monitor_ativos`) para verificar periodicamente os preços dos ativos.
    *   Envio de alertas por e-mail quando os preços atingem os limites configurados.
    *   Prevenção de spam de e-mail com base na frequência de verificação.

## Configuração do Ambiente

### 1. Clonar o Repositório e Criar Ambiente Virtual

```bash
git clone <URL_DO_SEU_REPOSITORIO>
cd desafio-inoa
python -m venv venv
```

### 2. Ativar o Ambiente Virtual

*   **Windows:**
    ```bash
    .\venv\Scripts\activate
    ```
*   **Linux/macOS:**
    ```bash
    source venv/bin/activate
    ```

### 3. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar Variáveis de Ambiente (`.env`)

Crie um arquivo chamado `.env` na raiz do projeto (na mesma pasta do `manage.py`) com base no arquivo `.env.example`. Este arquivo conterá suas credenciais sensíveis.

```
# Exemplo de arquivo .env
# Renomeie este arquivo para .env e preencha com suas credenciais.

# Configurações de E-mail (Gmail SMTP)
# Para EMAIL_HOST_PASSWORD, use uma "senha de aplicativo" gerada no Google.
# Veja como gerar: https://support.google.com/accounts/answer/185833
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu_email@gmail.com
EMAIL_HOST_PASSWORD=sua_senha_de_aplicativo
DEFAULT_FROM_EMAIL=seu_email@gmail.com

# Chave da API brapi.dev
# Obtenha sua chave gratuita em https://brapi.dev/
BRAPI_API_KEY=SUA_CHAVE_DA_API_BRAPI
```

**Como obter os valores:**

*   **`EMAIL_HOST_USER` e `DEFAULT_FROM_EMAIL`:** Seu endereço de e-mail do Gmail.
*   **`EMAIL_HOST_PASSWORD` (Senha de Aplicativo do Gmail):**
    1.  Vá para sua Conta Google.
    2.  Clique em "Segurança".
    3.  Em "Como fazer login no Google", clique em "Senhas de app". (Se não vir essa opção, ative a verificação em duas etapas).
    4.  Siga as instruções para gerar uma nova senha de aplicativo. Use essa senha aqui.
*   **`BRAPI_API_KEY`:**
    1.  Acesse [https://brapi.dev/](https://brapi.dev/).
    2.  Crie uma conta gratuita e obtenha sua chave de API.

### 5. Migrações do Banco de Dados

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Criar Superusuário (Opcional, para acesso ao Admin)

```bash
python manage.py createsuperuser
```

### 7. Executar o Servidor de Desenvolvimento

```bash
python manage.py runserver
```

Acesse `http://127.0.0.1:8000/` no seu navegador.

## Monitoramento de Ativos (Tarefa em Segundo Plano)

Para que o sistema monitore os ativos e envie alertas automaticamente, você precisa agendar a execução do comando `monitor_ativos` periodicamente no seu sistema operacional.

### Execução Manual (para Testes)

```bash
python manage.py monitor_ativos
```

### Agendamento (Windows Task Scheduler)

1.  Abra o "Agendador de Tarefas" (Task Scheduler).
2.  Clique em "Criar Tarefa Básica..." (Create Basic Task...).
3.  Dê um nome e descrição para a tarefa (ex: "Monitoramento de Ativos INOA").
4.  Escolha a frequência (ex: "Diariamente", "Semanalmente", ou "Uma vez" para testes, ou configure um gatilho mais avançado para "A cada X minutos").
5.  Na ação, selecione "Iniciar um programa" (Start a program).
6.  Em "Programa/script", coloque o caminho completo para o executável do Python dentro do seu ambiente virtual:
    ```
    C:\caminho\para\seu\projeto\venv\Scripts\python.exe
    ```
7.  Em "Adicionar argumentos (opcional)", coloque:
    ```
    manage.py monitor_ativos
    ```
8.  Em "Iniciar em (opcional)", coloque o caminho completo para a raiz do seu projeto:
    ```
    C:\caminho\para\seu\projeto\desafio-inoa
    ```
9.  Finalize a criação da tarefa.

### Agendamento (Linux/macOS - Cron)

1.  Abra o terminal.
2.  Edite o crontab:
    ```bash
    crontab -e
    ```
3.  Adicione a seguinte linha para executar o comando a cada minuto (ajuste a frequência conforme necessário):
    ```bash
    * * * * * /caminho/para/seu/projeto/venv/bin/python /caminho/para/seu/projeto/manage.py monitor_ativos >> /caminho/para/seu/projeto/monitor_log.log 2>&1
    ```
    *   Substitua `/caminho/para/seu/projeto/` pelo caminho real do seu projeto.
    *   `>> /caminho/para/seu/projeto/monitor_log.log 2>&1` redireciona a saída do comando para um arquivo de log, o que é útil para depuração.

## Telas da Aplicação

### Login
![Login](image/README/1767895749239.png)

### Cadastro
![Cadastro](image/README/1767895770368.png)

### Home - Meus Ativos
![ativos](image/README/1767895791624.png)

### Detalhes do Ativo
![detalhes](image/README/1767895811335.png)

### Output do Monitoramento no Terminal
![terminal monitor](image/README/1767895841404.png)

### E-mail de Alerta Recebido
![e-mail recebido](image/README/1767895856131.png)
