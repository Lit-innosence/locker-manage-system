import pandas as pd
import numpy as np
import config
from data_io import load_applicants, load_partners, load_winner_history, save_csv, sanitize_id

def run_validation(term: str):
    app_df = load_applicants(term)
    par_df = load_partners(term)
    win_df = load_winner_history()

    if app_df.empty:
        print("申請者データがないため、処理を終了します。")
        return

    app_df['タイムスタンプ_dt'] = pd.to_datetime(app_df['タイムスタンプ'], errors='coerce')
    if not par_df.empty:
        par_df['タイムスタンプ_dt'] = pd.to_datetime(par_df['タイムスタンプ'], errors='coerce')

    # =========================================================
    # 1. 各エラー条件の判定
    # =========================================================
    app_id_invalid = ~app_df['申請者の学籍番号'].str.match(config.STUDENT_ID_PATTERN)
    app_photo_invalid = app_df['申請者の学生証写真'].fillna('').astype(str).str.strip() == ''

    is_2_or_3F = app_df['希望階'].astype(str).str.contains(r'[23]')
    is_4_5_6F = app_df['希望階'].astype(str).str.contains(r'[456]')
    has_partner = app_df['共同利用者の有無'] == 'あり'

    floor_rule_invalid = (is_2_or_3F & ~has_partner) | (is_4_5_6F & has_partner)

    app_df['is_E1'] = app_id_invalid | app_photo_invalid | floor_rule_invalid

    app_df['is_E2'] = False
    if not par_df.empty:
        par_id_invalid = ~par_df['共同利用者の学籍番号'].str.match(config.STUDENT_ID_PATTERN)
        par_photo_invalid = par_df['共同利用者の学生証写真'].fillna('').astype(str).str.strip() == ''
        par_df['is_E1'] = par_id_invalid | par_photo_invalid

        valid_partners = par_df[~par_df['is_E1']]['共同利用者の学籍番号'].unique()
        app_df['is_E2'] = has_partner & (~app_df['共同利用者の学籍番号'].isin(valid_partners))
    else:
        app_df['is_E2'] = has_partner

    app_df['is_E3'] = False
    if not win_df.empty:
        past_winners = pd.concat([
            win_df['申請者学籍番号'],
            win_df['共同利用者学籍番号']
        ]).dropna().unique()

        app_df['is_E3'] = (
            app_df['申請者の学籍番号'].isin(past_winners) |
            app_df['共同利用者の学籍番号'].isin(past_winners)
        )

    app_df['is_E4'] = False
    valid_mask = ~(app_df['is_E1'] | app_df['is_E2'] | app_df['is_E3'])
    candidates = app_df[valid_mask].copy()

    if not candidates.empty:
        candidates = candidates.sort_values('タイムスタンプ_dt', ascending=False)
        candidates = candidates.drop_duplicates(subset=['申請者の学籍番号'], keep='first')

        if not par_df.empty:
            par_times = par_df[['共同利用者の学籍番号', 'タイムスタンプ_dt', '共同利用者の学生証写真']].rename(
                columns={'タイムスタンプ_dt': 'par_time', '共同利用者の学生証写真': 'パートナー写真URL'}
            )
            par_times = par_times.sort_values('par_time').drop_duplicates('共同利用者の学籍番号', keep='first')

            candidates = pd.merge(candidates, par_times, on='共同利用者の学籍番号', how='left')
            candidates['par_time'] = candidates['par_time'].fillna(pd.Timestamp.max)
            candidates = candidates.sort_values(by=['par_time', 'タイムスタンプ_dt'], ascending=[True, False])

            mask_has_par = candidates['共同利用者の学籍番号'] != ''
            dups = candidates[mask_has_par].duplicated(subset=['共同利用者の学籍番号'], keep='first')
            candidates = candidates.drop(candidates[mask_has_par][dups].index)

        e4_mask = valid_mask & (~app_df.index.isin(candidates.index))
        app_df.loc[e4_mask, 'is_E4'] = True

    # =========================================================
    # 2. エラーコードの優先適用
    # =========================================================
    conditions = [app_df['is_E1'], app_df['is_E2'], app_df['is_E3'], app_df['is_E4']]
    choices = ['E1', 'E2', 'E3', 'E4']
    app_df['結果'] = np.select(conditions, choices, default='S0')

    if not par_df.empty:
        par_urls = par_df.sort_values('タイムスタンプ_dt').drop_duplicates('共同利用者の学籍番号', keep='first')[['共同利用者の学籍番号', '共同利用者の学生証写真']]
        par_urls = par_urls.rename(columns={'共同利用者の学生証写真': 'パートナー写真URL'})
        app_df = pd.merge(app_df, par_urls, on='共同利用者の学籍番号', how='left')
        par_df['結果'] = np.where(par_df['is_E1'], 'E1', 'S0')

    # =========================================================
    # 3. CSVファイルの出力
    # =========================================================
    log_dir = config.OUTPUT_DIR / term / "log"

    invalid_app = app_df.sort_values('タイムスタンプ_dt').drop(
        columns=['タイムスタンプ_dt', 'is_E1', 'is_E2', 'is_E3', 'is_E4', 'パートナー写真URL'], errors='ignore'
    )
    save_csv(invalid_app, log_dir / "invalid_app.csv")

    if not par_df.empty:
        invalid_par = par_df.sort_values('タイムスタンプ_dt').drop(
            columns=['タイムスタンプ_dt', 'is_E1'], errors='ignore'
        )
        save_csv(invalid_par, log_dir / "invalid_par.csv")

    valid_df = app_df[app_df['結果'] == 'S0'].sort_values('申請者の学籍番号').copy()
    valid_df["学生証照合(TRUE/FALSE)"] = ""

    if 'パートナー写真URL' in valid_df.columns:
        valid_df['共同利用者の学生証写真'] = valid_df['パートナー写真URL']
    else:
        valid_df['共同利用者の学生証写真'] = ""

    out_cols = [
        "申請者の学籍番号", "申請者の氏名", "申請者の学生証写真",
        "共同利用者の学籍番号", "共同利用者の氏名", "共同利用者の学生証写真",
        "学生証照合(TRUE/FALSE)"
    ]

    for floor in ['2', '3', '4', '5', '6']:
        floor_df = valid_df[valid_df['希望階'].astype(str).str.contains(floor)].copy()

        if floor in ['4', '5', '6']:
            floor_df["共同利用者の学籍番号"] = ""
            floor_df["共同利用者の氏名"] = ""
            floor_df["共同利用者の学生証写真"] = ""

        existing_cols = [c for c in out_cols if c in floor_df.columns]
        save_csv(floor_df[existing_cols], log_dir / f"valid_{floor}F.csv")

if __name__ == "__main__":
    run_validation("term1")