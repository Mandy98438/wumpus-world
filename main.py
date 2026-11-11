import random
import tkinter as tk


# ---------- constants ----------
# sizes shown on the menu, and how much each 16px texture is scaled
SIZES = {"1": 4, "2": 5, "3": 6, "4": 8}
ZOOM = {4: 8, 5: 6, 6: 5, 8: 4}
FONT = "Courier New"

DIRS = {"Up": (-1, 0), "Down": (1, 0), "Left": (0, -1), "Right": (0, 1),
        "w": (-1, 0), "s": (1, 0), "a": (0, -1), "d": (0, 1)}

# 8x8 sprites, "." is transparent
STEVE = ["hhhhhhhh",
         "hhhhhhhh",
         "hssssssh",
         "ssssssss",
         "swbssbws",
         "sssttsss",
         "ssmmmmss",
         "sssmmsss"]
CREEPER = ["gggggggg",
           "gggggggg",
           "gkkggkkg",
           "gkkggkkg",
           "gggkkggg",
           "ggkkkkgg",
           "ggkkkkgg",
           "ggkggkgg"]
DIAMOND = ["...oo...",
           "..occo..",
           ".ocwccxo",
           "ocwcccxo",
           "occcccxo",
           ".occcxo.",
           "..occo..",
           "...oo..."]
COL = {"h": "#3d2b1a", "s": "#b98865", "t": "#9c6f4f", "w": "#e6e6f0",
       "b": "#3a2f8f", "m": "#5a3822", "g": "#50a83c", "k": "#0d0d0d",
       "c": "#5decf5", "x": "#2aa5b0", "o": "#0f5f69"}

# tile colour palettes
GRASS = ["#6aa84f", "#5f9a47", "#77b85a", "#548c3e"]
STONE = ["#7f7f7f", "#8b8b8b", "#727272", "#969696"]
LAVA = ["#d9531a", "#ec6f1a", "#ff9420", "#f7b21f"]
DIRT = ["#8b5e3c", "#7a4f31", "#6b4429", "#94664a"]
PALETTES = {"grass": GRASS, "stone": STONE, "lava": LAVA, "dirt": DIRT}


# ---------- textures and sprites ----------
def shade(h, f):
    r, g, b = (int(h[i:i + 2], 16) for i in (1, 3, 5))
    return "#%02x%02x%02x" % tuple(max(0, min(255, int(v * f))) for v in (r, g, b))


class Textures:
    """Builds the block textures and sprites and keeps them cached."""

    def __init__(self, zoom):
        self.zoom = zoom
        self.cell = 16 * zoom
        self.cache = {}

    def tile(self, kind, variant, night=False):
        key = (kind, variant, night)
        if key in self.cache:
            return self.cache[key]
        rng = random.Random(list(PALETTES).index(kind) * 10 + variant)
        pix = [[rng.choice(PALETTES[kind]) for _ in range(16)] for _ in range(16)]

        if kind == "grass":
            for _ in range(16):
                pix[rng.randrange(16)][rng.randrange(16)] = "#458233"
            for _ in range(10):
                x, y = rng.randrange(16), rng.randrange(1, 16)
                pix[y][x], pix[y - 1][x] = "#82c761", "#8fd46b"
        elif kind == "stone":
            for _ in range(4):
                x, y = rng.randrange(16), rng.randrange(16)
                for _ in range(5):
                    pix[y][x] = "#4d4d4d"
                    x = min(15, max(0, x + rng.choice((-1, 0, 1))))
                    y = min(15, max(0, y + rng.choice((0, 1))))
        elif kind == "lava":
            for _ in range(7):
                x, y = rng.randrange(1, 15), rng.randrange(1, 15)
                for dx, dy in ((0, 0), (1, 0), (0, 1)):
                    pix[y + dy][x + dx] = "#ffe066"
        else:
            for _ in range(14):
                pix[rng.randrange(16)][rng.randrange(16)] = "#4e3320"

        for y in range(16):
            for x in range(16):
                pix[y][x] = shade(pix[y][x], rng.uniform(0.94, 1.05))
        if kind != "dirt":  # light top/left edge, dark bottom/right edge
            for i in range(16):
                for x, y, f in ((i, 0, 1.1), (0, i, 1.1), (i, 15, 0.8), (15, i, 0.8)):
                    pix[y][x] = shade(pix[y][x], f)
        if night:
            pix = [[shade(c, 0.6) for c in row] for row in pix]

        img = tk.PhotoImage(width=16, height=16)
        img.put(" ".join("{" + " ".join(r) + "}" for r in pix), to=(0, 0))
        self.cache[key] = img.zoom(self.zoom)
        return self.cache[key]

    def sprite(self, art, seed):
        """Returns (image, pixel size)."""
        z = (self.cell * 3 // 4) // 8
        rng = random.Random(seed)
        img = tk.PhotoImage(width=8, height=8)
        for y, row in enumerate(art):
            for x, ch in enumerate(row):
                if ch != ".":
                    img.put(shade(COL[ch], rng.uniform(0.93, 1.06)), to=(x, y))
        return img.zoom(z), z * 8


# ---------- game rules (no graphics) ----------
class World:
    """Game rules and state. No graphics in here, so it can be tested on its own."""

    def __init__(self, n, seed=None):
        self.n = n
        self.rng = random.Random(seed)
        self.player = (0, 0)
        self.has_diamond = False
        self.arrows = 1
        self.moves = 0
        self.night = False
        self.aiming = False
        self.over = False
        self.won = False
        self.visited = {(0, 0)}
        self.msg = "Steve spawned in the top-left corner."
        self._generate()

    def _generate(self):
        n = self.n
        while True:
            cells = [(r, c) for r in range(n) for c in range(n) if max(r, c) > 1]
            self.rng.shuffle(cells)
            self.creeper = cells.pop()
            self.diamond = cells.pop()
            self.lava = set(cells[:max(2, n * n // 8)])
            if self._reachable():
                break

    def neighbors(self, pos):
        r, c = pos
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < self.n and 0 <= nc < self.n:
                yield (nr, nc)

    def _reachable(self):
        seen, todo = {(0, 0)}, [(0, 0)]
        while todo:
            cur = todo.pop()
            if cur == self.diamond:
                return True
            for nb in self.neighbors(cur):
                if nb not in seen and nb not in self.lava:
                    seen.add(nb)
                    todo.append(nb)
        return False

    def senses(self):
        if self.over:
            return ""
        near = list(self.neighbors(self.player))
        out = []
        if self.creeper in near:
            out.append("You hear a hiss nearby.")
        if any(p in self.lava for p in near):
            out.append("It feels hot here.")
        if self.player == self.diamond and not self.has_diamond:
            out.append("Something shiny is here. Press G.")
        return " ".join(out) or "Nothing unusual."

    # ----- actions -----
    def move(self, d):
        r, c = self.player[0] + d[0], self.player[1] + d[1]
        if not (0 <= r < self.n and 0 <= c < self.n):
            self.msg = "Bedrock. Can't go that way."
            return
        self.player = (r, c)
        self.msg = "Moved."
        self._after_action()

    def draw_bow(self):
        if self.arrows:
            self.aiming = True
            self.msg = "Bow drawn. Pick a direction."
        else:
            self.msg = "No arrows left."

    def cancel_aim(self):
        self.aiming = False
        self.msg = "Put the bow away."

    def shoot(self, d):
        self.aiming = False
        self.arrows -= 1
        r, c = self.player
        hit = False
        while True:
            r, c = r + d[0], c + d[1]
            if not (0 <= r < self.n and 0 <= c < self.n):
                break
            if (r, c) == self.creeper:
                hit = True
                break
        if hit:
            self.creeper = None
            self.msg = "The arrow hit something. Creeper is gone."
        else:
            self.msg = "The arrow hit the wall."
        self._after_action()

    def grab(self):
        if self.player == self.diamond and not self.has_diamond:
            self.has_diamond = True
            self.msg = "Picked up the diamond. Get back to the start."
        else:
            self.msg = "Nothing here to pick up."

    # ----- turn handling -----
    def _check_death(self):
        if self.player in self.lava:
            self._end("Steve tried to swim in lava.")
        elif self.creeper == self.player:
            self._end("Steve was blown up by Creeper.")

    def _end(self, text):
        self.over = True
        self.msg = text + " (R to retry, M for menu)"

    def _tick(self):
        self.moves += 1
        if self.moves % 12 == 0:
            self.night = not self.night
        if self.creeper is not None and self.moves % (3 if self.night else 6) == 0:
            options = [p for p in self.neighbors(self.creeper) if p not in self.lava]
            if options:
                self.creeper = self.rng.choice(options)
                self.msg += " Footsteps somewhere."

    def _after_action(self):
        self._check_death()
        if not self.over:
            self._tick()
            self._check_death()
        if not self.over:
            self.visited.add(self.player)
            if self.player == (0, 0) and self.has_diamond:
                self.over = self.won = True
                self.msg = "Steve got out with the diamond. You win. (R to play again)"


# ---------- window, menu, drawing and input ----------
class App:
    def __init__(self, root):
        self.root = root
        self.canvas = None
        self.world = None
        self.state = "menu"
        root.title("Wumpus World")
        root.configure(bg="#000")
        root.resizable(False, False)
        root.bind("<Key>", self.on_key)
        self.show_menu()

    def new_canvas(self, w, h):
        if self.canvas:
            self.canvas.destroy()
        self.canvas = tk.Canvas(self.root, width=w, height=h, bg="#000",
                                highlightthickness=0)
        self.canvas.pack()

    def text(self, x, y, s, color="#ffffff", size=14, anchor="nw", width=0):
        for off, col in ((2, "#3f3f3f"), (0, color)):
            self.canvas.create_text(x + off, y + off, text=s, fill=col,
                                    font=(FONT, size, "bold"), anchor=anchor,
                                    width=width, justify="center" if anchor == "n" else "left")

    # ----- menu -----
    def show_menu(self):
        self.state = "menu"
        tex = Textures(4)
        self.new_canvas(512, 512)
        for r in range(8):
            for c in range(8):
                self.canvas.create_image(c * 64, r * 64, anchor="nw",
                                         image=tex.tile("dirt", (r + c) % 4, True))
        self.menu_tex = tex
        self.text(256, 60, "WUMPUS WORLD", "#ffff55", 30, "n")
        self.text(256, 110, "Press 1-4 to pick a world size", "#dddddd", 12, "n")
        for i, (key, n) in enumerate(SIZES.items()):
            y = 170 + i * 62
            self.canvas.create_rectangle(106, y, 406, y + 48, fill="#7a7a7a",
                                         outline="#000", width=2)
            self.canvas.create_line(108, y + 2, 404, y + 2, fill="#b5b5b5", width=2)
            self.canvas.create_line(108, y + 2, 108, y + 46, fill="#b5b5b5", width=2)
            self.canvas.create_line(108, y + 46, 404, y + 46, fill="#3b3b3b", width=2)
            self.canvas.create_line(404, y + 2, 404, y + 46, fill="#3b3b3b", width=2)
            self.text(256, y + 24, f"{key}   {n} x {n}", "#ffffff", 16, "center")
        self.text(256, 460, "WASD/arrows move   F + direction shoot\n"
                            "G grab   R restart   M menu", "#aaaaaa", 10, "n")

    # ----- game -----
    def start(self, n):
        self.n = n
        self.world = World(n)
        self.tex = Textures(ZOOM[n])
        self.sprites = {"steve": self.tex.sprite(STEVE, 1),
                        "creeper": self.tex.sprite(CREEPER, 2),
                        "diamond": self.tex.sprite(DIAMOND, 3)}
        self.state = "play"
        self.new_canvas(n * self.tex.cell, n * self.tex.cell + 96)
        self.draw()

    def on_key(self, e):
        k = e.keysym.lower() if len(e.keysym) == 1 else e.keysym
        if k.startswith("KP_"):
            k = k[3:]
        if self.state == "menu":
            if k in SIZES:
                self.start(SIZES[k])
            return
        if k == "m":
            return self.show_menu()
        if k == "r":
            return self.start(self.n)
        w = self.world
        if w.over:
            return
        if w.aiming:
            if k in DIRS:
                w.shoot(DIRS[k])
            else:
                w.cancel_aim()
        elif k in DIRS:
            w.move(DIRS[k])
        elif k == "f":
            w.draw_bow()
        elif k == "g":
            w.grab()
        self.draw()

    def put(self, name, r, c):
        img, size = self.sprites[name]
        cell = self.tex.cell
        x = c * cell + (cell - size) // 2
        y = r * cell + (cell - size) // 2
        self.canvas.create_image(x, y, image=img, anchor="nw")
        if name == "steve":
            self.canvas.create_rectangle(x, y, x + size, y + size,
                                         outline="#000", width=2)

    def draw(self):
        w, cell = self.world, self.tex.cell
        size = w.n * cell
        self.canvas.delete("all")
        for r in range(w.n):
            for c in range(w.n):
                pos = (r, c)
                seen = pos in w.visited or w.over
                kind = ("lava" if pos in w.lava else "grass") if seen else "stone"
                img = self.tex.tile(kind, (r * 7 + c * 13) % 4, w.night)
                self.canvas.create_image(c * cell, r * cell, anchor="nw", image=img)
                if pos == w.diamond and not w.has_diamond and \
                        (w.over or w.player == pos):
                    self.put("diamond", r, c)
                if w.over and pos == w.creeper:
                    self.put("creeper", r, c)
        self.put("steve", *w.player)
        self.canvas.create_rectangle(8, size + 8, size - 8, size + 88,
                                     fill="#100010", outline="#3a0f7a", width=3)
        self.text(20, size + 16, f"Step {w.moves}: {w.msg}", "#ffffff", 12,
                  "nw", size - 40)
        self.text(20, size + 58, w.senses(), "#55ffff", 12, "nw", size - 40)


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
