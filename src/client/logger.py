import random

def gradient_color(start_color, end_color, steps):
    """
    Generate a gradient between two RGB colors over a given number of steps.
    """
    gradient = [
        (
            int(start_color[0] + (end_color[0] - start_color[0]) * i / (steps - 1)),
            int(start_color[1] + (end_color[1] - start_color[1]) * i / (steps - 1)),
            int(start_color[2] + (end_color[2] - start_color[2]) * i / (steps - 1)),
        )
        for i in range(steps)
    ]
    return gradient

def rgb_to_ansi(r, g, b):
    """
    Convert an RGB color to an ANSI escape code.
    """
    return f"\033[38;2;{r};{g};{b}m"

def info(string):
    """
    Print a string where each character is in a random color from a sea gradient.
    """
    sea_start_color=(193, 255, 254) # Teal
    sea_end_color=(0, 79, 118) # Deep Blue

    gradient = gradient_color(sea_start_color, sea_end_color, len(string))
    for char in string:
        r, g, b = random.choice(gradient)  # Randomly pick a color from the gradient
        print(rgb_to_ansi(r, g, b) + char, end="")
    print("\033[0m")

def error(string):
    """
    Print a string in red.
    """
    print("\033[91m" + "!>ERR: " + string + "\033[0m")

def debugging(string):
    """
    Print en default.
    """
    print("\033[3m" + "?>DBG: " + string + "\033[0m")

# print_sea("Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.")
