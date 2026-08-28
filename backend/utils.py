import re

translate_zenkaku_digits = str.maketrans("０１２３４５６７８９", "0123456789")

"""
サンプル
'Amazon.co.jp: この素晴らしい世界に祝福を！２ を観る | Prime Video',
'Amazon.co.jp: その着せ替え人形は恋をするを観る | Prime Video',
'Re:ゼロから始める異世界生活　4th season | アニメ動画見放題 | dアニメストア',
'Re:ゼロから始める異世界生活　2nd season | アニメ動画見放題 | dアニメストア',
'才女のお世話 高嶺の花だらけな名門校で、学院一のお嬢様(生活能力皆無)を陰ながらお世話することになりました 第08話 | dアニメストア',
'メダリスト | アニメ動画見放題 | dアニメストア',
"""

# 上記のパターンから、生のアニメタイトルを取得。
# \s* -> 1文字以上の空白
# \| -> |
# (.+?) -> 最小一致。
# 正規表現チェック:https://www.megasoft.co.jp/mifes/seiki/meta.html


def normalize_title(title: str) -> str:
    if "Amazon" in title:
        normalized_title = re.search(r"Amazon\.co\.jp:\s*(.+?)\s*\|\s*Prime Video",title).group(1)
        normalized_title = re.sub(r"\s*を観る", "", normalized_title)
    elif "dアニメストア" in title:
        normalized_title = re.search(r"(.+?)\s*\|\s*(?:アニメ動画見放題\s*\|\s*)?dアニメストア",title).group(1)
        normalized_title = re.sub(r"\s*第\d+話$", "", normalized_title) #第何話を除外
        normalized_title = re.sub(r"\s*STAGE\d+$", "", normalized_title, flags=re.IGNORECASE) 
    else:
        normalized_title = title

    return normalized_title.translate(translate_zenkaku_digits)