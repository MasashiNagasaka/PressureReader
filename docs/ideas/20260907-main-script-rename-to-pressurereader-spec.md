# ファイル名統一（PressureReader.py） 仕様書

> 作成日: 2026-09-07
> ステータス: Draft
> 用途: `/add-feature` での実装入力

---

## 1. 背景・目的

現在の主実行ファイル名は `src/PressReader_v3.5.0.py` だが、
プロダクト名（PressureReader）と表記ゆれがあり、バージョン番号依存のファイル名にもなっている。

本仕様では、主実行ファイル名を `PressureReader.py` に統一し、
起動手順・ドキュメント・参照箇所の整合を取る。

---

## 2. スコープ

### 2.1 実施すること
- 主実行ファイルを `src/PressReader_v3.5.0.py` から `src/PressureReader.py` へリネームする。
- 実行コマンド・参照パスが残っているドキュメントを新ファイル名へ更新する。
- リネーム後にアプリが起動可能であることを確認する。

### 2.2 実施しないこと
- 画面機能・解析ロジックの仕様変更。
- 既存メタデータ仕様や出力フォーマットの変更。
- クラス名/関数名の大規模リファクタリング。

---

## 3. ユーザーストーリー

- 開発者として、主実行ファイル名がプロダクト名と一致していてほしい。
- 開発者として、バージョン番号に依存しない固定ファイル名で起動したい。
- 開発者として、README や仕様書の手順どおりに実行して迷わない状態にしたい。

---

## 4. 仕様

### 4.1 ファイル名変更
- [ ] `src/PressReader_v3.5.0.py` を `src/PressureReader.py` に変更する。
- [ ] 旧ファイル名は `src` 配下に残さない。

### 4.2 参照更新（最小対象）
- [ ] `README.md` の実行コマンドを `python src/PressureReader.py` へ更新する。
- [ ] `docs/repository-structure.md` の主実行ファイル記述を更新する。
- [ ] `docs/functional-design.md` の主体ファイル記述を更新する。
- [ ] `docs/ideas/` 配下の関連仕様書で、実装対象として `src/PressReader_v3.5.0.py` を参照している箇所を `src/PressureReader.py` に更新する。

### 4.3 互換性方針
- [ ] 今回は互換ラッパー（旧ファイル名の薄い起動用スクリプト）は作成しない。
- [ ] 起動手順は新ファイル名に一本化する。

---

## 5. 品質要件

- 機能互換: リネーム前と同等に起動できること。
- 保守性: 今後のバージョン更新時にファイル名変更が不要であること。
- 一貫性: コードと主要ドキュメントの表記が一致していること。

---

## 6. 実装メモ（/add-feature 引き継ぎ）

### 6.1 変更対象（想定）
- `src/PressReader_v3.5.0.py` → `src/PressureReader.py`
- `README.md`
- `docs/repository-structure.md`
- `docs/functional-design.md`
- `docs/ideas/20260907-screen-clear-feature-spec.md`
- `docs/ideas/20260907-titlebar-text-change-spec.md`

### 6.2 作業順
1. 実行ファイルをリネーム。
2. `rg` で旧ファイル名の残存を検索し、必要箇所を更新。
3. 指定Pythonで構文チェック/起動確認（ユーザー運用手順に合わせる）。

### 6.3 起動確認コマンド
- `C:\nagasaka\python\testPressR\Scripts\python.exe src\PressureReader.py`

---

## 7. 受け入れ条件

- [ ] `src/PressureReader.py` が存在する。
- [ ] `src/PressReader_v3.5.0.py` が存在しない。
- [ ] README の実行コマンドが `PressureReader.py` になっている。
- [ ] 主要設計書（repository-structure / functional-design）の参照名が一致している。
- [ ] `C:\nagasaka\python\testPressR\Scripts\python.exe src\PressureReader.py` で起動できる。

---

## 8. 補足（前提）

- ユーザー要望「`PressReader_v3.5.0.py` ⇒ `PressureReader.py`」に基づき、
  現在の主実行ファイル `src/PressReader_v3.5.0.py` を改名対象とする。
