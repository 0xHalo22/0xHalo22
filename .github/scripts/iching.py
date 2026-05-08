"""
i ching hexagram data + rendering.

64 hexagrams in the king wen sequence. each entry has:
  number, chinese name, pinyin, english name, lines (top to bottom),
  and a single-line interpretation.

lines are 6 booleans: True = solid (yang), False = broken (yin).
the convention here is index 0 = bottom line, index 5 = top line —
which is the traditional way hexagrams are read (built from the
bottom up). when rendering we display top-to-bottom (top of the list
first), so we reverse for display.

interpretations are paraphrased compressions of the wilhelm/baynes
classical readings. they're meant to be evocative rather than canonical.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Hexagram:
    number: int
    chinese: str
    pinyin: str
    english: str
    # 6 booleans, bottom-up (index 0 = bottom line)
    lines: tuple[bool, bool, bool, bool, bool, bool]
    reading: str


# fmt: off
HEXAGRAMS: list[Hexagram] = [
    Hexagram( 1, "乾", "Qián",   "The Creative",          (True,  True,  True,  True,  True,  True ), "the dragon flies; persistence brings reward"),
    Hexagram( 2, "坤", "Kūn",    "The Receptive",         (False, False, False, False, False, False), "yield, follow, accept what arrives"),
    Hexagram( 3, "屯", "Zhūn",   "Difficulty at the Beginning", (True, False, False, False, True, False), "do not move yet — gather yourself first"),
    Hexagram( 4, "蒙", "Méng",   "Youthful Folly",        (False, True,  False, False, False, True ), "the question must be asked sincerely or not at all"),
    Hexagram( 5, "需", "Xū",     "Waiting",               (True,  True,  True,  False, True,  False), "patience now is its own action"),
    Hexagram( 6, "訟", "Sòng",   "Conflict",              (False, True,  False, True,  True,  True ), "step back; meet halfway before things harden"),
    Hexagram( 7, "師", "Shī",    "The Army",              (False, True,  False, False, False, False), "lead from discipline, not from force"),
    Hexagram( 8, "比", "Bǐ",     "Holding Together",      (False, False, False, False, True,  False), "stand close to others while it still costs nothing"),
    Hexagram( 9, "小畜", "Xiǎo Chù", "Small Restraint",   (True,  True,  True,  False, True,  True ), "small steps; gentle pressure; do not force the hand"),
    Hexagram(10, "履", "Lǚ",     "Treading",              (True,  True,  False, True,  True,  True ), "walk carefully past the tiger; do not provoke it"),
    Hexagram(11, "泰", "Tài",    "Peace",                 (True,  True,  True,  False, False, False), "heaven and earth meet; share what you have"),
    Hexagram(12, "否", "Pǐ",     "Standstill",            (False, False, False, True,  True,  True ), "the channel is blocked; wait without resentment"),
    Hexagram(13, "同人", "Tóng Rén", "Fellowship",        (True,  False, True,  True,  True,  True ), "find your people; act in the open"),
    Hexagram(14, "大有", "Dà Yǒu", "Great Possession",    (True,  True,  True,  True,  False, True ), "abundance comes; carry it with humility"),
    Hexagram(15, "謙", "Qiān",   "Modesty",               (False, False, True,  False, False, False), "the high makes itself low; this is durable"),
    Hexagram(16, "豫", "Yù",     "Enthusiasm",            (False, False, False, True,  False, False), "the moment is buoyant; ride it but do not lose your seat"),
    Hexagram(17, "隨", "Suí",    "Following",             (True,  False, False, True,  True,  False), "follow the current — but choose which current"),
    Hexagram(18, "蠱", "Gǔ",     "Work on the Decayed",   (False, True,  True,  False, False, True ), "what was neglected must be repaired now"),
    Hexagram(19, "臨", "Lín",    "Approach",              (True,  True,  False, False, False, False), "spring approaches; meet it halfway"),
    Hexagram(20, "觀", "Guān",   "Contemplation",         (False, False, False, False, True,  True ), "watch first, act later"),
    Hexagram(21, "噬嗑", "Shì Kè", "Biting Through",      (True,  False, False, True,  False, True ), "an obstacle remains; chew through it without rage"),
    Hexagram(22, "賁", "Bì",     "Grace",                 (True,  False, True,  False, False, True ), "form serves substance; do not mistake one for the other"),
    Hexagram(23, "剝", "Bō",     "Stripping Away",        (False, False, False, False, False, True ), "the old falls; let it"),
    Hexagram(24, "復", "Fù",     "Return",                (True,  False, False, False, False, False), "what was lost is coming back; do not chase it"),
    Hexagram(25, "無妄", "Wú Wàng", "Innocence",         (True,  False, False, True,  True,  True ), "act without ulterior motive; the path will hold"),
    Hexagram(26, "大畜", "Dà Chù", "Great Restraint",     (True,  True,  True,  False, False, True ), "hold the energy; release it only when it serves"),
    Hexagram(27, "頤", "Yí",     "Nourishment",           (True,  False, False, False, False, True ), "watch what you take in — and what you give out"),
    Hexagram(28, "大過", "Dà Guò", "Preponderance of the Great", (False, True,  True,  True,  True,  False), "the beam bends; act before it breaks"),
    Hexagram(29, "坎", "Kǎn",    "The Abyss",             (False, True,  False, False, True,  False), "in the danger, hold to what is true; do not panic"),
    Hexagram(30, "離", "Lí",     "Clinging",              (True,  False, True,  True,  False, True ), "find what holds you up; trust it visibly"),
    Hexagram(31, "咸", "Xián",   "Influence",             (False, False, True,  True,  True,  False), "feeling moves first; let it lead"),
    Hexagram(32, "恆", "Héng",   "Duration",              (False, True,  True,  True,  False, False), "endure without rigidity"),
    Hexagram(33, "遯", "Dùn",    "Retreat",               (False, False, True,  True,  True,  True ), "step back early; this is not weakness"),
    Hexagram(34, "大壯", "Dà Zhuàng", "Great Power",      (True,  True,  True,  True,  False, False), "strength has arrived; do not abuse it"),
    Hexagram(35, "晉", "Jìn",    "Progress",              (False, False, False, True,  False, True ), "the sun rises; act in plain view"),
    Hexagram(36, "明夷", "Míng Yí", "Darkening of the Light", (True, False, True,  False, False, False), "hide your light a while; the darkness is brief"),
    Hexagram(37, "家人", "Jiā Rén", "The Family",         (True,  False, True,  False, True,  True ), "tend to your inner circle; the outer takes care of itself"),
    Hexagram(38, "睽", "Kuí",    "Opposition",            (True,  True,  False, True,  False, True ), "differences are not enmity — find the common point"),
    Hexagram(39, "蹇", "Jiǎn",   "Obstruction",           (False, False, True,  False, True,  False), "the path is hard; turn inward, ask why"),
    Hexagram(40, "解", "Xiè",    "Deliverance",           (False, True,  False, True,  False, False), "the storm has passed; resume gently"),
    Hexagram(41, "損", "Sǔn",    "Decrease",              (True,  True,  False, False, False, True ), "give something up; what remains will be enough"),
    Hexagram(42, "益", "Yì",     "Increase",              (True,  False, False, False, True,  True ), "act now; the wind is at your back"),
    Hexagram(43, "夬", "Guài",   "Breakthrough",          (True,  True,  True,  True,  True,  False), "say the thing; resolve the standoff openly"),
    Hexagram(44, "姤", "Gòu",    "Coming to Meet",        (False, True,  True,  True,  True,  True ), "something small enters; watch what it grows into"),
    Hexagram(45, "萃", "Cuì",    "Gathering Together",    (False, False, False, True,  True,  False), "people gather around purpose; show up"),
    Hexagram(46, "升", "Shēng",  "Pushing Upward",        (False, True,  True,  False, False, False), "ascend without strain; the way is open"),
    Hexagram(47, "困", "Kùn",    "Oppression",            (False, True,  False, True,  True,  False), "exhaustion is real; do less, not more"),
    Hexagram(48, "井", "Jǐng",   "The Well",              (False, True,  True,  False, True,  False), "the source is steady; tend the means of access"),
    Hexagram(49, "革", "Gé",     "Revolution",            (True,  False, True,  True,  True,  False), "what was must change; the timing now is right"),
    Hexagram(50, "鼎", "Dǐng",   "The Cauldron",          (False, True,  True,  True,  False, True ), "transformation cooks slowly; do not rush the heat"),
    Hexagram(51, "震", "Zhèn",   "The Arousing",          (True,  False, False, True,  False, False), "the shock arrives; meet it without flinching"),
    Hexagram(52, "艮", "Gèn",    "Keeping Still",         (False, False, True,  False, False, True ), "stop where you are; this is the right place"),
    Hexagram(53, "漸", "Jiàn",   "Gradual Progress",      (False, False, True,  False, True,  True ), "step by step, like a tree growing on the mountain"),
    Hexagram(54, "歸妹", "Guī Mèi", "The Marrying Maiden", (True, True,  False, True,  False, False), "you are not the center of this; act with care"),
    Hexagram(55, "豐", "Fēng",   "Abundance",             (True,  False, True,  True,  False, False), "the noon sun; enjoy this — it will move"),
    Hexagram(56, "旅", "Lǚ",     "The Wanderer",          (False, False, True,  True,  False, True ), "you are a guest here; travel light, leave clean"),
    Hexagram(57, "巽", "Xùn",    "The Gentle",            (False, True,  True,  False, True,  True ), "small consistent influence beats sudden force"),
    Hexagram(58, "兌", "Duì",    "The Joyous",            (True,  True,  False, True,  True,  False), "share what brings you joy; it multiplies"),
    Hexagram(59, "渙", "Huàn",   "Dispersion",            (False, True,  False, False, True,  True ), "what was rigid dissolves; this is mercy"),
    Hexagram(60, "節", "Jié",    "Limitation",            (True,  True,  False, False, True,  False), "freedom requires a frame; choose yours"),
    Hexagram(61, "中孚", "Zhōng Fú", "Inner Truth",       (True,  True,  False, False, True,  True ), "what you mean is felt; speak from the center"),
    Hexagram(62, "小過", "Xiǎo Guò", "Small Excess",      (False, False, True,  True,  False, False), "be a little more careful than usual today"),
    Hexagram(63, "既濟", "Jì Jì", "After Completion",     (True,  False, True,  False, True,  False), "the work is done; the next thing has not begun"),
    Hexagram(64, "未濟", "Wèi Jì", "Before Completion",   (False, True,  False, True,  False, True ), "you are almost there; do not falter at the last step"),
]
# fmt: on

assert len(HEXAGRAMS) == 64


def hexagram_for(d: date) -> Hexagram:
    """deterministic daily hexagram — same hexagram for everyone who looks today.

    we use day-of-year + year as the seed so the rotation cycles through all 64
    over the course of ~2 months and shifts year over year. the precise mapping
    is not divinatorily meaningful — we're not casting yarrow stalks here, just
    rotating through the deck."""
    # ordinal day count gives us a monotonic integer; mod 64 picks the hexagram
    return HEXAGRAMS[d.toordinal() % 64]


def hexagram_char(h: Hexagram) -> str:
    """unicode codepoint for a king-wen-numbered hexagram.

    the unicode block 'yijing hexagram symbols' (U+4DC0–U+4DFF) follows the
    king wen sequence, so hexagram n is at U+4DC0 + (n-1)."""
    return chr(0x4DC0 + h.number - 1)


# bottom-up tuple → (unicode glyph, english name) for the 8 trigrams.
# unicode block 'yijing trigram symbols' is at U+2630–U+2637 in the order:
# heaven, lake, fire, thunder, wind, water, mountain, earth.
TRIGRAMS: dict[tuple[bool, bool, bool], tuple[str, str]] = {
    (True,  True,  True ): ("☰", "heaven"),
    (True,  True,  False): ("☱", "lake"),
    (True,  False, True ): ("☲", "fire"),
    (True,  False, False): ("☳", "thunder"),
    (False, True,  True ): ("☴", "wind"),
    (False, True,  False): ("☵", "water"),
    (False, False, True ): ("☶", "mountain"),
    (False, False, False): ("☷", "earth"),
}


def trigrams_of(h: Hexagram) -> tuple[tuple[str, str], tuple[str, str]]:
    """returns (upper, lower) — each as a (glyph, name) tuple.

    convention: lines are stored bottom-up, so lines[0:3] is the lower
    trigram and lines[3:6] is the upper trigram. classical readings name
    a hexagram as 'upper over lower' (e.g. hex 33 = heaven over mountain)."""
    lower = TRIGRAMS[h.lines[0:3]]
    upper = TRIGRAMS[h.lines[3:6]]
    return upper, lower


def render(h: Hexagram) -> str:
    """compact two-line render using the unicode hexagram character.

    the unicode glyph encodes all 6 lines of the hexagram visually as a single
    monospace character, so we don't need to draw the trigrams as ASCII art.
    one line for title, one for the reading."""
    return (
        f"   {hexagram_char(h)}  {h.number} {h.pinyin} — {h.english}\n"
        f'   "{h.reading}"'
    )


if __name__ == "__main__":
    # sanity check: render today's hexagram
    from datetime import date as _d
    print(render(hexagram_for(_d.today())))
