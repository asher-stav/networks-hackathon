color_map = {
    'w': (255, 255, 255),  # White color
    'ws': (255, 255, 255),  # WhiteSpace
    'g': (164, 208, 157),     # Matcha green(darker)
    'lg': (210, 226, 173),     # Olive green(lighter)
    'd': (70, 53, 97),  # Dark Purple
    'b': (160, 219, 241),   # Light blue
    'p': (249, 161, 166),    # Pink
    'lp': (250, 231, 220),    # Pink
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
            numStartIdx = 0
            color = ''
            for char in item:
                if char.isalpha():
                    color += char
                    numStartIdx += 1
                else:
                    break
            count = int(item[numStartIdx:])  # Extract the number of repetitions
            parsed_row.extend([color] * count)  # Repeat the color accordingly
        parsed_pixels.append(parsed_row)
    return parsed_pixels

# Print teapot pixels with colored backgrounds
def print_colored_pixels(pixel_data):
    for row in pixel_data:
        line = ""
        for color in row:
            if color == 'ws':  # Treat 'w' as whitespace (no color, just reset)
                line += "\033[0m  "  # Reset color after whitespace
            else:
                r, g, b = color_map[color]
                ansi_code = rgb_to_ansi(r, g, b)  # Convert to ANSI color code
                line += f"{ansi_code}  "  # Add color background with spaces
        print(line + "\033[0m")  # Reset color after printing the row

# Example teapot pixel data (use the format you provided with w12, g3, etc.)
teapot_pixels_raw = [
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


# Parse the input into the correct 2D array of pixels
teapot_pixels = parse_pixels(teapot_pixels_raw)

print(teapot_pixels)

# Print the teapot with colored pixels
print_colored_pixels(teapot_pixels)
