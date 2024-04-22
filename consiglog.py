from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.select import Select
from random import choice
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import zipfile
from fake_useragent import UserAgent
import time
from twocaptcha import TwoCaptcha
import traceback
from selenium.webdriver.common.action_chains import ActionChains
import os
import random
import pandas as pd
from selenium.webdriver import ActionChains
from config import *

def proxies(username, password, endpoint, port):
    manifest_json = """
    {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Proxies",
        "permissions": [
            "proxy",
            "tabs",
            "unlimitedStorage",
            "storage",
            "<all_urls>",
            "webRequest",
            "webRequestBlocking"
        ],
        "background": {
            "scripts": ["background.js"]
        },
        "minimum_chrome_version":"22.0.0"
    }
    """

    background_js = """
    var config = {
            mode: "fixed_servers",
            rules: {
              singleProxy: {
                scheme: "http",
                host: "%s",
                port: parseInt(%s)
              },
              bypassList: ["localhost"]
            }
          };

    chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

    function callbackFn(details) {
        return {
            authCredentials: {
                username: "%s",
                password: "%s"
            }
        };
    }

    chrome.webRequest.onAuthRequired.addListener(
                callbackFn,
                {urls: ["<all_urls>"]},
                ['blocking']
    );
    """ % (endpoint, port, username, password)

    extension = 'proxy_extension.zip'

    with zipfile.ZipFile(extension, 'w') as zp:
        zp.writestr("manifest.json", manifest_json)
        zp.writestr("background.js", background_js)

    return extension

proxy_list = [ 
              {"host":"181.41.197.51",'port':'59100','username':proxy_login,'password':proxy_password,'failed':0},
              {"host":"141.11.141.243",'port':'59100','username':proxy_login,'password':proxy_password,'failed':0},
              {"host":"185.74.55.82",'port':'59100','username':proxy_login,'password':proxy_password,'failed':0},
              {"host":"2.56.249.158",'port':'59100','username':proxy_login,'password':proxy_password,'failed':0},
              {"host":"191.96.73.137",'port':'59100','username':proxy_login,'password':proxy_password,'failed':0},
              ]
def create_new_chrome_browser(use_proxy=True, headless=True):
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument("--headless=new")
    ua = UserAgent(os="windows", min_percentage=0.5)
    user_agent = ua.getChrome
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-dev-shm-usage")
    # options.add_argument("--disable-gpu")
    prefs = {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
    }
    options.add_experimental_option("prefs", prefs)
    options.add_argument("--no-sandbox")
    options.add_argument("--start-maximized")
    options.add_argument(f"--user-agent={user_agent}")
    if use_proxy:

        if len(proxy_list) > 0:
            proxy_selected = choice(proxy_list)
            options.add_extension(proxy_selected['name_proxy'])

    else:
        proxy_selected = []
        pass
    
    driver = webdriver.Chrome(
        service=ChromeService(ChromeDriverManager().install()), options=options
    )
    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )
    while True:
        try:
            driver.get("http://checkip.amazonaws.com//")

            ip = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, "/html/body"))
            )

            print(ip.text)
            return driver
        except:
            tb = traceback.format_exc()
            print(tb)
            print("proxy falhou")
            if len(proxy_list) > 0:
                proxy_selected["failed"] += 1
                if proxy_selected["failed"] > 3:

                    proxy_list.remove(proxy_selected)
                create_new_chrome_browser(use_proxy=False)
            raise LookupError
def primeira_etapa(url, usuario, senha, url_margem):
    
    def abrir_navegador(url):
        print('Iniciando primeira etapa...')
        try:
            driver = create_new_chrome_browser(use_proxy=False,headless=False)
            driver.get(url)
            return driver
        except Exception as e:
            print(e)
            retorno = {
                "sucesso": False,
                "msg_retorno": 'A página pode estar temporariamente indisponível'
            }
            print(retorno)
            return retorno

    def preencher_login(driver, usuario):
        try:
            WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.ID, 'txtLogin'))
            )
            driver.find_element(By.ID, 'txtLogin').send_keys(usuario)
        except TimeoutException:
            print('erro ao preencher o usuario')

    def click_enter(driver):
        try:
            driver.find_element(By.ID, 'Entrar').click()
        except NoSuchElementException:
            print('erro ao clicar em entrar no login')
    
    def verificar_login_valido(driver):
        try:
            WebDriverWait(driver, 3).until(
                EC.visibility_of_element_located((By.ID, 'ucAjaxModalPopup1_lblMensagemPopup'))
            )
            msg_erro = driver.find_element(By.ID, 'ucAjaxModalPopup1_lblMensagemPopup').text
            if "Login inválido." in msg_erro:
                retorno = {
                    "sucesso": False,
                    "msg_retorno": 'Login inválido'
                }
                print(retorno)
                driver.quit()
                return retorno
        except TimeoutException:
            pass

    def preencher_senha(driver, senha):
        try:
            WebDriverWait(driver, 50).until(
                EC.visibility_of_element_located((By.ID, 'txtSenha'))
            )
            driver.find_element(By.ID, 'txtSenha').send_keys(senha)
        except TimeoutException:
            retorno = {
                "sucesso": False,
                "msg_retorno": 'Erro ao preencher a senha'
            }
            print(retorno)
            return retorno
        
    def verificar_senha_valida(driver):
        try:
            WebDriverWait(driver, 3).until(
                EC.visibility_of_element_located((By.ID, 'ucAjaxModalPopup1_lblMensagemPopup'))
            )
            msg_erro = driver.find_element(By.ID, 'ucAjaxModalPopup1_lblMensagemPopup').text
            msg_senha_invalida = 'Usuario ou senha Inválida, Você tentou entrar incorretamente no sistema 1 vezes, resta(m) 4 tentativa(s)'
            if msg_senha_invalida in msg_erro:
                retorno = {
                    "sucesso": False,
                    "msg_retorno": msg_senha_invalida
                }
                print(retorno)
                driver.quit()
                return retorno
        except:
            print('Login e Senha preenchidos com sucesso!')
            
    def verificar_usuario_logado(driver):
        try:
            WebDriverWait(driver, 5).until (
                EC.visibility_of_element_located((By.ID, 'ucAjaxModalPopupConfirmacao1_lblMensagemPopup'))
            )
            driver.find_element(By.ID, 'ucAjaxModalPopupConfirmacao1_btnConfirmarPopup').click()
        except TimeoutException:
            pass

    def clickar_convenio(driver):
        try:
            WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.XPATH, '//*[@id="gvOrgao"]/tbody'))
            )
            tbody_element = driver.find_element(By.XPATH, '//*[@id="gvOrgao"]/tbody')
            rows = tbody_element.find_elements(By.TAG_NAME, 'tr')
            
            for row in rows:
                columns = row.find_elements(By.TAG_NAME, 'td')
                for column in columns:
                    if column.text.strip() == 'GOVERNO AMAZONAS':
                        inputs = row.find_elements(By.TAG_NAME, 'input')
                        for input_elem in inputs:
                            id_element = input_elem.get_attribute('id')
                            driver.find_element(By.ID, id_element).click()
                            print('Convenio GOVERNO AMAZONAS selecionado com sucesso!')
                            return
        except NoSuchElementException:
            pass

    def entrar_consultar_margem(driver, url_margem):
        try:
            driver.get(url_margem)
        except Exception as e:
            print('Não foi possível acessar a página de consulta de margem', e)

    driver = abrir_navegador(url)
    preencher_login(driver, usuario)
    click_enter(driver)
    verificar_login_valido(driver)
    preencher_senha(driver, senha)
    click_enter(driver)
    verificar_senha_valida(driver)
    verificar_usuario_logado(driver)
    clickar_convenio(driver)
    entrar_consultar_margem(driver, url_margem)

    return driver

def segunda_etapa(driver, matricula='', cpf=''):
    print('Iniciando segunda etapa...')
    if not matricula and not cpf:
        return {'msg_retorno':'sem cpf e matricula'}
    def preencher_servico(driver):
        time.sleep(1)
        try:
            select_servico = driver.find_element(By.ID, 'body_servicoDropDownList')
            select = Select(select_servico)
            indice = 1
            select.select_by_index(indice)
        except NoSuchElementException:
            pass
    
    def preencher_matricula(driver, matricula):
        try:
            WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.ID, 'body_matriculaTextBox'))
            )
            driver.find_element(By.ID, 'body_matriculaTextBox').send_keys(matricula)
        except TimeoutException:
            retorno = {
                "sucesso": False,
                "msg_retorno": 'Erro ao preencher a matrícula'
            }
            print(retorno)
            return retorno
    
    def preencher_cpf(driver, cpf):
        try:
            WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.ID, 'body_cpfTextBox'))
            )
            driver.find_element(By.ID, 'body_cpfTextBox').send_keys(cpf)
        except TimeoutException:
            retorno = {
                "sucesso": False,
                "msg_retorno": 'Erro ao preencher o cpf'
            }
            print(retorno)
            return retorno
    
    def matricula_ou_cpf(driver):
        if matricula == '':
            preencher_cpf(driver, cpf)
        else:
            preencher_matricula(driver, matricula)
    
    def pesquisar_margem(driver):
        try:
            WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.ID, 'body_pesquisarButton'))
            )
            driver.find_element(By.ID, 'body_pesquisarButton').click()
        except:
            pass
        
    def verificar_erro(driver):
        try:
            WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.ID, 'body_ucAjaxModalPopup1_lblMensagemPopup'))
            )
            msg_erro = driver.find_element(By.ID, 'body_ucAjaxModalPopup1_lblMensagemPopup').text
            if msg_erro == 'CPF/Matrícula não encontrado.':
                print('CPF/Matrícula não encontrado.')
                fechar_alerta = driver.find_element(By.ID, 'body_ucAjaxModalPopup1_btnConfirmarPopup')
                fechar_alerta.click()
                retorno = {
                    "sucesso": False,
                    "msg_retorno": 'CPF/Matrícula não encontrado'
                }
                print(retorno)
                driver.quit()
                return retorno
        except:
            pass
            
    def verificar_quantidade_contratos(driver):
        try:
            WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.ID, 'body_servidorGridView'))
            )
            time.sleep(1)
            tr_elements = driver.find_elements(By.CSS_SELECTOR, 'tbody > tr')
            cpf_count = 0
            for tr in tr_elements:
                td_elements = tr.find_elements(By.TAG_NAME, 'td')
                for td in td_elements:
                    if td.text.strip() == 'Ativo':
                        cpf_count += 1
            time.sleep(0.5)
            driver.find_element(By.ID, 'body_cancelarButton').click()
            return cpf_count
        except:
            pass          
         
    def loop_entre_contratos(driver):
        try:
            quantidade_contratos = verificar_quantidade_contratos(driver)
            for num_id in range(quantidade_contratos):
                time.sleep(0.5)
                preencher_servico(driver)
                time.sleep(0.5)
                matricula_ou_cpf(driver)
                time.sleep(0.5)
                pesquisar_margem(driver)
                id_contrato = f'body_servidorGridView_selectImageButton_{num_id}'
                clicar_contrato = WebDriverWait(driver, 3).until(
                    EC.visibility_of_element_located((By.ID, id_contrato))
                )
                clicar_contrato.click()
                detalhes_margem(driver)
        except:
            pass
        
    def dados_extras(driver):
        try:
            nome_cliente_element = WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.ID, 'body_clienteTextBox'))
            )
            matricula_element = driver.find_element(By.ID, 'body_matriculaTextBox')
            cpf_nascimento_element = driver.find_element(By.ID, 'body_cpf_nascimentoTextBox')
            categoria_element = driver.find_element(By.ID, 'body_categoriaTextBox')
            data_admissao_element = driver.find_element(By.ID, 'body_txtDataAdmissao')
            lotacao_element = driver.find_element(By.ID, 'body_txtLotacao')
            situacao_element = driver.find_element(By.ID, 'body_txtSituacao')

            nome_cliente = nome_cliente_element.get_attribute('value')
            matricula = matricula_element.get_attribute('value')
            cpf_nascimento = cpf_nascimento_element.get_attribute('value')
            categoria = categoria_element.get_attribute('value')
            data_admissao = data_admissao_element.get_attribute('value')
            lotacao = lotacao_element.get_attribute('value')
            situacao = situacao_element.get_attribute('value')

            dados_extras = {
                "nome_cliente": nome_cliente,
                "matricula": matricula,
                "cpf_nascimento": cpf_nascimento,
                "categoria": categoria,
                "data_admissao": data_admissao,
                "lotacao": lotacao,
                "situacao": situacao
            }
            return dados_extras
        except:
            pass

    def detalhes_margem(driver):
        operacoes = []
        try:
            WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.ID, 'body_btnHistoricoMargem'))
            )
            for i in range(4):
                tr_id = f"body_rptMargens_headerservico_{i}"
                tr = driver.find_element(By.ID, tr_id)
                celulas = tr.find_elements(By.TAG_NAME, 'td')
                if len(celulas) >= 4:
                    servico = celulas[0].text.strip()
                    margem_total = float(celulas[1].text.strip().replace('R$', '').replace('.', '').replace(',', '.'))
                    margem_reservada = float(celulas[2].text.strip().replace('R$', '').replace('.', '').replace(',', '.'))
                    margem_disponivel_str = celulas[3].text.strip().replace('R$', '').replace('.', '').replace(',', '.').replace('\n', '')

                    if '-' in margem_disponivel_str:
                        margem_disponivel = -float(margem_disponivel_str.replace('-', ''))
                    else:
                        margem_disponivel = float(margem_disponivel_str)

                    dados_extra = dados_extras(driver)
                    operacao = {
                        "servico": servico,
                        "margem_total": margem_total,
                        "margem_reservada": margem_reservada,
                        "margem_disponivel": margem_disponivel,
                        "nome_cliente": dados_extra['nome_cliente'],
                        "matricula": dados_extra['matricula'],
                        "cpf_nascimento": dados_extra['cpf_nascimento'],
                        "categoria": dados_extra['categoria'],
                        "data_admissao": dados_extra['data_admissao'],
                        "lotacao": dados_extra['lotacao'],
                        "situacao": dados_extra['situacao']
                    }
                    operacoes.append(operacao)
                else:
                    print("Número insuficiente de células na linha.")
                    for celula in celulas:
                        print("Conteúdo da célula:", celula.text)
            print('Operações encontradas:', operacoes)
            time.sleep(1)
            clicar_voltar = driver.find_element(By.ID, 'body_voltarButton')
            clicar_voltar.click()
        except:
            pass

        msg_retorno = f"{len(operacoes)} Operação Encontrada" if len(operacoes) == 1 else f"{len(operacoes)} Operações Encontradas"

        return {
            "sucesso": True,
            "valor_liberado": 0,
            "msg_retorno": msg_retorno,
            "cpf": cpf,
            "operacoes": operacoes,
        }

    preencher_servico(driver)
    matricula_ou_cpf(driver)
    pesquisar_margem(driver)
    verificar_erro(driver)
    detalhes_margem(driver)
    loop_entre_contratos(driver)

url = 'https://govam.consiglog.com.br/Login.aspx'
url_margem = 'https://govam.consiglog.com.br/Margem/ConsultaMargem.aspx'
usuario = usuario
senha = senha
cpf = ''
matricula = ''

cpfs = [
    '7578935461', '34750312215', '44261950200', '93969147204', '51187140287', 
    '22980156272', '19401418268', '2226688226', '89746236253', '51366827287', 
    '88327396234', '33733155220', '13016032287', '95827870234', '72227125268', 
    '74533711200', '77298586220', '60996820230', '72847026215', '69879877268', 
    '85298123287', '6842089204', '58428933200', '91434289249', '85977896204', 
    '44567413253', '23999705272', '60407883215', '27362531249', '96222557287', 
    '45628734268', '1017280266', '73328383204', '64749789291', '34315136204', 
    '4680022272', '41789342287', '31517021200', '51641550287', '1244664278', 
    '95901256204', '79576923204', '955932254', '28413954215', '13505351253', 
    '6520707287', '24257354291', '7627858291', '71760580244', '23821809272'
]
try:
    driver = primeira_etapa(url, usuario, senha, url_margem)
    if driver:
        print('PRIMEIRA ETAPA CONCLUÍDA')
        for cpf in cpfs:
            retorno = segunda_etapa(driver, matricula, cpf)
            print(retorno)
    else:
        print('A primeira etapa falhou. Não foi possível prosseguir para a segunda etapa.')
except Exception as e:
    print(traceback.format_exc())
    print('Ocorreu um erro durante a execução da primeira etapa:', e)
    
