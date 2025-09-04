#!/usr/bin/env python3
"""
Скрипт запуска PoE2 Trade Assistant
"""

import sys
import os

# Добавляем src в путь
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from main import main

if __name__ == "__main__":
    main()