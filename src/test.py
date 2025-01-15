import threading
import time
from blessed import Terminal

# Teapot pixel data
pixels_raw = [
    ['ws7', 'd7', 'ws14'],
    ['ws4', 'd3', 'b1', 'w6', 'd4', 'ws10'],
    ['ws2', 'd2', 'b7', 'w7', 'd3', 'ws7'],
    ['ws1', 'd1', 'b4', 'd9', 'b3', 'w2', 'd1', 'ws7'],
    ['d1', 'b2', 'd3', 'g9', 'd3', 'b3', 'd1', 'ws1', 'd3', 'ws2'],
    ['d3', 'g3', 'lg12', 'd5', 'p1', 'lp2', 'd1', 'ws1'],
    ['d1', 'w1', 'd2', 'g4', 'lg10', 'd2', 'b1', 'd1', 'p1', 'd3', 'lp1', 'd1'],
    ['d1', 'w3', 'd3', 'g7', 'd4', 'b3', 'd3', 'ws1', 'd1', 'lp1', 'd1'],
    ['d1', 'w5', 'b1', 'd7', 'b8', 'd2', 'ws1', 'd1', 'p1', 'd1'],
    ['d1', 'w13', 'b7', 'd3', 'ws1', 'd1', 'p1', 'd1'],
    ['d1', 'w12', 'b8', 'd1', 'p1', 'd2', 'p1', 'd1', 'ws1'],
    ['ws1', 'd1', 'w12', 'b7', 'd2', 'b1', 'p1', 'd1', 'ws2'],
    ['ws1', 'd1', 'b1', 'w10', 'b11', 'd1', 'ws3'],
    ['ws2', 'd1', 'b2', 'w7', 'b7', 'd5', 'ws4'],
    ['ws3', 'd1', 'b2', 'w5', 'b7', 'd1', 'ws9'],
    ['ws4', 'd1', 'b12', 'd1', 'ws10'],
    ['ws4', 'd2', 'b9', 'd2', 'ws11'],
    ['ws4', 'd1', 'w1', 'd9', 'b1', 'd1', 'ws11'],
    ['ws5', 'd1', 'w1', 'b8', 'd2', 'ws11'],
    ['ws5', 'd2', 'w5', 'b2', 'd2', 'ws12'],
    ['ws7', 'd7', 'ws14']
]

# Color mapping for terminal colors (RGB values)
color_map = {
    'w': (255, 255, 255),  # White
    'ws': (0, 0, 0),       # Black for whitespace
    'g': (164, 208, 157),  # Matcha green
    'lg': (210, 226, 173), # Olive green
    'd': (70, 53, 97),     # Dark Purple
    'b': (160, 219, 241),  # Light blue
    'p': (249, 161, 166),  # Pink
    'lp': (250, 231, 220), # Light pink
    ' ': (0, 0, 0)         # Black for empty space
}

# Initialize the terminal
term = Terminal()

# Parse raw pixel data into a usable 2D list
def parse_pixels(raw_list):
    parsed_pixels = []
    for row in raw_list:
        parsed_row = []
        for item in row:
            num_start_idx = 0
            color = ''
            for char in item:
                if char.isalpha():
                    color += char
                    num_start_idx += 1
                else:
                    break
            count = int(item[num_start_idx:])  # Extract number of repetitions
            parsed_row.extend([color] * count)
        parsed_pixels.append(parsed_row)
    return parsed_pixels

# Convert RGB to ANSI background color
def rgb_to_ansi(r, g, b):
    return term.on_color_rgb(r, g, b)

# Teapot rendering function
def render_teapot(parsed_pixels):
    for row_idx, row in enumerate(parsed_pixels):
        for col_idx, color in enumerate(row):
            r, g, b = color_map[color]
            with term.location(col_idx * 2, row_idx):  # Move cursor to specific position
                print(rgb_to_ansi(r, g, b) + "  " + term.normal, end='', flush=True)
        time.sleep(0.1)  # Add delay for row rendering
    print(term.normal)  # Reset color

# Threaded progress bar
def progress_bar():
    for i in range(101):
        with term.location(0, term.height - 2):  # Fixed position for progress bar
            print(f"Progress: {i}%", end='', flush=True)
        time.sleep(0.1)

# Main function
def main():
    parsed_pixels = parse_pixels(pixels_raw)

    # Start progress bar in a separate thread
    progress_thread = threading.Thread(target=progress_bar, daemon=True)
    progress_thread.start()

    # Render the teapot in the main thread
    with term.hidden_cursor():
        render_teapot(parsed_pixels)

if __name__ == "__main__":
    main()
