# 🎉 Trial 02 — 2026-05-06（成功）

**[日本語](#日本語) | [English](#english)**

---

<a id="日本語"></a>
## 日本語

第2回試作の記録。**4色のOctocatバスボムが綺麗に外れて成功** 🐱✨

[第1回 (失敗)](../2026-05-04-trial-01/) で得た学びを反映した改良版クラムシェル型を使用。

---

### 背景ストーリー 🎁

GitHub を退職する同僚（**元 Microsoft 社員**）への餞別ギフトとして製作。
Octocat の形をした **Microsoft ロゴカラー（赤・緑・青・黄）** の 4 色バスボムを作り、
マリオの「はてなブロック」風の 3D プリント箱に詰めて贈ることに。

> 💡 万が一手作りバスボムが失敗しても恥をかかないよう、
> 保険として Lush の「ヨッシーの卵」バスボムと泡ボムも 1 個ずつ同梱。
> 結果として手作りも成功したので、両方贈ることになりました。

---

### 使用した型

| 項目 | 値 |
|------|----|
| STL ファイル | [`mold_cat_clamshell_A.stl`](../../mold_cat_clamshell_A.stl) / [`mold_cat_clamshell_B.stl`](../../mold_cat_clamshell_B.stl) |
| 型方式 | クラムシェル 2 分割（左右ハーフ） |
| キャビティ深さ | 10mm × 2（合計約 20mm） |
| 抜き勾配 | 8° |
| 壁厚 / 床厚 | 4mm / 4mm |
| フィレット | R3mm |
| フランジ幅 / 厚さ | 5mm / 4mm |
| 位置決めピン | φ4mm × 4 本（クリアランス 0.8mm） |
| プリント材料 | PLA（黒） |

---

### 制作手順（写真付き）

#### フェーズ A: 4 色の粉末準備

重曹・クエン酸・コーンスターチ・コーンスターチ・塩を計量し、4 つのボウルに分けて
それぞれ食用色素で **赤・緑・青・黄** に着色。無水エタノールでしっとり感を調整。

| | |
|---|---|
| ![色付き粉俯瞰](01-color-mixing-overhead.jpg) | ![色付き粉別アングル](02-color-mixing-alt.jpg) |

ラップでボウルをカバーして粉の飛散と湿気を防止。

#### フェーズ B: 型詰め・乾燥

各色をクラムシェル型のハーフに山盛りに詰めて、もう片方のハーフをかぶせて
ぐっと押し付けて圧縮。ゴムバンドで圧着して半日〜1 日乾燥。

![クランプされたクラムシェル型](03-mold-clamped.jpg)

#### フェーズ C: 離型

乾燥後、ゴムバンドを外して型をパカッと開く。

![型を開けた状態](04-demolding.jpg)

軽く叩くだけでバスボムがするっと外れる！クラムシェル化と勾配 8° の効果絶大。

![成功した緑バスボム](05-success-green.jpg)

#### フェーズ D: 保存・梱包

完成したバスボムは Ziploc に入れて湿気から保護。

![Ziploc保存](06-ziploc-storage.jpg)

緩衝材入りの白箱に 1 個ずつ、または 4 色セットで梱包。

| 1 個梱包 | 4 色セット |
|---|---|
| ![単品梱包](07-single-packed.jpg) | ![4色セット](08-set-of-four.jpg) |

#### フェーズ E: ギフトラッピング 🎁

3D プリント製の **マリオはてなブロック箱** に詰めて、ふたに Octocat ステッカーを貼って完成。

| ブロック箱（前） | フタを閉じて完成 |
|---|---|
| ![はてなブロック箱・前面](09-question-block-front.jpg) | ![フタを閉じた完成形](10-question-block-closed.jpg) |

---

### Trial 01 → Trial 02 で達成された改善

[trial-01](../2026-05-04-trial-01/) の「次回への改善方針」をすべてクリア:

| 改善項目 | trial-01 | trial-02 | 結果 |
|---|---|---|---|
| 型構造 | 片面コンテナ（床密閉） | クラムシェル 2 分割 | ✅ パカッと開けるだけで離型 |
| 抜き勾配 | 5° | 8° | ✅ 粉末でも詰まらず外れる |
| 厚み | 25mm（1 個分） | 10mm × 2 = 20mm | ✅ 手の平サイズで使いやすい |
| 位置決め | なし | フランジ + φ4mm ピン × 4 | ✅ ハーフ同士がぴったり合う |
| ピン穴クリアランス | — | 0.8mm（緩めに） | ✅ FDM 収縮を吸収しスッと嵌まる |
| 取り出し方 | 「外れない…」 | パカッ → ポロッ | ✅ 完全成功 |

---

### 学び・気づき

- **クラムシェル化は正解**: 上下から分割するだけで離型問題は劇的に改善
- **8° の抜き勾配** は粉末材料に対して必要十分。これより浅いと厳しい
- **ピン穴は緩めに**（クリアランス 0.8mm 以上）— FDM プリントの収縮で 0.3mm では入らないことがある
- **複数色の粉を別々に作る** ことで 1 セットで色違いの作品が作れる（Microsoft ロゴカラーや好きなテーマカラーで！）
- **乾燥は焦らない**：圧縮直後すぐ開けると崩れるリスク。ゴムバンドで半日以上クランプ推奨
- **保険は大事**: 自作の出来に自信が無ければ市販品も同梱するのは賢いリスクヘッジ

---

<a id="english"></a>
## English

Second trial — **four-color Octocat bath bombs released cleanly from the mold!** 🐱✨

Used the redesigned clamshell mold incorporating all the lessons from
[Trial 01 (failure)](../2026-05-04-trial-01/).

---

### Backstory 🎁

These bath bombs were made as a farewell gift for **a colleague leaving GitHub
(formerly at Microsoft)**. To honor both employers, four Octocats were cast in the
**Microsoft logo colors (red, green, blue, yellow)** and packed into a 3D-printed
**Mario question block** gift box.

> 💡 As insurance against a possible failure of the homemade bath bombs,
> a Lush "Yoshi's Egg" bath bomb and a foam bath bomb were included as backups.
> The homemade ones turned out great — so both went into the gift.

---

### Mold Used

| Spec | Value |
|------|-------|
| STL files | [`mold_cat_clamshell_A.stl`](../../mold_cat_clamshell_A.stl) / [`mold_cat_clamshell_B.stl`](../../mold_cat_clamshell_B.stl) |
| Structure | Two-piece clamshell (halves A + B) |
| Cavity depth | 10mm × 2 (≈20mm total) |
| Draft angle | 8° |
| Wall / floor | 4mm / 4mm |
| Fillet | R3mm |
| Flange width / thickness | 5mm / 4mm |
| Alignment dowels | 4 × φ4mm (0.8mm clearance) |
| Filament | PLA (black) |

---

### Process (with photos)

#### Phase A — Mix four colors of powder

Baking soda, citric acid, cornstarch and salt were measured into four bowls
and each was tinted with food coloring (**red, green, blue, yellow**).
Anhydrous ethanol was misted in to give the powder a "wet sand" texture.

| | |
|---|---|
| ![Powders, overhead](01-color-mixing-overhead.jpg) | ![Powders, alt angle](02-color-mixing-alt.jpg) |

Plastic wrap kept the bowls dust-free and dry until packing.

#### Phase B — Pack the clamshell mold

Heap each color into one mold half, press the other half down firmly,
clamp with rubber bands, and leave to cure for half a day to a full day.

![Clamped clamshell](03-mold-clamped.jpg)

#### Phase C — Release

After curing, remove the rubber bands and pop the two halves apart.

![Mold opened, bath bomb still in one half](04-demolding.jpg)

A gentle tap is all it takes — the bath bomb falls out cleanly. The clamshell
geometry and the 8° draft made the difference vs. Trial 01.

![Successful green Octocat](05-success-green.jpg)

#### Phase D — Store & pack

Each finished bath bomb went into a Ziploc bag to protect against humidity.

![Ziploc storage](06-ziploc-storage.jpg)

Then either packed individually or as a 4-color set in a white box with peanut packing.

| Single | Set of four |
|---|---|
| ![Single packed](07-single-packed.jpg) | ![Set of four](08-set-of-four.jpg) |

#### Phase E — Gift wrapping 🎁

The set was placed inside a 3D-printed **Mario question-block box** with an
Octocat sticker on the lid.

| Block (front view) | Final lid closed |
|---|---|
| ![Question block, front](09-question-block-front.jpg) | ![Question block, closed](10-question-block-closed.jpg) |

---

### Improvements vs. Trial 01

Every "next-trial" item from [Trial 01](../2026-05-04-trial-01/) was achieved:

| Improvement | Trial 01 | Trial 02 | Result |
|---|---|---|---|
| Mold structure | Single-sided container (sealed floor) | Two-piece clamshell | ✅ Just open it |
| Draft angle | 5° | 8° | ✅ Powder releases cleanly |
| Thickness | 25mm (whole bomb) | 10mm × 2 = 20mm | ✅ Pleasant hand-size |
| Alignment | None | Flange + 4× φ4mm pins | ✅ Halves self-align |
| Pin clearance | — | 0.8mm (loose fit) | ✅ Accommodates FDM shrinkage |
| Removal | "Won't come out…" | Pop → Out | ✅ Total success |

---

### Lessons Learned

- **Clamshell geometry is the answer.** Splitting top/bottom solves the release problem at the source.
- **8° draft** is the sweet spot for powdery material. Anything shallower struggles.
- **Use generous pin clearance (≥0.8mm).** Tight 0.3mm clearances often won't seat after FDM shrinkage.
- **Mix multiple colors separately** to make a multi-color set in one printing of the mold — perfect for themed gifts.
- **Don't rush the cure.** Opening too soon risks crumbling. Half a day under rubber-band clamp is the minimum.
- **Insurance pays.** Including a commercial bath bomb as backup is a smart hedge for first-time gifts.
