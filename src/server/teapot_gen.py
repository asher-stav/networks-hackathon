
color_map = {
    'w': (255, 255, 255),  # White color
    'g': (50, 50, 50),     # Even darker gray
    'b': (80, 50, 20),     # Even darker brown
    'e': (245, 231, 191),  # Beige 
    'r': (219, 204, 160),   # Slightly darker beige
    'p': (136, 17, 85),    # Purple
    ' ': (0, 0, 0)         # Black (for whitespace)
}

# Function to convert RGB to ANSI escape code for terminal
def rgb_to_ansi(r, g, b):
    return f"\033[48;2;{r};{g};{b}m"

# Convert teapot pixels into the correct format
def parse_pixels(raw_list):
    parsed_pixels = []
    for row in raw_list:
        parsed_row = []
        for item in row:
            color = item[0]  # Extract the color code ('w', 'g', etc.)
            count = int(item[1:])  # Extract the number of repetitions
            parsed_row.extend([color] * count)  # Repeat the color accordingly
        parsed_pixels.append(parsed_row)
    return parsed_pixels

# Print teapot pixels with colored backgrounds
def print_colored_pixels(pixel_data):
    for row in pixel_data:
        line = ""
        for color in row:
            if color == 'w':  # Treat 'w' as whitespace (no color, just reset)
                line += "\033[0m  "  # Reset color after whitespace
            else:
                r, g, b = color_map[color]
                ansi_code = rgb_to_ansi(r, g, b)  # Convert to ANSI color code
                line += f"{ansi_code}  "  # Add color background with spaces
        print(line + "\033[0m")  # Reset color after printing the row

# Example teapot pixel data (use the format you provided with w12, g3, etc.)
teapot_pixels_raw = [
    ['w12', 'g3', 'w9'],
    ['w11', 'g1', 'b3', 'g1', 'w8'],
    ['w9', 'g2', 'b5', 'g2', 'w6'],
    ['w8', 'g1', 'e3', 'b3', 'e3', 'g1', 'w5'],
    ['w1', 'g3', 'w3', 'g1', 'e11', 'g1', 'w4'],
    ['g1', 'e3', 'g1', 'w1', 'g1', 'r2', 'e8', 'r2', 'g3', 'w2'],
    ['w1', 'g2', 'e2', 'g2', 'e2', 'r8', 'e5', 'g1', 'w1'],
    ['w2', 'g1', 'e3', 'r1', 'e12', 'g3', 'e1', 'g1'],
    ['w3', 'g1', 'e2', 'r1', 'e12', 'g1', 'w1', 'g1', 'e1', 'g1'],
    ['w4', 'g1', 'e1', 'r1', 'e1', 'p1', 'e2', 'p1', 'e2', 'p1', 'e2', 'p1', 'e1', 'g1', 'w1', 'g1', 'e1', 'g1'],
    ['w5', 'g2', 'p1', 'e1', 'p2', 'e1', 'p2', 'e1', 'p2', 'e1', 'p1', 'g2', 'e1', 'g1', 'w1'],
    ['w6', 'g1', 'e1', 'p1', 'e2', 'p1', 'e2', 'p1', 'e2', 'p1', 'e3', 'g1', 'w2'],
    ['w6', 'g1', 'e12', 'g2', 'w3'],
    ['w7', 'g1', 'e10', 'g1', 'w5'],
    ['w8', 'g1', 'e8', 'g1', 'w6'],
    ['w9', 'g8', 'w7']
]

# Parse the input into the correct 2D array of pixels
teapot_pixels = parse_pixels(teapot_pixels_raw)

# Print the teapot with colored pixels
print_colored_pixels(teapot_pixels)
