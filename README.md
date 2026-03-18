# Locker Manage System

週次のロッカー申請を `validate` で自動判定し、管理者が `manual_status=keep/reject` を付けた `review_*.csv` をもとに `lottery` を実行する CLI です。

## 運用フロー

1. `config/default.yml` を基準に設定を確認する。
1. `validate` を実行して `output/<term>/validation/` と `output/<term>/review/` を生成する。
1. `output/<term>/review/review_*.csv` を管理者が確認し、`manual_status` を `keep` または `reject` に更新する。
1. `lottery` を実行して `output/<term>/lottery/` に当選結果を出力する。

## 入力と出力

- 入力は `demo-input/applicant_data.csv` と `demo-input/partner_data.csv` を想定する。
- `validate` の出力は機械判定用の `validation/` と人手確認用の `review/` に分かれる。
- `lottery` の出力は `result.csv`、`locker_assignments.csv`、`lottery_log.csv`、PDF である。

## 使い方

```bash
locker-manage-system validate \
  --config config/default.yml \
  --term term1 \
  --input-dir demo-input \
  --state-dir state \
  --output-dir output

locker-manage-system lottery \
  --config config/default.yml \
  --term term1 \
  --review-dir output/term1/review \
  --state-dir state \
  --output-dir output
```

## 実行ファイル化

PyInstaller で OS ごとに個別ビルドする。`Linux`、`Windows`、`macOS` でそれぞれビルドした実行ファイルを配布する前提にする。

```bash
pyinstaller packaging/pyinstaller.spec
```

## 補足

- 学生証画像 URL は管理者確認用の情報として保持する。
- 公開 PDF には申請者の学籍番号のみを掲載する。
