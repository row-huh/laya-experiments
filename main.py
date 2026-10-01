"""Snake with a laya autopilot.
Arrow keys (or W/S/D) = play yourself. Press A = toggle laya autopilot. R = restart.
Run: python snake_laya.py
"""
import random
import tkinter as tk
from typesafe_sdk import Choice, Noul, Score, TypeSafeClient
from laya import Router
import os

os.environ["TYPESAFE_BASE_URL"] = "http://localhost:11434"
os.environ["TYPESAFE_API_KEY"] = "ollama"
os.environ["TYPESAFE_DEFAULT_MODEL"] = "nimble"



CELL, GRID, TICK = 20, 20, 110
DIRS = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}
KEYS = {"Up": "up", "w": "up", "Down": "down", "s": "down",
        "Left": "left", "Right": "right", "d": "right"}

router = Router()

QUESTIONS = {
    "move": {
        "type": "choice",
        "instructions": "Which direction should the snake move next to reach the food without dying?",
        "criteria": {
            "up": "food is above and up is safe",
            "down": "food is below and down is safe",
            "left": "food is to the left and left is safe",
            "right": "food is to the right and right is safe",
        },
    },
}


class Snake:
    def __init__(self, root):
        self.root = root
        self.canvas = tk.Canvas(root, width=CELL * GRID, height=CELL * GRID, bg="#111")
        self.canvas.pack()
        self.label = tk.Label(root, font=("Consolas", 11))
        self.label.pack()
        root.bind("<Key>", self.on_key)
        self.auto = False
        self.reset()
        self.tick()

    def reset(self):
        self.body = [(GRID // 2, GRID // 2)]
        self.dir = "right"
        self.score = 0
        self.dead = False
        self.food = self.spawn_food()

    def spawn_food(self):
        free = [(x, y) for x in range(GRID) for y in range(GRID) if (x, y) not in self.body]
        return random.choice(free)

    def is_safe(self, d):
        hx, hy = self.body[0]
        nx, ny = hx + DIRS[d][0], hy + DIRS[d][1]
        return 0 <= nx < GRID and 0 <= ny < GRID and (nx, ny) not in self.body[:-1]

    def describe(self):
        hx, hy = self.body[0]
        fx, fy = self.food
        dx, dy = fx - hx, fy - hy
        parts = []
        if dx: parts.append(f"{abs(dx)} cells {'right' if dx > 0 else 'left'}")
        if dy: parts.append(f"{abs(dy)} cells {'down' if dy > 0 else 'up'}")
        blocked = [d for d in DIRS if not self.is_safe(d)]
        return (f"Snake moving {self.dir}. Food is {' and '.join(parts)}. "
                f"Blocked directions: {', '.join(blocked) or 'none'}.")

    def pick_auto(self):
        with TypeSafeClient(timeout=120) as client:
            result = client.system_one(
                state={"Position": self.describe()},
                questions=QUESTIONS,
    )


        # result = router.predict(self.describe(), QUESTIONS)
        choice = result["answers"]["move"]["choice"]
        opposite = {"up": "down", "down": "up", "left": "right", "right": "left"}
        # guardrail: if laya picks a reverse/fatal move, fall back to any safe one
        if choice == opposite[self.dir] or not self.is_safe(choice):
            safe = [d for d in DIRS if d != opposite[self.dir] and self.is_safe(d)]
            choice = safe[0] if safe else self.dir
        return choice

    def on_key(self, e):
        k = e.keysym if e.keysym in KEYS else e.char.lower()
        if k == "a":
            self.auto = not self.auto
        elif k == "r":
            self.reset()
        elif k in KEYS:
            new = KEYS[k]
            opposite = {"up": "down", "down": "up", "left": "right", "right": "left"}
            if not self.auto and new != opposite[self.dir]:
                self.dir = new

    def tick(self):
        if not self.dead:
            if self.auto:
                self.dir = self.pick_auto()
            hx, hy = self.body[0]
            nx, ny = hx + DIRS[self.dir][0], hy + DIRS[self.dir][1]
            if not (0 <= nx < GRID and 0 <= ny < GRID) or (nx, ny) in self.body[:-1]:
                self.dead = True
            else:
                self.body.insert(0, (nx, ny))
                if (nx, ny) == self.food:
                    self.score += 1
                    self.food = self.spawn_food()
                else:
                    self.body.pop()
        self.draw()
        self.root.after(TICK, self.tick)

    def draw(self):
        c = self.canvas
        c.delete("all")
        fx, fy = self.food
        c.create_oval(fx * CELL + 2, fy * CELL + 2, fx * CELL + CELL - 2, fy * CELL + CELL - 2, fill="#e74c3c")
        for i, (x, y) in enumerate(self.body):
            c.create_rectangle(x * CELL + 1, y * CELL + 1, x * CELL + CELL - 1, y * CELL + CELL - 1,
                               fill="#2ecc71" if i else "#a8ffcf", outline="")
        if self.dead:
            c.create_text(CELL * GRID / 2, CELL * GRID / 2, text="GAME OVER\nR to restart",
                          fill="white", font=("Consolas", 18, "bold"), justify="center")
        mode = "laya autopilot" if self.auto else "manual"
        self.label.config(text=f"Score: {self.score}   Mode: {mode}   [A] toggle  [R] restart")


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Snake x laya")
    Snake(root)
    root.mainloop()