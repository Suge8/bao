from assets._build_svg_arch import render_arch
from assets._build_svg_features import render_features
from assets._build_svg_hero import render_hero
from assets._build_svg_shared import themes


def _write_svg(path: str, content: str) -> None:
    with open(path, "w") as file_handle:
        file_handle.write(content)


def save() -> None:
    out_dir = "/Users/sugeh/Documents/Project/Bao/assets"
    for theme_name, t in themes.items():
        _write_svg(f"{out_dir}/hero-{theme_name}.svg", render_hero(t, "zh", theme_name))
        _write_svg(f"{out_dir}/hero-en-{theme_name}.svg", render_hero(t, "en", theme_name))
        _write_svg(f"{out_dir}/features-{theme_name}.svg", render_features(t, "zh", theme_name))
        _write_svg(f"{out_dir}/features-en-{theme_name}.svg", render_features(t, "en", theme_name))
        _write_svg(f"{out_dir}/architecture-{theme_name}.svg", render_arch(t, "zh", theme_name))
        _write_svg(f"{out_dir}/architecture-en-{theme_name}.svg", render_arch(t, "en", theme_name))

if __name__ == "__main__":
    save()
