import sys
from validator import run_validation
from lottery import run_lottery

def show_menu():
    """メニュー画面の表示"""
    print("\n" + "="*45)
    print(" ロッカー管理システム - メニュー")
    print("="*45)
    print("  [1] バリデーション処理を実行")
    print("  [2] 抽選処理を実行")
    print("  [0] システムを終了")
    print("="*45)

def main():
    print("システムを起動しました。")

    while True:
        show_menu()
        choice = input("実行する処理の番号（0〜2）を入力してください: ").strip()

        if choice == '0':
            print("システムを終了します。お疲れ様でした。")
            sys.exit(0)

        elif choice == '1':
            term = input("対象の期間を入力してください（例: term1）: ").strip()
            if not term:
                print("※期間が入力されませんでした。メニューに戻ります。")
                continue

            print(f"\n>>> 【{term}】のバリデーション処理を開始します...")
            run_validation(term)
            print(">>> バリデーション処理が完了しました。")
            print(f">>> 「output/{term}/log/」内のCSVを確認して、学生証写真の照合を行ってください。")

        elif choice == '2':
            term = input("対象の期間を入力してください（例: term1）: ").strip()
            if not term:
                print("※期間が入力されませんでした。メニューに戻ります。")
                continue

            print(f"\n>>> 【{term}】の抽選処理を開始します...")
            run_lottery(term)
            print(">>> 抽選処理と結果の出力が完了しました。")
            print(f">>> 「output/{term}/」内のPDFおよびCSVを確認してください。")

        else:
            print("※無効な入力です。0, 1, 2 のいずれかを半角数字で入力してください。")

if __name__ == "__main__":
    main()