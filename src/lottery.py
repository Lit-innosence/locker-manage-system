import pandas as pd
import datetime
import config
from data_io import load_locker_master, load_winner_history, save_csv, sanitize_id
from pdf_generator import generate_pdf

def initialize_locker_master():
    ranges = {
        '2': (2001, 2420), '3': (3001, 3240), '4': (4001, 4240),
        '5': (5001, 5240), '6': (6001, 6240)
    }
    data = []
    for floor, (start, end) in ranges.items():
        for num in range(start, end + 1):
            data.append({"ロッカー番号": num, "割り当て状態": ""})

    return pd.DataFrame(data)

def run_lottery(term: str):
    print(f"\n[{term}] 抽選処理を開始します...")

    master_df = load_locker_master()
    if master_df.empty or "ロッカー番号" not in master_df.columns:
        master_df = initialize_locker_master()
        print(">> ロッカー確定表（マスター）を初期化しました。")

    is_empty_locker = master_df["割り当て状態"].isna() | (master_df["割り当て状態"].astype(str).str.strip() == "")

    today_str = datetime.date.today().strftime("%Y-%m-%d")
    new_winners = []
    log_dir = config.OUTPUT_DIR / term / "log"

    for floor in ['2', '3', '4', '5', '6']:
        file_path = log_dir / f"valid_{floor}F.csv"
        if not file_path.exists():
            continue

        df = pd.read_csv(file_path)

        # 読み込み直後のサニタイズ（.0 と nan の除去）
        for col in ["申請者の学籍番号", "共同利用者の学籍番号"]:
            if col in df.columns:
                df[col] = sanitize_id(df[col])
        for col in ["申請者の氏名", "共同利用者の氏名"]:
            if col in df.columns:
                df[col] = df[col].fillna('')

        if df.empty or "学生証照合(TRUE/FALSE)" not in df.columns:
            continue

        valid_mask = df["学生証照合(TRUE/FALSE)"].astype(str).str.upper().isin(['TRUE', '1', '1.0'])
        candidates = df[valid_mask].copy()

        if candidates.empty:
            continue

        floor_mask = master_df["ロッカー番号"].astype(str).str.startswith(floor)
        available_lockers = master_df[floor_mask & is_empty_locker]["ロッカー番号"].tolist()

        available_count = len(available_lockers)
        applicant_count = len(candidates)

        print(f"  {floor}F: 応募数 {applicant_count}名 / 空き枠 {available_count}個")

        if available_count == 0:
            print(f"    -> {floor}Fの空き枠がありません。抽選をスキップします。")
            continue

        if applicant_count > available_count:
            winners = candidates.sample(n=available_count, random_state=None)
            print(f"    -> 定員オーバーのため抽選を実施し、{available_count}名が当選しました。")
        else:
            winners = candidates
            print(f"    -> 全員当選しました。")

        assigned_lockers = available_lockers[:len(winners)]
        winners["割り当てロッカー"] = assigned_lockers
        winners["処理日"] = today_str

        for idx, row in winners.iterrows():
            locker_no = row["割り当てロッカー"]

            m_idx = master_df[master_df["ロッカー番号"] == locker_no].index
            if not m_idx.empty:
                master_df.loc[m_idx[0], "割り当て状態"] = row["申請者の学籍番号"]

            new_winners.append({
                "申請者氏名": row["申請者の氏名"],
                "申請者学籍番号": row["申請者の学籍番号"],
                "共同利用者氏名": row.get("共同利用者の氏名", ""),
                "共同利用者学籍番号": row.get("共同利用者の学籍番号", ""),
                "処理日": row["処理日"],
                "割り当てロッカー": locker_no
            })

    if not new_winners:
        print(">> 今回の抽選による新規当選者はいませんでした。")
        return

    save_csv(master_df, config.DATA_DIR / "locker_master.csv")

    result_df = pd.DataFrame(new_winners)
    result_df = result_df.sort_values(by=["処理日", "割り当てロッカー"])
    save_csv(result_df, config.OUTPUT_DIR / term / "result.csv")

    history_df = load_winner_history()
    history_df = pd.concat([history_df, result_df], ignore_index=True)
    history_df = history_df.sort_values(by=["処理日", "割り当てロッカー"])
    save_csv(history_df, config.DATA_DIR / "winner_history.csv")

    print("\n>> 抽選結果の保存が完了しました。")
    print(f">> 出力先: {config.OUTPUT_DIR / term / 'result.csv'}")

    generate_pdf(term)

if __name__ == "__main__":
    run_lottery("term1")