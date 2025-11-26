# PetroBahia S.A.

A **PetroBahia S.A.** é uma empresa fictícia do setor de óleo e gás. Seu sistema interno calcula preços de combustíveis, valida clientes e gera relatórios. 
O código está **mal estruturado** e **difícil de manter**. O objetivo é **refatorar** aplicando **PEP8**, **Clean Code** e **princípios SOLID** (SRP e OCP).

## Objetivos
- Melhorar legibilidade e clareza do código
- Extrair funções e classes coesas
- Eliminar duplicações e efeitos colaterais
- Melhorar nomes e modularidade

## Estrutura
```
src/
├── main.py
└── legacy/
    ├── clientes.py
    ├── pedido_service.py
    └── preco_calculadora.py
```

## Instruções
1. Leia o código legado.
2. Liste os problemas encontrados.
3. Refatore sem mudar o comportamento principal.
4. Documente suas **decisões de design** neste README.

---

#  Decisões de Design

##  Arquitetura e Estrutura

    src/
    ├── domains/                      
    │   ├── cliente.py                
    │   └── pedido.py                 
    ├── services/                     
    │   ├── preco_calculadora.py      
    │   └── servico_cliente.py        
    └── main.py                       


## Melhorias de PEP 8
* **Nomenclatura e estrutura de módulos**

  * Arquivos e pacotes **minúsculos** (`cliente.py`, `servico_cliente.py`), `__init__.py` corretos, layout `src/` claro.
  * Imports **absolutos** (`from src...`) e execução como módulo: `python -m src.main`.
---
* **Docstrings e organização (PEP 257)**

  * Docstrings em módulos/classes/métodos públicos; separação em seções; duas linhas entre defs top-level.
---
* **Typing forte**

  * Anotações completas (`-> None`, `-> Decimal`, `Optional`, `Final`, `Pattern[str]`), tornando o código **auto-documentado** e “mypy-friendly”.
---
* **Constantes e regex compilada**

  * `EMAIL_RE: Final[Pattern[str]] = re.compile(...)` em vez de string solta; custo de compilação único; intenção explícita.
---
* **Formatação e estilo**

  * `black` (line-length 88) + `isort profile=black`; nomes em `snake_case`; zero `print` em services (usa `logging`).
  * `pathlib.Path` para caminhos (mais legível e portátil do que `open` puro com strings).
---
* **Erros e controle de fluxo**

  * Antes: `print` e `False` silenciosos; agora: **exceções** significativas (`ValueError` para dados, `IOError` para I/O), com logs.
  * Domínio usa `__post_init__` para validar/normalizar (e.g., e-mail: `@@`→`@`, `lower()`, `.com` se domínio sem ponto).
---
* **Precisão numérica**

  * Antes: `float` + `round()` heterogêneo;
  * Agora: **`Decimal`** + `quantize`, com regras explícitas por produto:

    * Diesel: 0 casas (`ROUND_HALF_UP`),
    * Gasolina: 2 casas (`ROUND_HALF_UP`),
    * Outros: **truncar** 2 casas (`ROUND_DOWN`).
  * Resultado: **determinismo monetário** (sem erro binário de `float`).
---
* **Persistência previsível**

  * `Cliente.to_storage_format()` padroniza **CSV de 3 colunas** (`nome,email,cnpj`) em `src/clientes.txt` (antes gravava `str(obj)` ou campos incompletos).


---


## Melhorias de SOLID

* **SRP (Single Responsibility)**

  * Antes: funções misturavam validação, I/O, formatação de saída e regra de negócio.
  * Agora:

    * `domain/cliente.py` e `domain/pedido.py` → **entidades puras** (validam e normalizam dados; sem I/O).
    * `services/servico_cliente.py` → **caso de uso** de cadastro (orquestra validação/persistência/notificação).
    * `services/preco_calculadora.py` → **cálculo de preços** separado, com pipeline claro.
---
* **DIP (Dependency Inversion)**

  * Antes: `cadastrar_cliente` escrevia diretamente em arquivo e “enviava e-mail” com `print`.
  * Agora: portas **`ClienteRepository`** e **`NotificationService`** (Protocols) são injetadas; o serviço depende de **abstrações**, não de implementações. Trocar arquivo por banco/SMTP não muda o caso de uso.
---
* **OCP / LSP (Open/Closed + Liskov)**

  * Antes: cadeias de `if/elif` para produto/cupom – cada novo produto quebraria o código existente.
  * Agora: **Strategy** por produto (`EstrategiaDiesel/Gasolina/Etanol/Lubrificante` herdam de `EstrategiaPreco`).

    * **OCP**: novas regras = nova classe (sem editar código velho).
    * **LSP**: todas as estratégias expõem a mesma interface (`calcular_bruto`, `aplicar_cupom`, `arredondar`) e podem ser trocadas sem quebrar o cliente.
---
* **ISP (Interface Segregation) — na prática**

  * Portas enxutas e específicas: `ClienteRepository.save(...)` e `NotificationService.send_welcome_email(...)`. O serviço não é obrigado a conhecer métodos que não usa.
---
* **Alta coesão & baixo acoplamento**

  * Domínio sem I/O; services orquestram; adapters concretos ficam nas bordas. Isso **facilita testes** e evolução.


------------------------------------------------------------------------

## ⚙️ Como o Sistema Funciona

### A. `main.py`

-   Cria adaptadores reais
-   Injeta dependências
-   Executa cadastro e processamento de pedidos

### B. Cadastro de Clientes

1.  Criação do objeto `Cliente` (com validação automática)
2.  Salvamento através da Porta
3.  Notificação via Porta

### C. Processamento de Pedidos

-   Cada etapa isolada:
    -   `_preco_bruto`
    -   `_aplicar_cupom`
    -   `_arredondar_final`

------------------------------------------------------------------------

##  Como Rodar

``` bash
cd repo_petrobahia
python -m src.main
```

O uso de `-m` garante imports corretos dentro do pacote.

------------------------------------------------------------------------

##  Saída Esperada

    ==== Início processamento PetroBahia ====

    Cliente com problema: {...}
    Cliente cadastrado: Carlos <carlos@petrobahia.com>
    Pedido ok: TransLog, diesel, qtd=1200 => 4309.20
    Pedido ok: MoveMais, gasolina, qtd=300 => 1466.70
    Pedido ok: EcoFrota, etanol, qtd=50 => 170.55
    Pedido ok: PetroPark, lubrificante, qtd=12 => 294.00

    TOTAL = 6240.45

    ==== Fim processamento PetroBahia ====

