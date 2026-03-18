# Locker Manage System

週次のロッカー申請を `validate` で自動判定し、管理者が `manual_status=keep/reject` を付けた `review_*.csv` をもとに `lottery` を実行する CLI です。

## 実行環境

- 開発時は Python 3.10 以上を想定する。
- 配布時は PyInstaller で単体実行ファイル化する。
- 実行ファイルは `Linux`、`Windows`、`macOS` それぞれの OS 上で別々にビルドする。

## 運用フロー

1. `config/default.yml` を基準に設定を確認する。
1. `validate` を実行して `output/<term>/validation/` と `output/<term>/review/` を生成する。
1. `output/<term>/review/review_*.csv` を管理者が確認し、`manual_status` を `keep` または `reject` に更新する。
1. `lottery` を実行して `output/<term>/lottery/` に当選結果を出力する。

## 入力と出力

- 入力は `demo-input/applicant_data.csv` と `demo-input/partner_data.csv` を想定する。
- `validate` の出力は機械判定用の `validation/` と人手確認用の `review/` に分かれる。
- `lottery` の出力は `result.csv`、`locker_assignments.csv`、`lottery_log.csv`、PDF である。

## 実行方法

### Python から直接実行する場合

リポジトリ直下で次を実行する。

```bash
PYTHONPATH=src python -m locker_manage_system.main validate \
  --config config/default.yml \
  --term term1 \
  --input-dir demo-input \
  --state-dir state \
  --output-dir output

PYTHONPATH=src python -m locker_manage_system.main lottery \
  --config config/default.yml \
  --term term1 \
  --review-dir output/term1/review \
  --state-dir state \
  --output-dir output
```

### 実行ファイルから実行する場合

Linux / macOS:

```bash
./locker-manage-system validate \
  --config config/default.yml \
  --term term1 \
  --input-dir demo-input \
  --state-dir state \
  --output-dir output

./locker-manage-system lottery \
  --config config/default.yml \
  --term term1 \
  --review-dir output/term1/review \
  --state-dir state \
  --output-dir output
```

Windows:

```powershell
.\locker-manage-system.exe validate `
  --config config/default.yml `
  --term term1 `
  --input-dir demo-input `
  --state-dir state `
  --output-dir output

.\locker-manage-system.exe lottery `
  --config config/default.yml `
  --term term1 `
  --review-dir output/term1/review `
  --state-dir state `
  --output-dir output
```

## 引数の説明

### 共通引数

- `--config`
  設定ファイルのパス。年度、各階のロッカー数、利用条件、ロッカー番号範囲をここから読む。
- `--term`
  今回の処理単位名。`term1` などの名前を付け、出力先の `output/<term>/...` に使う。
- `--state-dir`
  年度内で引き継ぐ状態ファイルを置くディレクトリ。`winners.csv` と `locker_assignments.csv` をここから読む。

### `validate` の引数

- `--input-dir`
  入力 CSV の置き場所。この中に `applicant_data.csv` と `partner_data.csv` が必要。
- `--output-dir`
  自動判定結果の出力先の親ディレクトリ。`output/<term>/validation/` と `output/<term>/review/` が作られる。

### `lottery` の引数

- `--review-dir`
  管理者が `manual_status` を編集した `review_*.csv` の置き場所。通常は `output/<term>/review/` を指定する。
- `--output-dir`
  抽選結果の出力先の親ディレクトリ。`output/<term>/lottery/` が作られる。
- `--seed`
  抽選の乱数シード。省略可能。同じ入力と同じシードを使うと再現しやすい。

## ビルド方法

まず依存関係を入れる。

```bash
pip install -e .
pip install pyinstaller
```

その後、対象 OS 上で次を実行する。

```bash
pyinstaller packaging/pyinstaller.spec
```

生成物:

- Linux / macOS: `dist/locker-manage-system`
- Windows: `dist/locker-manage-system.exe`

補足:

- `Linux` 版は Linux 上でビルドする。
- `Windows` 版は Windows 上でビルドする。
- `macOS` 版は macOS 上でビルドする。
- 別 OS 向けの実行ファイルをこの 1 台からまとめて作ることは前提にしない。

## 補足

- 学生証画像 URL は管理者確認用の情報として保持する。
- 公開 PDF には申請者の学籍番号のみを掲載する。
