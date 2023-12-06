# Consulta de ativos listados na B3
- Execultar comando para atualizar tabela com ativos: `python manage.py update-tables`
- Execultar comando para criar super usuario `python manage.py createsuperuser`


# URL's
- '/': Página inicial
  - Cabeçario com opção de login, logoff, cadastro e favoritos
    - login e cadastro desabilitado caso usuário ja esteja logado
    - logoff e favoritos disponível apenas quando logado
  - Lista todos ativos da B3 disponivel no db
  - Opção de busca ativo pelo nome da empresa ou codigo
  - Tabela que informa valor da ação de venda e compra
  - Descrição da empresa cujo ativo foi selecionado
- '/favoritos/': Pagina clone da inicial porem com opção de exibir na lista apenas ativos favoritos, talvez um com *toggle select*
- '/auth/cadastro/': Página para realizar cadastro do usuário
  - Cabeçario com opção de login
  - Formulario de cadastro
- '/auth/login/': Página para realizar login do usuário
  - Cabeçario com opção de cadastro
  - Formulário de login
