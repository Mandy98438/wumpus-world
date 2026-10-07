# wumpus-world
# Wumpus World (Minecraft Edition)

A small Python version of the classic Wumpus World puzzle, redone with a Minecraft theme. You play as Steve, exploring a dark grid where you can't see what's ahead. Find the diamond, avoid the lava and the Creeper, and get back to the start.

Made with Python and tkinter. No images or extra libraries needed, all the textures are drawn in code.

## Requirements

- Python 3.7 or newer
- tkinter (comes with Python on Windows and macOS)

On some Linux systems you need to install it once:

```
sudo apt install python3-tk
```

## Install

```
pip install git+https://github.com/Mandy98438/wumpus-world.git
```

Or from a local clone:

```
pip install .
```

## How to run

```
wumpus-world
```

or

```
python -m wumpus_world
```

When the game opens, press a number key to choose the world size:

| Key | Size  |
|-----|-------|
| 1   | 4 x 4 |
| 2   | 5 x 5 |
| 3   | 6 x 6 |
| 4   | 8 x 8 |

## Controls

| Key                   | Action                              |
|-----------------------|-------------------------------------|
| W A S D / arrow keys  | Move                                |
| F, then a direction   | Shoot your arrow                    |
| G                     | Pick up the diamond                 |
| R                     | Restart with the same size          |
| M                     | Back to the size menu               |

## How to play

You start in the top-left corner. Every block you haven't visited is hidden as grey stone, so you only learn about the world by walking around.

Goal: find the diamond, pick it up with G, then walk back to the top-left corner to win.

What can go wrong:

- **Lava** kills you if you step in it.
- **The Creeper** kills you if you share a block with it.

The text box at the bottom tells you what you sense on your current block:

| Message                              | Meaning                                  |
|--------------------------------------|------------------------------------------|
| You hear a hiss nearby.              | The Creeper is on a block next to you.   |
| It feels hot here.                   | There is lava on a block next to you.    |
| Something shiny is here. Press G.    | You are standing on the diamond.         |

The senses only cover the four blocks touching you (up, down, left, right), not diagonals.

You have one arrow. Press F and then a direction and the arrow flies in a straight line to the edge of the board. If the Creeper is anywhere on that line, it dies. Use it carefully, because you only get one shot.

## Wumpus World vs. this version

| Classic Wumpus World | In this game |
|----------------------|--------------|
| Agent                | Steve        |
| Wumpus               | Creeper      |
| Pits                 | Lava         |
| Gold                 | Diamond      |
| Breeze               | "It feels hot here." |
| Stench               | "You hear a hiss nearby." |
| Glitter              | "Something shiny is here." |

## What's different from the normal game

- **The Creeper moves.** In the classic version the Wumpus stays in one spot. Here it wanders to a nearby block every few steps, so a spot that was safe earlier might not be safe now.
- **Day and night.** It switches every 12 steps. The board gets darker at night, and the Creeper moves twice as often.
- **Solvable maps only.** The game checks that a path from the start to the diamond exists without crossing lava, and regenerates the map if not.

## Notes

- The start area (the 2x2 corner) never has lava, the Creeper or the diamond.
- The number of lava blocks depends on the board size, roughly one for every eight blocks (minimum 2).
- The Creeper can still wander next to you or onto the block you're standing on, so don't stay in one place for too long.

## Files

```
wumpus_world/game.py       the whole game
wumpus_world/__main__.py   enables python -m wumpus_world
pyproject.toml             packaging config
README.md                  this file
```
