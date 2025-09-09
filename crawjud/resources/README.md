# Resources - Recursos Estáticos e Elementos

Este módulo contém recursos estáticos, elementos de interface, configurações de elementos web e outros assets utilizados pelos bots e pela aplicação CrawJUD.

## Estrutura

### Elements (`elements/`)
Definições de elementos web utilizados pelos bots:
- Seletores CSS e XPath
- Configurações de elementos
- Mapeamentos de elementos por sistema
- Templates de elementos reutilizáveis

## Funcionalidades Principais

### Elementos Web
Definições centralizadas de elementos para automação:

#### Seletores CSS
```python
class PJeSelectors:
    """Seletores CSS para o sistema PJe."""
    
    # Login
    LOGIN_FORM = "form#loginForm"
    USERNAME_INPUT = "input#username"
    PASSWORD_INPUT = "input#password"
    LOGIN_BUTTON = "button[type='submit']"
    
    # Navegação
    MENU_PROCESSES = "a[href*='processos']"
    SEARCH_INPUT = "input#numeroProcesso"
    SEARCH_BUTTON = "button.btn-search"
    
    # Tabelas
    PROCESS_TABLE = "table.processos"
    PROCESS_ROWS = "table.processos tbody tr"
    PROCESS_LINK = "td a.processo-link"
```

#### XPath Expressions
```python
class ESAJXPaths:
    """XPath expressions para o sistema ESAJ."""
    
    # Consulta de processos
    SEARCH_FRAME = "//frame[@name='mainFrame']"
    PROCESS_NUMBER_INPUT = "//input[@name='numeroDigitoAnoUnificado']"
    SEARCH_BUTTON = "//input[@value='Consultar']"
    
    # Resultados
    RESULT_TABLE = "//table[@class='fundocinza1']"
    PROCESS_DETAILS = "//td[contains(@class, 'fundocinza1')]"
    DOWNLOAD_LINKS = "//a[contains(@href, 'download')]"
```

### Configurações de Elementos

#### Timeouts e Esperas
```python
class ElementConfig:
    """Configurações de elementos web."""
    
    DEFAULT_TIMEOUT = 30
    IMPLICIT_WAIT = 10
    PAGE_LOAD_TIMEOUT = 60
    
    # Timeouts específicos por tipo
    TIMEOUTS = {
        'login': 20,
        'search': 15,
        'download': 120,
        'navigation': 10
    }
    
    # Estratégias de espera
    WAIT_STRATEGIES = {
        'element_clickable': EC.element_to_be_clickable,
        'element_visible': EC.visibility_of_element_located,
        'element_present': EC.presence_of_element_located,
        'text_present': EC.text_to_be_present_in_element
    }
```

#### Actions Configurations
```python
class ActionConfig:
    """Configurações de ações de automação."""
    
    # Delays entre ações
    ACTION_DELAYS = {
        'click': 0.5,
        'type': 0.1,
        'navigation': 2.0,
        'form_submit': 1.0
    }
    
    # Retry configurations
    RETRY_CONFIG = {
        'max_attempts': 3,
        'backoff_factor': 2,
        'exceptions': [TimeoutException, NoSuchElementException]
    }
```

### Mapeamentos por Sistema

#### PJe Elements
```python
class PJeElements:
    """Elementos específicos do sistema PJe."""
    
    LOGIN = {
        'certificate_option': "//input[@value='certificado']",
        'password_option': "//input[@value='senha']",
        'certificate_select': "select#certificateSelect",
        'username_field': "input#username",
        'password_field': "input#password",
        'login_button': "button#loginButton"
    }
    
    PROCESS_SEARCH = {
        'search_tab': "//a[contains(text(), 'Consulta')]",
        'number_input': "input#numeroProcesso",
        'search_button': "button.btn-consultar",
        'result_table': "table#tabelaResultados",
        'process_link': "a.linkProcesso"
    }
    
    PROCESS_DETAILS = {
        'capa_tab': "//a[contains(text(), 'Capa')]",
        'parties_section': "div.partesProcesso",
        'movements_tab': "//a[contains(text(), 'Movimentações')]",
        'documents_tab': "//a[contains(text(), 'Documentos')]"
    }
```

#### ESAJ Elements
```python
class ESAJElements:
    """Elementos específicos do sistema ESAJ."""
    
    FRAMES = {
        'main_frame': "frame[name='mainFrame']",
        'content_frame': "frame[name='contentFrame']",
        'search_frame': "frame[name='searchFrame']"
    }
    
    SEARCH = {
        'process_input': "input[name='numeroDigitoAnoUnificado']",
        'verification_input': "input[name='foroNumeroUnificado']",
        'captcha_input': "input[name='vlCaptcha']",
        'captcha_image': "img[src*='captcha']",
        'search_button': "input[value='Consultar']"
    }
    
    RESULTS = {
        'table': "table.fundocinza1",
        'process_row': "tr.fundocinza1",
        'details_link': "a[href*='detalhes']",
        'documents_link': "a[href*='documentos']"
    }
```

### Templates de Elementos

#### Form Templates
```python
class FormTemplates:
    """Templates para formulários comuns."""
    
    @staticmethod
    def login_form(username_selector, password_selector, submit_selector):
        """Template para formulário de login."""
        return {
            'username': {
                'selector': username_selector,
                'type': 'input',
                'wait_strategy': 'element_visible'
            },
            'password': {
                'selector': password_selector,
                'type': 'password',
                'wait_strategy': 'element_visible'
            },
            'submit': {
                'selector': submit_selector,
                'type': 'button',
                'wait_strategy': 'element_clickable'
            }
        }
    
    @staticmethod
    def search_form(search_input, search_button, results_container):
        """Template para formulário de busca."""
        return {
            'search_input': {
                'selector': search_input,
                'type': 'input',
                'wait_strategy': 'element_visible'
            },
            'search_button': {
                'selector': search_button,
                'type': 'button',
                'wait_strategy': 'element_clickable'
            },
            'results': {
                'selector': results_container,
                'type': 'container',
                'wait_strategy': 'element_present'
            }
        }
```

### Utilities para Elementos

#### Element Finder
```python
class ElementFinder:
    """Utilitário para encontrar elementos."""
    
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, ElementConfig.DEFAULT_TIMEOUT)
    
    def find_element(self, selector, strategy='css'):
        """Encontra elemento por seletor."""
        if strategy == 'css':
            return self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
        elif strategy == 'xpath':
            return self.wait.until(
                EC.presence_of_element_located((By.XPATH, selector))
            )
        elif strategy == 'id':
            return self.wait.until(
                EC.presence_of_element_located((By.ID, selector))
            )
    
    def find_clickable_element(self, selector, strategy='css'):
        """Encontra elemento clicável."""
        locator = self._get_locator(selector, strategy)
        return self.wait.until(EC.element_to_be_clickable(locator))
    
    def find_visible_element(self, selector, strategy='css'):
        """Encontra elemento visível."""
        locator = self._get_locator(selector, strategy)
        return self.wait.until(EC.visibility_of_element_located(locator))
```

#### Element Interactor
```python
class ElementInteractor:
    """Utilitário para interagir com elementos."""
    
    def __init__(self, driver):
        self.driver = driver
        self.finder = ElementFinder(driver)
    
    async def click_element(self, selector, strategy='css'):
        """Clica em elemento com retry."""
        for attempt in range(ActionConfig.RETRY_CONFIG['max_attempts']):
            try:
                element = self.finder.find_clickable_element(selector, strategy)
                element.click()
                await asyncio.sleep(ActionConfig.ACTION_DELAYS['click'])
                return True
            except Exception as e:
                if attempt == ActionConfig.RETRY_CONFIG['max_attempts'] - 1:
                    raise
                await asyncio.sleep(ActionConfig.RETRY_CONFIG['backoff_factor'] ** attempt)
        return False
    
    async def type_text(self, selector, text, strategy='css', clear_first=True):
        """Digita texto em elemento."""
        element = self.finder.find_element(selector, strategy)
        
        if clear_first:
            element.clear()
        
        for char in text:
            element.send_keys(char)
            await asyncio.sleep(ActionConfig.ACTION_DELAYS['type'])
    
    async def select_dropdown_option(self, selector, option_text, strategy='css'):
        """Seleciona opção em dropdown."""
        element = self.finder.find_element(selector, strategy)
        select = Select(element)
        select.select_by_visible_text(option_text)
```

## Asset Management

### Static Files
```python
class AssetManager:
    """Gerenciador de assets estáticos."""
    
    ASSET_PATHS = {
        'icons': 'resources/icons/',
        'images': 'resources/images/',
        'templates': 'resources/templates/',
        'css': 'resources/css/',
        'js': 'resources/js/'
    }
    
    @classmethod
    def get_asset_path(cls, asset_type, filename):
        """Obtém caminho completo do asset."""
        base_path = cls.ASSET_PATHS.get(asset_type, 'resources/')
        return Path(__file__).parent / base_path / filename
    
    @classmethod
    def load_template(cls, template_name):
        """Carrega template de arquivo."""
        template_path = cls.get_asset_path('templates', f"{template_name}.html")
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
```

## Configuração de Recursos

### Resource Loading
```python
class ResourceLoader:
    """Carregador de recursos."""
    
    _cache = {}
    
    @classmethod
    def load_elements(cls, system_name):
        """Carrega elementos para um sistema específico."""
        if system_name in cls._cache:
            return cls._cache[system_name]
        
        elements_file = f"elements/{system_name}_elements.json"
        elements_path = AssetManager.get_asset_path('templates', elements_file)
        
        with open(elements_path, 'r', encoding='utf-8') as f:
            elements = json.load(f)
        
        cls._cache[system_name] = elements
        return elements
    
    @classmethod
    def get_element_config(cls, system_name, element_name):
        """Obtém configuração específica de elemento."""
        elements = cls.load_elements(system_name)
        return elements.get(element_name, {})
```

## Uso

### Exemplo de Uso
```python
from crawjud.resources.elements import PJeElements, ElementFinder, ElementInteractor

class PJeBot:
    def __init__(self, driver):
        self.driver = driver
        self.finder = ElementFinder(driver)
        self.interactor = ElementInteractor(driver)
    
    async def login(self, username, password):
        """Realiza login no PJe."""
        # Usar elementos definidos
        await self.interactor.type_text(
            PJeElements.LOGIN['username_field'], 
            username
        )
        await self.interactor.type_text(
            PJeElements.LOGIN['password_field'], 
            password
        )
        await self.interactor.click_element(
            PJeElements.LOGIN['login_button']
        )
```