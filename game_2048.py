import tkinter as tk
import random
import colors as c
import time
import math

class Game(tk.Frame):
    def __init__(self):
        tk.Frame.__init__(self)
        self.grid()
        self.master.title('2048')
        
        self.main_grid = tk.Frame(
            self, bg=c.GRID_COLOR, bd=3, width=400, height=400)
        self.main_grid.grid(pady=(80, 0))
        self.make_GUI()
        self.start_game()

        self.master.bind("<Left>", self.left)
        self.master.bind("<Right>", self.right)
        self.master.bind("<Up>", self.up)
        self.master.bind("<Down>", self.down)

        self.animation_speed = 15  # milliseconds between animation frames
        self.animation_steps = 15  # number of steps in animation
        self.is_animating = False
        self.animations = []  # List to track active animations

        self.mainloop()

    def make_GUI(self):
        # make grid
        self.cells = []
        for i in range(4):
            row = []
            for j in range(4):
                cell_frame = tk.Frame(
                    self.main_grid,
                    bg=c.EMPTY_CELL_COLOR,
                    width=100,
                    height=100)
                cell_frame.grid(row=i, column=j, padx=5, pady=5)
                
                # Create a canvas for animations
                canvas = tk.Canvas(
                    cell_frame,
                    width=90,
                    height=90,
                    bg=c.EMPTY_CELL_COLOR,
                    highlightthickness=0)
                canvas.place(relx=0.5, rely=0.5, anchor="center")
                
                cell_data = {
                    "frame": cell_frame,
                    "canvas": canvas,
                    "value": 0,
                    "tile": None  # Will store the tile rectangle
                }
                row.append(cell_data)
            self.cells.append(row)

        # make score header
        score_frame = tk.Frame(self)
        score_frame.place(relx=0.5, y=40, anchor="center")
        tk.Label(
            score_frame,
            text="Score",
            font=("Arial", 20)
        ).grid(row=0)
        self.score_label = tk.Label(score_frame, text="0", font=("Arial", 20))
        self.score_label.grid(row=1)

    def start_game(self):
        # create matrix of zeroes
        self.matrix = [[0] * 4 for _ in range(4)]
        
        # fill 2 random cells with 2s
        row = random.randint(0, 3)
        col = random.randint(0, 3)
        self.matrix[row][col] = 2
        self.cells[row][col]["value"] = 2
        
        # Create first tile
        canvas = self.cells[row][col]["canvas"]
        self.cells[row][col]["tile"] = self.create_tile(canvas, 2, 45, 45)
        
        # Create second tile
        while(self.matrix[row][col] != 0):
            row = random.randint(0, 3)
            col = random.randint(0, 3)
        self.matrix[row][col] = 2
        self.cells[row][col]["value"] = 2
        
        # Create second tile
        canvas = self.cells[row][col]["canvas"]
        self.cells[row][col]["tile"] = self.create_tile(canvas, 2, 45, 45)

        self.score = 0

    def create_tile(self, canvas, value, x, y, scale=1.0, alpha=1.0):
        # Clear previous content
        canvas.delete("all")
        
        if value == 0:
            return None
            
        # Get color for the value
        color = c.CELL_COLORS[value]
        
        # Calculate size based on scale
        size = 90 * scale
        
        # Create rounded rectangle
        tile = canvas.create_rectangle(
            x - size/2, y - size/2,
            x + size/2, y + size/2,
            fill=color,
            outline="",
            width=0
        )
        
        # Add text
        text_color = c.CELL_NUMBER_COLORS[value]
        font = c.CELL_NUMBER_FONTS[value]
        canvas.create_text(
            x, y,
            text=str(value),
            fill=text_color,
            font=font
        )
        
        return tile

    def animate_tile(self, from_pos, to_pos, value, step=0):
        if step >= self.animation_steps:
            if self.animate_tile in self.animations:
                self.animations.remove(self.animate_tile)
            if not self.animations:
                self.is_animating = False
            return

        # Calculate intermediate position
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        # Calculate current position based on animation step
        progress = step / self.animation_steps
        current_row = from_row + (to_row - from_row) * progress
        current_col = from_col + (to_col - from_col) * progress

        # Calculate scale and alpha for pop effect
        scale = 1.0
        if value > 0:  # Only animate non-empty tiles
            if progress < 0.3:  # Pop out
                scale = 1.0 + 0.2 * (progress / 0.3)
            elif progress > 0.7:  # Pop in
                scale = 1.0 + 0.2 * ((1 - progress) / 0.3)

        # Update tile position and appearance
        canvas = self.cells[from_row][from_col]["canvas"]
        
        # Create new tile with current animation state
        self.cells[from_row][from_col]["tile"] = self.create_tile(
            canvas, value, 45, 45, scale)

        # Schedule next animation step
        self.after(self.animation_speed, 
                  lambda: self.animate_tile(from_pos, to_pos, value, step + 1))

    def update_GUI(self):
        for i in range(4):
            for j in range(4):
                cell_value = self.matrix[i][j]
                if cell_value == 0:
                    self.cells[i][j]["canvas"].delete("all")
                    self.cells[i][j]["value"] = 0
                else:
                    if self.cells[i][j]["value"] != cell_value:
                        # Start new animation
                        self.is_animating = True
                        if self.animate_tile not in self.animations:
                            self.animations.append(self.animate_tile)
                        self.animate_tile((i, j), (i, j), cell_value)
                    self.cells[i][j]["value"] = cell_value

        self.score_label.configure(text=self.score)
        self.update_idletasks()

    def add_new_tile(self):
        if self.is_animating:
            self.after(100, self.add_new_tile)
            return

        row = random.randint(0, 3)
        col = random.randint(0, 3)
        while(self.matrix[row][col] != 0):
            row = random.randint(0, 3)
            col = random.randint(0, 3)
        self.matrix[row][col] = random.choice([2, 4])
        self.update_GUI()

    # Matrix Manipulation Functions
    def stack(self):
        new_matrix = [[0] * 4 for _ in range(4)]
        for i in range(4):
            fill_position = 0
            for j in range(4):
                if self.matrix[i][j] != 0:
                    new_matrix[i][fill_position] = self.matrix[i][j]
                    fill_position += 1
        self.matrix = new_matrix

    def combine(self):
        for i in range(4):
            for j in range(3):
                if self.matrix[i][j] != 0 and self.matrix[i][j] == self.matrix[i][j + 1]:
                    self.matrix[i][j] *= 2
                    self.matrix[i][j + 1] = 0
                    self.score += self.matrix[i][j]

    def reverse(self):
        new_matrix = []
        for i in range(4):
            new_matrix.append([])
            for j in range(4):
                new_matrix[i].append(self.matrix[i][3 - j])
        self.matrix = new_matrix

    def transpose(self):
        new_matrix = [[0] * 4 for _ in range(4)]
        for i in range(4):
            for j in range(4):
                new_matrix[i][j] = self.matrix[j][i]
        self.matrix = new_matrix

    # Arrow-Press Functions
    def left(self, event):
        if self.is_animating:
            return
        self.stack()
        self.combine()
        self.stack()
        self.add_new_tile()
        self.game_over()

    def right(self, event):
        if self.is_animating:
            return
        self.reverse()
        self.stack()
        self.combine()
        self.stack()
        self.reverse()
        self.add_new_tile()
        self.game_over()

    def up(self, event):
        if self.is_animating:
            return
        self.transpose()
        self.stack()
        self.combine()
        self.stack()
        self.transpose()
        self.add_new_tile()
        self.game_over()

    def down(self, event):
        if self.is_animating:
            return
        self.transpose()
        self.reverse()
        self.stack()
        self.combine()
        self.stack()
        self.reverse()
        self.transpose()
        self.add_new_tile()
        self.game_over()

    # Check if any moves are possible
    def horizontal_move_exists(self):
        for i in range(4):
            for j in range(3):
                if self.matrix[i][j] == self.matrix[i][j + 1]:
                    return True
        return False

    def vertical_move_exists(self):
        for i in range(3):
            for j in range(4):
                if self.matrix[i][j] == self.matrix[i + 1][j]:
                    return True
        return False

    # Check if game is over (Win/Lose)
    def game_over(self):
        if any(2048 in row for row in self.matrix):
            game_over_frame = tk.Frame(self.main_grid, borderwidth=2)
            game_over_frame.place(relx=0.5, rely=0.5, anchor="center")
            tk.Label(
                game_over_frame,
                text="You Win!",
                bg=c.WINNER_BG,
                fg=c.GAME_OVER_FONT_COLOR,
                font=c.GAME_OVER_FONT).pack()
        elif not any(0 in row for row in self.matrix) and not self.horizontal_move_exists() and not self.vertical_move_exists():
            game_over_frame = tk.Frame(self.main_grid, borderwidth=2)
            game_over_frame.place(relx=0.5, rely=0.5, anchor="center")
            tk.Label(
                game_over_frame,
                text="Game Over!",
                bg=c.LOSER_BG,
                fg=c.GAME_OVER_FONT_COLOR,
                font=c.GAME_OVER_FONT).pack()

if __name__ == "__main__":
    Game() 