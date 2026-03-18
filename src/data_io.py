import pandas as pd
import os
from pathlib import Path
import config

def sanitize_id(series: pd.Series) -> pd.Series:
    """
    pandasの仕様で欠損値混じりの列がfloat型（例: 8200003.0）や 'nan' になるのを防ぎ、
    純粋な文字列に変換する共通ヘルパー関数。
    """
    return series.fillna('').astype(str).str.replace(r'\.0$', '', regex=True).replace('nan', '').str.strip()

def load_applicants(term: str) -> pd.DataFrame:
    file_path = config.INPUT_DIR / term / "applicants.csv"
    if not file_path.exists():
        return pd.DataFrame()

    df = pd.read_csv(file_path)

    col_single = "階数希望選択（共同利用者なし）"
    col_pair = "階数希望選択（共同利用者あり）"
    if col_single in df.columns and col_pair in df.columns:
        df["希望階"] = df[col_single].fillna(df[col_pair])
    else:
        df["希望階"] = pd.NA

    df["結果"] = "S0"

    # 読み込み直後にIDをサニタイズ
    for col in ["申請者の学籍番号", "共同利用者の学籍番号"]:
        if col in df.columns:
            df[col] = sanitize_id(df[col])

    return df

def load_partners(term: str) -> pd.DataFrame:
    file_path = config.INPUT_DIR / term / "partners.csv"
    if not file_path.exists():
        return pd.DataFrame()

    df = pd.read_csv(file_path)
    df["結果"] = "S0"

    if "共同利用者の学籍番号" in df.columns:
        df["共同利用者の学籍番号"] = sanitize_id(df["共同利用者の学籍番号"])

    return df

def load_winner_history() -> pd.DataFrame:
    file_path = config.DATA_DIR / "winner_history.csv"
    if not file_path.exists():
        cols = ["申請者氏名", "申請者学籍番号", "共同利用者氏名", "共同利用者学籍番号", "処理日", "割り当てロッカー"]
        return pd.DataFrame(columns=cols)

    df = pd.read_csv(file_path)
    # 履歴データのIDもサニタイズ
    for col in ["申請者学籍番号", "共同利用者学籍番号", "割り当てロッカー"]:
        if col in df.columns:
            df[col] = sanitize_id(df[col])
    return df

def load_locker_master() -> pd.DataFrame:
    file_path = config.DATA_DIR / "locker_master.csv"
    if not file_path.exists():
        return pd.DataFrame(columns=["ロッカー番号", "割り当て状態"])

    df = pd.read_csv(file_path)
    for col in ["ロッカー番号", "割り当て状態"]:
        if col in df.columns:
            df[col] = sanitize_id(df[col])
    return df

def save_csv(df: pd.DataFrame, output_path: Path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False, encoding="utf-8-sig")