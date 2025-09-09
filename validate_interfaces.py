#!/usr/bin/env python3
"""Script de validação da nova estrutura de interfaces reorganizadas.

Este script demonstra como usar a nova organização baseada em domínios
e valida que os imports essenciais estão funcionando corretamente.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Adiciona o diretório do projeto ao path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def test_core_types() -> bool:
    """Testa os tipos básicos e fundamentais."""
    try:
        from crawjud.interfaces.core import (
            DictData,
            ListData,
            PyNumbers,
            StatusType,
            StrProcessoCNJ,
        )

        print("✓ Core types: DictData, ListData, PyNumbers, StatusType, StrProcessoCNJ")
        
        # Teste de uso básico
        status: StatusType = "Em Execução"
        data: DictData = {"processo": "1234567-89.2023.1.00.0001", "status": status}
        
        print(f"  - Exemplo de uso: {data}")
        return True
    except ImportError as e:
        print(f"❌ Erro ao importar tipos core: {e}")
        return False


def test_auth_types() -> bool:
    """Testa os tipos de autenticação."""
    try:
        from crawjud.interfaces.auth import CurrentUser, SessionDict

        print("✓ Auth types: CurrentUser, SessionDict")
        
        # Teste de uso básico
        user: CurrentUser = {
            "id": 1,
            "login": "usuario.teste",
            "nome_usuario": "Usuário de Teste",
            "email": "teste@exemplo.com",
        }
        
        print(f"  - Exemplo de uso: {user['nome_usuario']} ({user['email']})")
        return True
    except ImportError as e:
        print(f"❌ Erro ao importar tipos auth: {e}")
        return False


def test_module_imports() -> bool:
    """Testa as importações dos módulos principais."""
    try:
        from crawjud.interfaces import auth, core

        print("✓ Módulos principais: core, auth")
        print(f"  - Core exports: {len(core.__all__)} tipos")
        print(f"  - Auth exports: {len(auth.__all__)} tipos")
        return True
    except ImportError as e:
        print(f"❌ Erro ao importar módulos: {e}")
        return False


def test_interface_module() -> bool:
    """Testa o módulo principal de interfaces."""
    try:
        import crawjud.interfaces

        print("✓ Módulo principal de interfaces")
        print(f"  - Módulos disponíveis: {crawjud.interfaces.__all__}")
        print(f"  - ASyncServerType: {hasattr(crawjud.interfaces, 'ASyncServerType')}")
        return True
    except ImportError as e:
        print(f"❌ Erro ao importar interfaces: {e}")
        return False


def show_new_structure() -> None:
    """Mostra a nova estrutura de organização."""
    print("\n📁 Nova Estrutura Baseada em Domínios:")
    print("├── core/           # Tipos básicos, primitivos e customizados")
    print("│   ├── primitives.py")
    print("│   ├── literals.py")
    print("│   └── custom.py")
    print("├── auth/           # Tipos de autenticação e sessão")
    print("│   ├── session.py")
    print("│   └── credentials.py")
    print("├── bots/           # Tipos relacionados aos bots")
    print("│   ├── data.py")
    print("│   ├── pje.py")
    print("│   └── projudi.py")
    print("├── systems/        # Tipos de sistemas externos")
    print("│   ├── pje/")
    print("│   └── webdriver/")
    print("├── tasks/          # Tipos de tarefas assíncronas")
    print("├── forms/          # Tipos de formulários")
    print("└── controllers/    # Tipos de controladores")


def show_usage_examples() -> None:
    """Mostra exemplos de uso da nova estrutura."""
    print("\n🚀 Exemplos de Uso:")
    print()
    print("# Tipos básicos e primitivos")
    print("from crawjud.interfaces.core import DictData, StatusType, StrProcessoCNJ")
    print()
    print("# Tipos de autenticação")
    print("from crawjud.interfaces.auth import SessionDict, CurrentUser")
    print()
    print("# Importação por módulo")
    print("from crawjud.interfaces import core, auth")
    print("user_data: auth.CurrentUser = {...}")
    print("process_data: core.DictData = {...}")


def main() -> None:
    """Função principal do script de validação."""
    print("🔍 Validação da Nova Estrutura de Interfaces CrawJUD")
    print("=" * 60)
    
    # Lista de testes
    tests = [
        ("Tipos Core", test_core_types),
        ("Tipos Auth", test_auth_types),
        ("Importação de Módulos", test_module_imports),
        ("Módulo Principal", test_interface_module),
    ]
    
    # Executa testes
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Testando: {test_name}")
        if test_func():
            passed += 1
        else:
            print(f"❌ Falha no teste: {test_name}")
    
    # Resultados
    print(f"\n📊 Resultados: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 Todos os testes passaram! A reorganização foi bem-sucedida.")
        show_new_structure()
        show_usage_examples()
        
        print("\n✨ Benefícios da Nova Organização:")
        print("• Organização por domínio de responsabilidade")
        print("• Imports mais claros e intuitivos")
        print("• Redução de acoplamento entre módulos")
        print("• Facilita manutenção e evolução")
        print("• Documentação mais organizada")
        
    else:
        print("❌ Alguns testes falharam. Verifique os erros acima.")
        sys.exit(1)


if __name__ == "__main__":
    main()