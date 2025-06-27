import requests
from dotenv import load_dotenv
import os
import argparse
import traceback
from datetime import datetime
from psycopg2 import Error
from connect import connect, disconnect

load_dotenv()

# rode esse comando para criar o executor
# pyinstaller --onefile --noconsole main.py

def main():
    # Configura os argumentos que o programa pode receber
    parser = argparse.ArgumentParser(description="Automação de verificação de licenças no portal Arpa.")
    parser.add_argument('--estoque', action='store_true')
    parser.add_argument('--empresas', action='store_true')
    parser.add_argument('--licencas', action='store_true')
    parser.add_argument('--clear', action='store_true')
    args = parser.parse_args()

    connection = connect(args)  # Conecta ao banco de dados
    cursor = connection.cursor()  # Conexão da variavel para executar comandos sql
    cursor.execute("select current_database()")
    row = cursor.fetchone()
    # print(f"Database: {row[0]}")
    save_log(f'Database: {row[0]}')

    # Headers para as configurações das páginas
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
        'Authorization': '',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json',
        'Referer': '',  # valor muda para cada chamada
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        # 'Cookie': '__Host-next-auth.csrf-token=61466c17518e3bbe0399e6a397fd013499943824b47087ca06d084a772e50de2%7C7554cc7ac7b964c9689f0ed5d40dc63ac5761d4bd42b4dc0d90be5cfc6b31d58; PortalArpa-next-auth.callback-url=https%3A%2F%2Fportal.arpasistemas.com.br%2Fportal%2Flogin; PortalArpa-next-auth.session-token=eyJhbGciOiJkaXIiLCJlbmMiOiJBMjU2R0NNIn0..2FBpz8RRqagzSZi4.1p3kqcaNbE7j7uUsNbyvnVCFz5sZafr1I6-OqhFv6IHa_6C5yANQ3ivmv3mYp_LKaANuxepmKJ_rklJ4yC5PV_YPhtFf-dU8f-MsSXLBpoM3RHJzvl8E9JSuoJ4cCHLakugEequGp0aT4amF5HTkf7Get90DFPaHzhpphbwuloz29cqFGOaQJEoIGtFhDSt7ncqt2tYFbGcvQz0psr3WIAGid68w5FkmDMboamXCp75ZhvNVcIFIx3JbLkVQb_O5bzEWsdqdWhQ8gdhQA_1PWp65GoV9v-iGvY9UcOQKq5_lWZmOCpVq3Uqr3daVXIw-nJp97YvyXTsw0y-7IgQ33P4oz9uFbInmnp6QT89LQayqllcoSOAqzruAyCnw2TaIFB6bptuBqu1JvYaBvb4HNxD3-xQr_4-WuYuDHR-XegQho-OTyXWhwaYAzcYk75jzNPPMGZYoYXImkeoUNFNjjaaR4mNceRgfFWIpGsYSsq4VhIIkKyJkQbSKS5vSEbr9ycDNYXPn6qdZpiv4yvf_VyP-awLg7Uq1ZVtfXNoBs84ki81vVeXAafNxnjICrBbeJ296ctROLLIpRrzGNCQgz2NuhO_Vrk1YxErci8c4A3vK0hjFdc1svSzS-4HbXAcCrDKmiYT5mz41jlW4VeTHK4mnDezGNgwREr8nsqqMTrAqsG1LO2UkyRFoSdZDjCqw0YYbpbDyTEsz8SnbSE8eW_8BAVTZErfoCTU-fbHQ4Vb14rMjJf81_N-k7cBcdll2CAFgtB9loeZb22xilMiavGewW7Zf6OXRj7LZ697WiTlop16dyTu4msd7__z-Quuq_jKPfEHBktLVUM7Yk0GJWYQMf2fCQmMkfvnSIPQzQ09d3vk.3DumkGLtLQAiV-f9fp6wcA',
    }

    with requests.Session() as session:
        # Com base no argumento, chama a rotina correspondente.
        if args.estoque:
            # print("\n###### Executando rotina de verificação de estoque ######")
            save_log('###### Executando rotina de verificação de estoque ######')
            estoque_licencas(session, headers, cursor, connection)  # Rotina de estoque

        elif args.empresas:
            # print("\n###### Executando rotina de verificação de empresas ######")
            save_log('###### Executando rotina de verificação de empresas ######')
            empresas(session, headers, cursor, connection)  # Rotina de empresas

        elif args.licencas:
            # print("\n###### Executando rotina de verificação de licenças por empresa ######")
            save_log('###### Executando rotina de verificação de licenças por empresa  ######')
            licencas(session, headers, cursor, connection)  # Rotina de licensas

        else:
            # print("Nenhuma rotina foi selecionada")
            help_text = """
            Argumentos disponíveis:
            --estoque    Verifica a quantidade de licenças em estoque.
            --empresas   Verifica as empresas cadastradas.
            --licencas   Verifica as licenças de todas as empresas.
            --clear      Limpa os logs.
            """
            save_log('Nenhuma rotina foi selecionada')
            save_log(help_text)

    disconnect(connection)  # Desconecta do banco de dados
    save_log('Fim da execução')


def estoque_licencas(session, headers, cursor, connection):
    url = 'https://portal.arpasistemas.com.br/portal/api/router/representante/controleLicenca/buscarLicencaEstoque'
    headers['Referer'] = 'https://portal.arpasistemas.com.br/portal/representante/estoque'
    headers['Authorization'] = get_token(session, connection)  # Coloca a chave de acesso no header

    # Parâmetros da página
    params = {
        'plano': '',
        'produto': '',
        'pagina': '0',
        'tamanhoPagina': '200',  # Mude para aumentar o número de itens na chamada
    }

    save_log('Obtendo dados do estoque no site...')
    try:
        api_response = session.get(url, headers=headers, params=params)  # faz a chamada na api
        api_response.raise_for_status()  # caso tenha um erro, ele capta a mensagem de erro
        dados_estoque = api_response.json()  # pega os dados do estoque no site
        save_log('Dados obtidos com sucesso!')
        # print(dados_estoque)
    except requests.exceptions.RequestException as e:
        erro_completo = traceback.format_exc()
        # print(f'Erro na chamada dos dados: {e}')
        save_log(f'Erro na chamada dos dados: {e}')
        save_log(f'{erro_completo}')

        return

    # quantidade das licencas
    qtd_licencas = {
        "Premium": 0,
        "Standart": 0,
        "Pro": 0,
        "Retaguarda": 0,
        "PDV": 0,
        "PDV_Offline": 0,
        "GOC": 0,
        "Smart_vendas": 0,
        "Pre_venda_movel": 0,
        "Check_stock": 0,
        "Controle_lote": 0,
        "Pratto_control": 0,
        "Movel_pratto": 0,
        "OS": 0,
        "Gestao_prom": 0,
        "Emissor_boleto": 0,
        "Dashboard": 0,
        "Nfe_serv": 0,
        "Arpag": 0,
        "PIX": 0,
        "Vimbo": 0
    }

    # lê a quantidade das licencas
    for licenca in dados_estoque:
        match licenca['produto']:
            case 'Premium -  937(sistema)':
                qtd_licencas["Premium"] += 1
            case 'Standart - 938 (sistema)':
                qtd_licencas["Standart"] += 1
            case 'Pró - 939 (Sistema)':
                qtd_licencas["Pro"] += 1
            case 'Retaguarda - 940 (adicional)':
                qtd_licencas["Retaguarda"] += 1
            case 'PDV -  941 (adicional)':
                qtd_licencas["PDV"] += 1
            case 'PDV Off-Line - 942':
                qtd_licencas["PDV_Offline"] += 1
            case 'GOC ( Gerenciador de Operações com Cartões) - 943':
                qtd_licencas["GOC"] += 1
            case 'Smart Força de Vendas - 944 (APP)':
                qtd_licencas["Smart_vendas"] += 1
            case 'Pré Venda Móvel- 945 (APP)':
                qtd_licencas["Pre_venda_movel"] += 1
            case 'CHECK STOCK (Coletor de Dados Móvel)  -  946':
                qtd_licencas["Check_stock"] += 1
            case 'Controle de Lote - 947 ':
                qtd_licencas["Controle_lote"] += 1
            case 'Pratto Control - 948':
                qtd_licencas["Pratto_control"] += 1
            case 'Móvel Pratto-950 (APP)':
                qtd_licencas["Movel_pratto"] += 1
            case 'O.S. (Ordem de Serviço) - 963':
                qtd_licencas["OS"] += 1
            case 'Gestão de promoções -  964':
                qtd_licencas["Gestao_prom"] += 1
            case 'Emissor de Boleto Automático - 966':
                qtd_licencas["Emissor_boleto"] += 1
            case 'Dashboard':
                qtd_licencas["Dashboard"] += 1
            case 'Nota Fiscal de Serviço- 973':
                qtd_licencas["Nfe_serv"] += 1
            case 'Arpag - 975':
                qtd_licencas["Arpag"] += 1
            case 'PIX Integrado':
                qtd_licencas["PIX"] += 1
            case 'Vimbo Padrão':
                qtd_licencas["Vimbo"] += 1

    # Exibir a quantidade de licencas
    # print(qtd_licencas)

    save_log("Obtendo estoque das licencas no banco de dados...")
    try:
        # pega os cnpj's já existentes no banco para fazer uma validação
        cursor.execute("select licenca, quantidade from estoque_licencas")
        db_licencas = {row[0]: row[1] for row in cursor.fetchall()}
        save_log('Dados obtidos com sucesso!')
    except Error as e:
        # print(f'Erro na chamada dos dados: {e}')
        save_log(f'Erro na chamada dos dados: {e}')
        return

    # print(db_licencas['Retaguarda']) # quantidade de uma licenca especifica no banco

    alterados = 0

    # um loop para contar o número de cada tipo de licença para adicionar no banco de dados
    save_log('Atualizando dados do estoque no banco de dados...')
    try:
        for licenca_nome, quantidade in qtd_licencas.items():
            if db_licencas[
                licenca_nome] != quantidade:  # Caso a quantidade no site seja diferente da quantidade no banco de dados, atualiza o banco de dados
                try:
                    cursor.execute(
                        "UPDATE estoque_licencas SET quantidade = %s WHERE licenca = %s;",
                        (quantidade, licenca_nome))
                    alterados += 1
                except Error as e:
                    # print(f'Erro na inclusão dos dados: {e}')
                    erro_completo = traceback.format_exc()
                    save_log(f'Erro na inclusão dos dados: {e}')
                    save_log(f'{erro_completo}')
                    return

        connection.commit()  # commit dos dados
        if alterados > 0:
            # print(f'Quantidade de licencas alteradas: {alterados}')
            save_log('Dados do estoque atualizados no banco de dados com sucesso!')
            save_log(f'Quantidade de licencas alteradas: {alterados}')
        else:
            # print('Nenhuma licenca alterada')
            save_log('Nenhuma licenca alterada')
        save_log('###### Fim da rotina de verificação de estoque ######')

    except:
        erro_completo = traceback.format_exc()
        # print(f'Erro na chamada dos dados')
        save_log('Erro na atualização dos dados')
        save_log(f'{erro_completo}')
        return


def empresas(session, headers, cursor, connection):
    url = 'https://portal.arpasistemas.com.br/portal/api/router/representante/clienteWeb/buscarClienteComLicenca'
    headers['Referer'] = 'https://portal.arpasistemas.com.br/portal/representante/cliente-licenciamento'
    headers['Authorization'] = get_token(session, connection)  # Coloca a chave de acesso no header

    # Parâmetros da página
    params = {
        'nome': '',
        'cnpj': '',
        'pagina': '0',
        'tamanhoPagina': '1000',  # Mude para aumentar o número de itens na chamada
    }

    save_log('Obtendo dados das empresas no site...')
    try:
        api_response = session.get(url, headers=headers, params=params)  # faz a chamada na api
        api_response.raise_for_status()  # caso tenha um erro, ele capta a mensagem de erro
        dados_empresas = api_response.json()['content']  # pega as empresas cadastradas
        save_log('Dados obtidos com sucesso!')
        # print(dados_empresas)
    except requests.exceptions.RequestException as e:
        erro_completo = traceback.format_exc()
        # print(f'Erro na chamada dos dados: {e}')
        save_log(f'Erro na chamada dos dados: {e}')
        save_log(f'{erro_completo}')
        return

    save_log("Obtendo cnpj's do banco de dados...")
    try:
        # pega os cnpj's já existentes no banco para fazer uma validação
        cursor.execute('select cnpj from empresas;')
        db_cnpj = [row[0] for row in cursor.fetchall()]
        save_log('Dados obtidos com sucesso!')
    except Error as e:
        # print(f'Erro na chamada dos dados: {e}')
        save_log(f'Erro na chamada dos dados: {e}')
        return

    # número de empresas que foram tratadas
    cadastros = 0
    cadastros_removidos = 0

    # Atualiza os dados das empresas no banco de dados comparando com cada cnpj já existente no banco
    save_log("Atualizando dados das empresas no banco de dados...")
    try:
        # Adiciona empresas que não estão no banco de dados mas estão no site
        for empresa in dados_empresas:
            cnpj = empresa['cnpj']
            if cnpj not in db_cnpj:
                try:
                    cursor.execute(
                        "INSERT INTO empresas (cnpj, razao_social, nome_fantasia) VALUES (%s, %s, %s)",
                        (empresa['cnpj'], capitalizar_nome(empresa['razao']), capitalizar_nome(empresa['fantasia']))
                    )
                    save_log(f"CNPJ/CPF: {empresa['cnpj']} - RAZAO: {empresa['razao']}")
                    cadastros += 1
                except Error as e:
                    erro_completo = traceback.format_exc()
                    # print(f'Erro na inclusão dos dados: {e}')
                    save_log(f"Erro na inclusão dos dados: {e}")
                    save_log(f"{erro_completo}")
                    return

        # Remove empresas que estão no banco de dados mas não estão mais no site
        for db_cnpj in db_cnpj:
            try:
                if db_cnpj not in [empresa['cnpj'] for empresa in dados_empresas]:
                    cursor.execute(
                        "select cnpj from licencas",
                        (db_cnpj,)
                    )
                    cnpj_licencas = [row[0] for row in cursor.fetchall()]

                    # deleta as licencas atribuidas à empresa
                    if db_cnpj in cnpj_licencas:
                        cursor.execute(
                            "delete from licencas where cnpj = %s",
                            (db_cnpj,)
                        )

                    cursor.execute(
                        "DELETE FROM empresas WHERE cnpj = %s",
                        (db_cnpj,)
                    )
                    # print(f"CNPJ {db_cnpj} removido com sucesso!")
                    save_log(f"CNPJ/CPF: {db_cnpj} - REMOVIDO")
                    cadastros_removidos += 1
            except Error as e:
                erro_completo = traceback.format_exc()
                # print(f'Erro na exclusão dos dados: {e}')
                save_log(f"Erro na exclusão dos dados: {e}")
                save_log(f"{erro_completo}")
                return

        connection.commit()  # commit dos dados

        # Validação para o número de empresas cadastradas
        if cadastros == 0:
            # print('Nenhuma empresa foi cadastrada.')
            save_log("Nenhuma empresa foi cadastrada.")
        else:
            # print(f"Número de empresas cadastradas: {cadastros}")
            save_log(f"Número de empresas cadastradas: {cadastros}")

        # Validação para o número de empresas removidas
        if cadastros_removidos == 0:
            # print('Nenhuma empresa foi removida.')
            save_log("Nenhuma empresa foi removida.")
        else:
            # print(f"Número de empresas removidas: {cadastros_removidos}")
            save_log(f"Número de empresas removidas: {cadastros_removidos}")
        save_log("###### Fim da rotina de verificação de empresas ######")

    except:
        erro_completo = traceback.format_exc()
        # print(f'Erro na chamada dos dados')
        save_log("Erro na atualização dos dados")
        save_log(f"{erro_completo}")
        return


def licencas(session, headers, cursor, connection):
    url = 'https://portal.arpasistemas.com.br/portal/api/router/representante/controleLicenca/buscarLicenca'

    headers['Authorization'] = get_token(session, connection)
    headers['Content-Type'] = 'application/json'

    payload = {
        'cnpj': '',
        'dataFinal': '',
        'dataInicial': '',
        'plano': '',
        'produto': '',
        'statusLicenca': [
            'ATIVA',
            'VENCIDA',
            'BLOQUEADA',
            'RENOVADA',
            'INATIVADA',
        ],
        'tipoData': 'NENHUM',
    }

    # Parâmetros da página
    params = {
        'pagina': '0',
        'tamanhoPagina': '1000',  # Mude para aumentar o número de itens na chamada
    }

    save_log("Obtendo cnpj's do banco de dados...")
    try:
        # pega os cnpj's já existentes no banco para fazer uma validação
        cursor.execute('select cnpj from empresas;')
        db_cnpj = [row[0] for row in cursor.fetchall()]
        save_log('Dados obtidos com sucesso!')
    except Error as e:
        erro_completo = traceback.format_exc()
        # print(f'Erro na chamada dos dados: {e}')
        save_log(f"Erro na chamada dos dados: {e}")
        save_log(f"{erro_completo}")
        return

    save_log("Obtendo ID's das licencas no banco de dados...")
    try:
        # pega os cnpj's já existentes no banco para fazer uma validação
        cursor.execute('select licenca_id from licencas;')
        db_licenca_id = [row[0] for row in cursor.fetchall()]
        save_log("Dados obtidos com sucesso!")
    except Error as e:
        # print(f'Erro na chamada dos dados: {e}')
        save_log(f"Erro na chamada dos dados: {e}")
        return

    save_log("Obtendo dados das licencas das empresas...")
    try:
        for cnpj in db_cnpj:
            payload['cnpj'] = cnpj  # adiciona o cnpj no payload para fazer a chamada da api

            try:
                api_response = session.post(url, json=payload, headers=headers, params=params)  # faz a chamada na api
                api_response.raise_for_status()  # caso tenha um erro, ele capta a mensagem de erro
                licencas = api_response.json()['content']
            except requests.exceptions.RequestException as e:
                erro_completo = traceback.format_exc()
                # print(f'Erro na chamada dos dados: {e}')
                save_log(f"Erro na chamada dos dados na api: {e}")
                save_log(f"{erro_completo}")
                return

            # print(licencas)
            save_log("Atualizando dados das licencas...")
            try:
                for i in range(len(licencas)):
                    if str(licencas[i]['codigoLicenca']) not in db_licenca_id:  # caso a licenca já estiver no banco
                        cursor.execute(
                            "insert into licencas (licenca_id, cnpj, licenca_codigo, produto, status, plano, data_validade, data_ativacao, data_vinculo) values (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                            (str(licencas[i]['codigoLicenca']), cnpj, licencas[i]['planoCodigo'],
                             licencas[i]['produto'],
                             licencas[i]['statusLicenca'],
                             licencas[i]['plano'], licencas[i]['dataValidade'], licencas[i]['dataAtivacao'],
                             licencas[i]['dataVinculo'])
                        )
            except Error as e:
                erro_completo = traceback.format_exc()
                # print(f'Erro na chamada dos dados: {e}')
                save_log(f"Erro na inclusão dos dados no banco de dados: {e}")
                save_log(f"{erro_completo}")
                return

    except:
        erro_completo = traceback.format_exc()
        # print(f'Erro ao obter dados das licencas no banco de dados')
        save_log("Erro na atualização dos dados")
        save_log(f"{erro_completo}")

        return

    connection.commit()  # commit dos dados
    # print('Dados das licencas das empresas adicionadas!')
    save_log("Dados licencas das empresas atualizadas no banco de dados com sucesso!")
    save_log("###### Fim da rotina de verificação de licencas ######")


def get_token(session, connection):
    # Dados de login
    payload = {
        'email': os.getenv('SITE_EMAIL'),
        'password': os.getenv('SITE_PASSWORD'),
        'callbackUrl': 'https://portal.arpasistemas.com.br/portal/login',
        'csrfToken': ''
    }

    try:
        # Coloca a chave csrf no payload para o login
        csrf_response = session.get('https://portal.arpasistemas.com.br/portal/api/auth/csrf')
        csrf_response.raise_for_status()
        csrf_token = csrf_response.json()['csrfToken']
        payload['csrfToken'] = csrf_token
    except requests.exceptions.RequestException as e:
        erro_completo = traceback.format_exc()
        # print(f'Erro na chamada do csrf token: {e}')
        save_log(f"Erro na chamada do csrf token: {e}")
        save_log(f"{erro_completo}")

        disconnect(connection)
        quit()

    save_log("Realizando login...")
    try:
        # faz o login
        login_response = session.post('https://portal.arpasistemas.com.br/portal/api/auth/callback/credentials',
                                      data=payload, allow_redirects=False)
        login_response.raise_for_status()  # caso tenha um erro, ele capta a mensagem de erro
        save_log("Login realizado com sucesso!")
    except requests.exceptions.RequestException as e:
        erro_completo = traceback.format_exc()
        # print(f'Erro na chamada do token: {e}')
        save_log(f"Erro na chamada do token: {e}")
        save_log(f"{erro_completo}")

        disconnect(connection)
        quit()

    save_log("Resgatando o Token...")
    try:
        # pega o token de acesso
        credentials_response = session.get('https://portal.arpasistemas.com.br/portal/api/auth/session')
        credentials_response.raise_for_status()  # caso tenha um erro, ele capta a mensagem de erro
        token = credentials_response.json()['user']['access_token']  # Pega exatamente o campo do token
        save_log("Token obtido com sucesso!")
        return f"Bearer {token}"  # Retorna o token formatado para a inclusão no header
    except requests.exceptions.RequestException as e:
        erro_completo = traceback.format_exc()
        # print(f'Erro na chamada do token: {e}')
        save_log(f"Erro na chamada do token: {e}")
        save_log(f"{erro_completo}")
        disconnect(connection)
        quit()
    except:
        erro_completo = traceback.format_exc()
        # print(f'Erro na chamada do token ou credenciais de login incorretas.')
        save_log("Erro na chamada do token ou credenciais de login incorretas")
        save_log(f"{erro_completo}")
        disconnect(connection)
        quit()


def save_log(texto):
    with open('logs/logs.txt', 'a', encoding='utf-8') as arquivo_log:
        data_atual = datetime.now()
        data_formatada = data_atual.strftime('%d-%m-%Y - %H:%M:%S.%f')
        arquivo_log.write(f"[ {data_formatada} ] ----- {texto}\n")


def capitalizar_nome(texto):
    """
    Capitaliza a primeira letra de cada palavra do texto, mantendo algumas preposições em minúsculo
    """
    if not texto:
        return texto

    excecoes = ['de', 'da', 'do', 'das', 'dos', 'e', 'em', 'para']
    palavras = texto.lower().split()
    resultado = []

    for i, palavra in enumerate(palavras):
        if i == 0 or palavra not in excecoes:
            resultado.append(palavra.capitalize())
        else:
            resultado.append(palavra.lower())

    return ' '.join(resultado)


if __name__ == '__main__':
    main()
