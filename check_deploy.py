#!/usr/bin/env python
"""
Script para verificar que todo está listo para desplegar a Render
"""
import os
import sys

def check_file(path, description):
    """Verificar que un archivo existe"""
    if os.path.exists(path):
        print(f"✓ {description}")
        return True
    else:
        print(f"✗ {description} - FALTA: {path}")
        return False

def check_directory(path, description):
    """Verificar que una carpeta existe"""
    if os.path.isdir(path):
        print(f"✓ {description}")
        return True
    else:
        print(f"✗ {description} - FALTA: {path}")
        return False

def main():
    print("=" * 60)
    print("VERIFICACIÓN PRE-DEPLOY A RENDER")
    print("=" * 60)
    print()
    
    checks = []
    
    print("ESTRUCTURA DE CARPETAS:")
    checks.append(check_directory("backend", "  Backend directory"))
    checks.append(check_directory("backend/services", "  Services directory"))
    print()
    
    print("ARCHIVOS REQUERIDOS:")
    checks.append(check_file("backend/app.py", "  Flask application"))
    checks.append(check_file("backend/requirements.txt", "  Requirements"))
    checks.append(check_file("backend/.env.example", "  .env example"))
    checks.append(check_file("backend/services/sii_scraper.py", "  SII Scraper"))
    print()
    
    print("ARCHIVOS DE DEPLOY:")
    checks.append(check_file("render.yaml", "  render.yaml configuration"))
    checks.append(check_file("Procfile", "  Procfile"))
    checks.append(check_file(".gitignore", "  .gitignore"))
    print()
    
    print("DOCUMENTACIÓN:")
    checks.append(check_file("README.md", "  README"))
    checks.append(check_file("DEPLOY_RENDER_PASO_A_PASO.md", "  Deploy guide"))
    print()
    
    # Verificar requirements.txt contiene lo necesario
    print("DEPENDENCIAS (requirements.txt):")
    try:
        with open("backend/requirements.txt", "r") as f:
            content = f.read().lower()
            deps = [
                ("flask", "Flask"),
                ("flask-cors", "Flask-CORS"),
                ("playwright", "Playwright"),
                ("gunicorn", "Gunicorn"),
                ("python-dotenv", "python-dotenv"),
            ]
            
            for dep, name in deps:
                if dep in content:
                    print(f"  ✓ {name}")
                    checks.append(True)
                else:
                    print(f"  ✗ {name} - FALTA")
                    checks.append(False)
    except Exception as e:
        print(f"  ✗ Error leyendo requirements.txt: {e}")
        checks.append(False)
    
    print()
    
    # Resumen
    total = len(checks)
    passed = sum(checks)
    failed = total - passed
    
    print("=" * 60)
    print(f"RESULTADO: {passed}/{total} verificaciones pasaron")
    print("=" * 60)
    
    if failed == 0:
        print()
        print("✓ TODOS LOS CHECKS PASARON")
        print()
        print("Próximos pasos:")
        print("  1. git add . && git commit -m 'Ready for deploy'")
        print("  2. git push origin main")
        print("  3. Ir a https://render.com")
        print("  4. Conectar GitHub y seguir guía DEPLOY_RENDER_PASO_A_PASO.md")
        print()
        return 0
    else:
        print()
        print(f"✗ {failed} verificaciones FALLARON")
        print()
        print("Debes arreglar los errores antes de desplegar.")
        print()
        return 1

if __name__ == "__main__":
    sys.exit(main())
