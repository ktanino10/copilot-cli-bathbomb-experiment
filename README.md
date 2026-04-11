# 🛁 copilot-cli-bathbomb-experiment

🧪 GitHub Copilot CLIで画像からバスボム用3Dプリント型（モールド）を自動生成する実験記録

**Experiment: Auto-generating 3D-printable bath bomb molds from images with GitHub Copilot CLI**

## 概要

GitHub のロゴ（Octocat）の画像から、バスボム（入浴剤）用の3Dプリント型を自動生成します。
中に防水加工した写真（9cm×5.5cm）を仕込み、お湯に溶けるとサプライズが出てくるギフト用バスボムを制作するプロジェクトです。

## 生成される型（3種類）

| タイプ | 説明 | 難易度 | ロゴ忠実度 |
|--------|------|--------|-----------|
| **A: シルエット型** | バスボム自体がOctocatの形 | 上級 | ★★☆ |
| **B: レリーフ型** | 円盤＋表面にOctocat浮き彫り | 初級 | ★☆☆ |
| **C: くり抜き型** | 円盤＋Octocatの凹み模様 | 初級 | ★★★ |

各タイプごとに上型・下型の2つ割り型を出力（計6 STLファイル）。

## 使い方

```bash
# 依存ライブラリのインストール
pip install pillow numpy scipy scikit-image shapely trimesh manifold3d numpy-stl

# STLファイル生成
python generate_mold.py
```

## 出力ファイル

```
mold_A_silhouette_bottom.stl / _top.stl   — シルエット型
mold_B_relief_bottom.stl     / _top.stl   — レリーフ型
mold_C_cutout_bottom.stl     / _top.stl   — くり抜き型
```

## 3Dプリント推奨設定

| パラメータ | 設定値 |
|-----------|--------|
| プリンター | FDM |
| フィラメント | PLA |
| レイヤー高さ | 0.2mm |
| インフィル | 20〜30% |
| ブリム | あり（反り防止） |

印刷後はキャビティ内面をサンドペーパー（#400→#800）で研磨し、使用時は食品用ラップを敷いてください。

## 型の設計仕様

- キャビティ深さ: 各20mm（合計40mm = バスボム厚さ）
- 壁厚: 3mm
- ダボ穴: 4箇所（上下型の位置合わせ）
- レリーフ/くり抜き深さ: 5mm
- 写真内蔵スペース: 9cm×5.5cm対応

## ツール

- [GitHub Copilot CLI](https://githubnext.com/projects/copilot-cli/)
- Python 3 + trimesh + manifold3d（3Dブーリアン演算）
- scikit-image + shapely（画像→ポリゴン変換）

## ライセンス

MIT
