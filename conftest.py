"""
conftest.py — raíz del módulo agentes-ia.
Agrega este directorio al path para que los subpaquetes (etapa-1/, etapa-2/)
puedan hacer `from utils import ...` sin importación relativa.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
