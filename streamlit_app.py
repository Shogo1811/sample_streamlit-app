"""SiSエントリーポイント — src/app.py を実行するラッパー"""

import os
import sys

# SiS環境で src/ パッケージを参照可能にする
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.app import main  # noqa: E402

main()
