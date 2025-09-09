# Estrutura do Projeto

A estrutura do projeto CrawJUD é organizada da seguinte forma:

```powershell
CrawJUD
├───crawjud
│   ├───api
│   │   ├───namespaces
│   │   └───routes
│   │       ├───bot
│   │       ├───config
│   │       └───execution
│   ├───bots
│   │   ├───caixa
│   │   │   └───resources
│   │   ├───calculadoras
│   │   ├───csi
│   │   ├───elaw
│   │   │   └───cadastro
│   │   ├───esaj
│   │   │   └───capa
│   │   ├───jusbr
│   │   ├───pje
│   │   │   └───protocolo
│   │   └───projudi
│   │       └───capa
│   ├───common
│   │   └───exceptions
│   │       └───bot
│   ├───controllers
│   │   └───main
│   ├───custom
│   ├───decorators
│   ├───interfaces
│   │   ├───controllers
│   │   ├───dict
│   │   ├───formbot
│   │   ├───pje
│   │   └───types
│   │       ├───bots
│   │       └───celery
│   ├───models
│   ├───resources
│   │   └───elements
│   ├───tasks
│   │   └───mail
│   │       └───templates
│   └───utils
│       ├───interfaces
│       ├───logger
│       │   └───handlers
│       ├───models
│       ├───storage
│       │   └───credentials
│       ├───webdriver
│       │   └───config
│       └───xlsx_generator
│           └───models
└───docs

```
