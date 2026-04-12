# 🛁🐱 copilot-cli-bathbomb-experiment

**[日本語](#日本語) | [English](#english)**

---

<a id="日本語"></a>
## 日本語

🧪 GitHub Copilot CLIで画像からバスボム用3Dプリント型（モールド）を自動生成する実験記録

### 概要

GitHub のロゴ（Octocat）の画像から、猫型バスボム用の3Dプリント型を自動生成します。
中に防水加工した写真（9cm×5.5cm）を仕込み、お湯に溶けるとサプライズが出てくるギフト用バスボムです。

### 生成される型

猫シルエット型の容器モールド（片面型）

- 猫のシルエットに沿った壁を持つ容器型
- 上面のみ開口（材料投入口）、底面は密閉
- 抜き勾配5°（取り出しやすい）
- フィレットR3mm（角を丸めてひび割れ防止）
- 壁厚4mm・床厚4mm

### 使い方

```bash
# 依存ライブラリのインストール
pip install pillow numpy scipy scikit-image shapely trimesh manifold3d

# STLファイル生成
python generate_mold.py
```

### 出力ファイル

```
mold_cat_container.stl  — 猫型コンテナモールド（片面型）
```

### 3Dプリント推奨設定

| パラメータ | 設定値 |
|-----------|--------|
| プリンター | FDM |
| フィラメント | PLA |
| レイヤー高さ | 0.2mm |
| インフィル | 20〜30% |
| サポート | なし |
| ブリム | あり（反り防止） |

印刷後はキャビティ内面をサンドペーパー（#400→#800）で研磨し、使用時は食品用ラップを敷いてください。

### 型の設計仕様

| 項目 | 値 |
|------|-----|
| キャビティ深さ | 25mm |
| 壁厚 | 4mm |
| 床厚 | 4mm |
| 抜き勾配 | 5° |
| フィレット | R3mm |
| 写真対応サイズ | 85×55mm以内 |

### 制作ガイド

📖 **[GUIDE.md](GUIDE.md)** — 買い出しリスト・全手順・トラブルシューティング（日本語）

📖 **[GUIDE_EN.md](GUIDE_EN.md)** — Full guide in English

### ツール

- [GitHub Copilot CLI](https://githubnext.com/projects/copilot-cli/)
- Python 3 + trimesh + manifold3d（3Dブーリアン演算）
- scikit-image + shapely（画像→ポリゴン変換）

---

<a id="english"></a>
## English

🧪 Experiment: Auto-generating 3D-printable bath bomb molds from images with GitHub Copilot CLI

### Overview

Automatically generates a cat-shaped (Octocat) 3D-printable bath bomb mold from the GitHub logo image.
Includes a waterproofed photo (9cm × 5.5cm) hidden inside as a surprise gift — revealed when the bath bomb dissolves!

### Generated Mold

Single-sided cat silhouette container mold:

- Walls follow the Octocat silhouette
- Open top (for filling), sealed bottom
- 5° draft angle (easy release)
- R3mm fillets (prevents cracking)
- 4mm walls and floor

### Usage

```bash
# Install dependencies
pip install pillow numpy scipy scikit-image shapely trimesh manifold3d

# Generate STL
python generate_mold.py
```

### Output

```
mold_cat_container.stl  — Cat-shaped container mold (single-sided)
```

### Recommended Print Settings

| Parameter | Value |
|-----------|-------|
| Printer | FDM |
| Filament | PLA |
| Layer height | 0.2mm |
| Infill | 20–30% |
| Support | None |
| Brim | Yes (prevents warping) |

Sand the cavity interior (#400 → #800 grit) after printing. Line with plastic wrap before use.

### Mold Specs

| Spec | Value |
|------|-------|
| Cavity depth | 25mm |
| Wall thickness | 4mm |
| Floor thickness | 4mm |
| Draft angle | 5° |
| Fillet radius | R3mm |
| Max photo size | 85×55mm |

### Crafting Guide

📖 **[GUIDE.md](GUIDE.md)** — Full guide in Japanese (日本語)

📖 **[GUIDE_EN.md](GUIDE_EN.md)** — Shopping list, step-by-step instructions & troubleshooting

### Tools

- [GitHub Copilot CLI](https://githubnext.com/projects/copilot-cli/)
- Python 3 + trimesh + manifold3d (3D boolean operations)
- scikit-image + shapely (image → polygon conversion)

## License

MIT
