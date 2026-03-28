# Locker Manage System

週次のロッカー申請を `validate` で自動判定し、管理者が `manual_status=keep/reject` を付けた `review_*.csv` をもとに `lottery` を実行する CLI です。

## 実行環境

- 開発時は `uv` と Python 3.10 以上を想定する。
- 配布時は PyInstaller で単体実行ファイル化する。
- 実行ファイルは `Linux`、`Windows`、`macOS` それぞれの OS 上で別々にビルドする。

## セットアップ

初回はリポジトリ直下で次を実行する。

```bash
uv sync --group dev
```

依存更新後に lock を更新する場合:

```bash
uv lock
```

## 運用フロー

1. `config/default.yml` を確認する。
1. 引数なしで起動し、`validate` か `lottery`、開始日、終了日を対話入力する。
1. `validate` を実行して `output/<term>/validation/` と `output/<term>/review/` を生成する。
1. `output/<term>/review/review_*.csv` を管理者が確認し、`manual_status` を `keep` または `reject` に更新する。
1. `lottery` を実行して `output/<term>/lottery/` に当選結果を出力する。

## 対話入力

引数なしで起動すると、次を順に聞く。

1. `validate` か `lottery`
1. 開始日
1. 終了日

開始日と終了日は `YYYY-MM-DD` 形式で入力する。例:

```text
開始日を入力してください（例: 2026-04-01）
終了日を入力してください（例: 2026-04-07）
```

誤った文字列を入力した場合は再入力になる。終了日が開始日より前なら、開始日から聞き直す。強制終了したい場合は `Ctrl+C` を使う。

## 理想的なファイル構成

次の構成なら、`--term` 以外の引数なしで動く。

```text
.
├── config/
│   └── default.yml
├── input/
│   ├── applicant_data.csv
│   └── partner_data.csv
├── output/
│   ├── state/
│   │   └── 2026/
│   │       ├── winners.csv
│   │       └── locker_assignments.csv
│   └── 2026-04-01..2026-04-07/
│       ├── validation/
│       ├── review/
│       └── lottery/
└── dist/
    └── locker-manage-system
```

`output/state/<year>/` の `<year>` は `--term` の開始日から自動決定する。例えば `2026-04-01..2026-04-07` なら `output/state/2026/` を使う。

## 入力と出力

- 入力は `input/applicant_data.csv` と `input/partner_data.csv` を想定する。
- `validate` の出力は機械判定用の `validation/` と人手確認用の `review/` に分かれる。
- `lottery` の出力は `result.csv`、`locker_assignments.csv`、`lottery_log.csv`、PDF である。

## 実行方法

### Python から直接実行する場合

リポジトリ直下で次を実行する。

```bash
uv run locker-manage-system
```

### 実行ファイルから実行する場合

Linux / macOS:

```bash
./dist/locker-manage-system
```

Windows:

```powershell
.\dist\locker-manage-system.exe
```

サブコマンドを使う既存方式も残している。`validate --term ...` や `lottery --term ...` を指定した場合は対話をスキップする。

## 引数の説明

通常運用では引数なしでよい。サブコマンド指定時だけ次の引数を使う。

- `--term`
  対象期間。形式は `YYYY-MM-DD..YYYY-MM-DD`。開始日の 00:00:00 から終了日の 23:59:59 までを有効期間として扱い、期間外の応募は `E1` とする。出力先の `output/<term>/...` にもこの文字列を使う。
- `--config`
  省略時は `config/default.yml`。
- `--input-dir`
  `validate` 専用。省略時は `input/`。
- `--state-dir`
  省略時は `output/state/<termの開始年>/`。
- `--output-dir`
  省略時は `output/`。
- `--review-dir`
  `lottery` 専用。省略時は `output/<term>/review/`。
- `--seed`
  `lottery` 専用。抽選の乱数シード。省略可能。

## ビルド方法

依存関係は `uv` で入れる。

```bash
uv sync --group dev
```

その後、対象 OS 上で次を実行する。

```bash
uv run pyinstaller packaging/pyinstaller.spec
```

生成物:

- Linux / macOS: `dist/locker-manage-system`
- Windows: `dist/locker-manage-system.exe`

補足:

- `Linux` 版は Linux 上でビルドする。
- `Windows` 版は Windows 上でビルドする。
- `macOS` 版は macOS 上でビルドする。
- 別 OS 向けの実行ファイルをこの 1 台からまとめて作ることは前提にしない。

## テスト

```bash
uv run pytest -v
```

## 補足

- 学生証画像 URL は管理者確認用の情報として保持する。
- 公開 PDF には申請者の学籍番号のみを掲載する。
