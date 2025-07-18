def color_text(text, color=None, style=None, background=None):
    # ANSI color codes
    colors = {
        "black": 30, "red": 31, "green": 32, "yellow": 33,
        "blue": 34, "magenta": 35, "cyan": 36, "white": 37
    }
    styles = {
        "normal": 0, "bold": 1, "underline": 4
    }
    backgrounds = {
        "black": 40, "red": 41, "green": 42, "yellow": 43,
        "blue": 44, "magenta": 45, "cyan": 46, "white": 47
    }

    codes = []

    if style in styles:
        codes.append(str(styles[style]))
    if color in colors:
        codes.append(str(colors[color]))
    if background in backgrounds:
        codes.append(str(backgrounds[background]))

    prefix = f"\033[{';'.join(codes)}m" if codes else ""
    suffix = "\033[0m" if codes else ""

    return f"{prefix}{text}{suffix}"


def color_print(*args, color=None, style=None, background=None, sep=" ", end="\n"):
    colored_args = [color_text(
        str(arg), color=color, style=style, background=background) for arg in args]
    print(*colored_args, sep=sep, end=end)

# color_print("Hello, world!", color="green")
# color_print("Error!", color="red", style="bold")
# color_print("Warning", color="yellow", background="black", style="underline")
