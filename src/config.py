# ライブラリの読み込み
import os
from pathlib import Path

# ベースディレクトリの取得 (srcの親ディレクトリ)
BASE_DIR = Path(__file__).resolve().parent.parent

# フォルダパスの定義
DATA_DIR = BASE_DIR / "data"
INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"

# 正規表現パターン
# 先頭15で残り5桁、または先頭4か8で2桁目が1〜6、残り5桁
STUDENT_ID_PATTERN = r'^(15\d{5}|[48][1-6]\d{5})$'

# ロッカーの仕様定義（階ごとの個数と利用人数条件）
LOCKER_CAPACITY = {
    "2F": {"count": 420, "capacity": 2},
    "3F": {"count": 240, "capacity": 2},
    "4F": {"count": 240, "capacity": 1},
    "5F": {"count": 240, "capacity": 1},
    "6F": {"count": 240, "capacity": 1},
}

# エラーコードの定義
ERROR_CODES = {
    "S0": "成功",
    "E1": "入力値エラー",
    "E2": "共同利用者不在エラー",
    "E3": "当選済みエラー",
    "E4": "マッチング済みエラー",
}

# 必須カラム名（pandasで読み込む際の列名定義）
REQUIRED_COLS_APP = [
    "タイムスタンプ", "メールアドレス", "規約への同意",
    "申請者の学籍番号", "申請者の氏名", "申請者の学生証写真",
    "共同利用者の有無", "共同利用者の学籍番号", "共同利用者の氏名",
    "階数希望選択（共同利用者なし）", "階数希望選択（共同利用者あり）"
]

REQUIRED_COLS_PAR = [
    "タイムスタンプ", "メールアドレス", "規約への同意",
    "共同利用者の学籍番号", "共同利用者の氏名", "共同利用者の学生証写真"
]