CREATE TABLE IF NOT EXISTS cards (
    id        TEXT PRIMARY KEY,   -- TCGdex id, e.g. 'swsh10-113'
    name      TEXT NOT NULL,      -- e.g. 'Origin Forme Dialga V'
    set_id    TEXT NOT NULL,      -- e.g. 'swsh10'
    set_name  TEXT,               -- e.g. 'Astral Radiance'
    local_id  TEXT NOT NULL       -- card number within the set, e.g. '113' or 'H9'
);

CREATE TABLE IF NOT EXISTS prices (
    card_id     TEXT NOT NULL REFERENCES cards(id),
    source      TEXT NOT NULL,     -- where the price came from, e.g. 'tcgdex-tcgplayer'
    variant     TEXT NOT NULL,     -- 'normal', 'reverse' or 'holo'
    condition   TEXT NOT NULL,     -- 'nearmint', 'good', 'played', 'used' or 'poor'
    day         DATE NOT NULL,
    avg_cents   INTEGER NOT NULL,
    min_cents   INTEGER,
    max_cents   INTEGER,
    sale_count  INTEGER,
    PRIMARY KEY (card_id, source, variant, condition, day)
);