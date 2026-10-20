from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


OUTPUT = Path(__file__).resolve().parent
WIDTH, HEIGHT = 1050, 600
SEA = (32, 178, 170)
DEEP = (9, 27, 38)
INK = (23, 38, 48)
CORAL = (255, 128, 107)
WHITE = (255, 255, 255)
MUTED = (190, 209, 214)
FONT_DIR = Path(r"C:\Windows\Fonts")


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_DIR / name), size)


def rounded_gradient(size: tuple[int, int], top: tuple[int, ...], bottom: tuple[int, ...]) -> Image.Image:
    width, height = size
    image = Image.new("RGB", size)
    pixels = image.load()
    for y in range(height):
        ratio = y / max(1, height - 1)
        color = tuple(round(top[i] * (1 - ratio) + bottom[i] * ratio) for i in range(3))
        for x in range(width):
            pixels[x, y] = color
    return image


def draw_mark(draw: ImageDraw.ImageDraw, x: int, y: int, size: int) -> None:
    radius = round(size * .28)
    draw.rounded_rectangle((x, y, x + size, y + size), radius=radius, fill=SEA)
    center = x + size * .5
    top = y + size * .22
    shaft_bottom = y + size * .61
    draw.rounded_rectangle(
        (center - size * .085, top, center + size * .085, shaft_bottom),
        radius=size * .035,
        fill=WHITE,
    )
    draw.polygon(
        [
            (center - size * .29, y + size * .58),
            (center + size * .29, y + size * .58),
            (center, y + size * .84),
        ],
        fill=WHITE,
    )
    draw.ellipse(
        (
            x + size * .69,
            y + size * .13,
            x + size * .82,
            y + size * .26,
        ),
        fill=CORAL,
    )


def draw_wordmark(draw: ImageDraw.ImageDraw, x: int, y: int, scale: int, light: bool) -> None:
    primary = WHITE if light else INK
    draw.text((x, y), "One", font=font("segoeuib.ttf", scale), fill=primary)
    one_width = draw.textlength("One", font=font("segoeuib.ttf", scale))
    draw.text((x + one_width, y), "Down", font=font("segoeuib.ttf", scale), fill=SEA)
    draw.text(
        (x + 2, y + scale * 1.12),
        "S O L U T I O N",
        font=font("segoeui.ttf", round(scale * .27)),
        fill=MUTED if light else (91, 112, 121),
    )


def save_jpg(image: Image.Image, path: Path) -> None:
    image.convert("RGB").save(path, "JPEG", quality=95, subsampling=0, dpi=(300, 300), optimize=True)


def make_front() -> Image.Image:
    image = rounded_gradient((WIDTH, HEIGHT), (15, 48, 56), (7, 24, 35))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((22, 22, WIDTH - 22, HEIGHT - 22), radius=34, outline=(69, 119, 120), width=2)
    draw_mark(draw, 72, 76, 98)
    draw_wordmark(draw, 193, 83, 59, True)
    draw.line((72, 229, 978, 229), fill=(54, 91, 96), width=2)
    draw.rounded_rectangle((72, 271, 82, 425), radius=5, fill=SEA)
    draw.text((111, 264), "Muhammad Khalid", font=font("segoeuib.ttf", 58), fill=WHITE)
    draw.text((114, 337), "AI  /  SOFTWARE  /  DIGITAL GROWTH", font=font("segoeui.ttf", 24), fill=(124, 226, 216))
    draw.ellipse((116, 430, 130, 444), fill=SEA)
    draw.text((151, 418), "+92 301 2949584", font=font("segoeuib.ttf", 37), fill=WHITE)
    draw.text((151, 468), "CALL  /  WHATSAPP", font=font("segoeui.ttf", 21), fill=MUTED)
    draw.text((72, 540), "THOUGHTFUL SOFTWARE. MEANINGFUL POSSIBILITIES.", font=font("segoeui.ttf", 18), fill=(145, 173, 179))
    return image


def make_back() -> Image.Image:
    image = Image.new("RGB", (WIDTH, HEIGHT), (247, 250, 249))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((22, 22, WIDTH - 22, HEIGHT - 22), radius=34, outline=(210, 228, 225), width=2)
    draw.rounded_rectangle((0, 0, 310, HEIGHT), radius=0, fill=(13, 40, 49))
    draw_mark(draw, 89, 107, 128)
    draw_wordmark(draw, 71, 284, 41, True)
    draw.text((359, 72), "WHAT WE BUILD", font=font("segoeui.ttf", 23), fill=(24, 126, 120))
    draw.text((359, 111), "Technology with a purpose.", font=font("segoeuib.ttf", 39), fill=INK)
    items = [
        ("01", "AI solutions", "Ankaboot.ai"),
        ("02", "Web development", "Websites · E-commerce · Platforms"),
        ("03", "Mobile apps", "iOS · Android · Product design"),
        ("04", "Custom software", "Business systems · APIs · Integrations"),
        ("05", "Digital marketing", "Strategy · Content · Growth"),
    ]
    y = 195
    for number, title, detail in items:
        draw.rounded_rectangle((361, y + 4, 403, y + 46), radius=14, fill=(225, 246, 242))
        draw.text((370, y + 12), number, font=font("segoeuib.ttf", 17), fill=(21, 126, 119))
        draw.text((424, y), title, font=font("segoeuib.ttf", 25), fill=INK)
        draw.text((424, y + 34), detail, font=font("segoeui.ttf", 18), fill=(94, 112, 120))
        y += 77
    draw.line((359, 572, 973, 572), fill=(210, 226, 222), width=2)
    return image


def make_logo(size: tuple[int, int], light: bool) -> Image.Image:
    width, height = size
    image = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    mark_size = round(height * .78)
    x, y = round(height * .1), round(height * .11)
    draw_mark(draw, x, y, mark_size)
    draw_wordmark(draw, round(height * 1.02), round(height * .15), round(height * .40), light)
    return image


def make_icon(size: int) -> Image.Image:
    image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw_mark(ImageDraw.Draw(image), round(size * .06), round(size * .06), round(size * .88))
    return image


def save_svg_assets() -> None:
    primary = """<svg xmlns="http://www.w3.org/2000/svg" width="720" height="180" viewBox="0 0 720 180"><g transform="translate(18 19)"><rect width="142" height="142" rx="40" fill="#20b2aa"/><path d="M59 34h24v55h22L71 126 37 89h25V58l-14 8V45z" fill="#fff"/><circle cx="112" cy="23" r="9" fill="#ff806b"/></g><text x="188" y="91" font-family="Segoe UI,Arial,sans-serif" font-size="64" font-weight="700" fill="#172630">One</text><text x="319" y="91" font-family="Segoe UI,Arial,sans-serif" font-size="64" font-weight="700" fill="#20b2aa">Down</text><text x="191" y="137" font-family="Segoe UI,Arial,sans-serif" font-size="19" letter-spacing="8" fill="#5b7079">SOLUTION</text></svg>"""
    white = primary.replace('fill="#172630"', 'fill="#ffffff"').replace('fill="#5b7079"', 'fill="#c5d2d5"')
    (OUTPUT / "onedown-logo.svg").write_text(primary, encoding="utf-8")
    (OUTPUT / "onedown-logo-white.svg").write_text(white, encoding="utf-8")
    (OUTPUT / "business-card-front.svg").write_text(make_card_svg(front=True), encoding="utf-8")
    (OUTPUT / "business-card-back.svg").write_text(make_card_svg(front=False), encoding="utf-8")


def make_card_svg(front: bool) -> str:
    if front:
        return """<svg xmlns="http://www.w3.org/2000/svg" width="1050" height="600" viewBox="0 0 1050 600"><defs><linearGradient id="bg" x2="0" y2="1"><stop stop-color="#0f3038"/><stop offset="1" stop-color="#071823"/></linearGradient></defs><rect width="1050" height="600" rx="34" fill="url(#bg)"/><rect x="22" y="22" width="1006" height="556" rx="34" fill="none" stroke="#457778" stroke-width="2"/><g transform="translate(72 76)"><rect width="98" height="98" rx="27" fill="#20b2aa"/><path d="M41 22h17v38h16L49 83 25 60h17V39l-10 6V29z" fill="white"/><circle cx="76" cy="16" r="6" fill="#ff806b"/></g><text x="193" y="137" font-family="Arial,sans-serif" font-size="59" font-weight="700" fill="white">One<tspan fill="#20b2aa">Down</tspan></text><text x="195" y="178" font-family="Arial,sans-serif" font-size="16" letter-spacing="7" fill="#bed1d6">S O L U T I O N</text><path d="M72 229h906" stroke="#365b60" stroke-width="2"/><rect x="72" y="271" width="10" height="154" rx="5" fill="#20b2aa"/><text x="111" y="322" font-family="Arial,sans-serif" font-size="58" font-weight="700" fill="white">Muhammad Khalid</text><text x="114" y="376" font-family="Arial,sans-serif" font-size="24" fill="#7ce2d8">AI  /  SOFTWARE  /  DIGITAL GROWTH</text><text x="151" y="450" font-family="Arial,sans-serif" font-size="37" font-weight="700" fill="white">+92 301 2949584</text><text x="151" y="493" font-family="Arial,sans-serif" font-size="21" fill="#bed1d6">CALL  /  WHATSAPP</text><text x="72" y="554" font-family="Arial,sans-serif" font-size="18" letter-spacing="1" fill="#91adb3">THOUGHTFUL SOFTWARE. MEANINGFUL POSSIBILITIES.</text></svg>"""
    return """<svg xmlns="http://www.w3.org/2000/svg" width="1050" height="600" viewBox="0 0 1050 600"><rect width="1050" height="600" rx="34" fill="#f7faf9"/><rect x="22" y="22" width="1006" height="556" rx="34" fill="none" stroke="#d2e4e1" stroke-width="2"/><path d="M34 22h242a34 34 0 0 1 34 34v488a34 34 0 0 1-34 34H34z" fill="#0d2831"/><g transform="translate(89 107)"><rect width="128" height="128" rx="36" fill="#20b2aa"/><path d="M54 29h22v50h20l-31 34-31-34h22V51l-13 7V37z" fill="white"/><circle cx="99" cy="21" r="8" fill="#ff806b"/></g><text x="71" y="326" font-family="Arial,sans-serif" font-size="41" font-weight="700" fill="white">One<tspan fill="#20b2aa">Down</tspan></text><text x="73" y="358" font-family="Arial,sans-serif" font-size="13" letter-spacing="5" fill="#c5d2d5">SOLUTION</text><text x="359" y="95" font-family="Arial,sans-serif" font-size="23" letter-spacing="2" fill="#187e78">WHAT WE BUILD</text><text x="359" y="153" font-family="Arial,sans-serif" font-size="39" font-weight="700" fill="#172630">Technology with a purpose.</text>""" + "".join(
        f'<rect x="361" y="{199+i*77}" width="42" height="42" rx="14" fill="#e1f6f2"/><text x="370" y="{227+i*77}" font-family="Arial,sans-serif" font-size="17" font-weight="700" fill="#157e77">{i+1:02}</text><text x="424" y="{220+i*77}" font-family="Arial,sans-serif" font-size="25" font-weight="700" fill="#172630">{title}</text><text x="424" y="{251+i*77}" font-family="Arial,sans-serif" font-size="18" fill="#5e7078">{detail}</text>'
        for i, (title, detail) in enumerate(
            [
                ("AI solutions", "Ankaboot.ai"),
                ("Web development", "Websites · E-commerce · Platforms"),
                ("Mobile apps", "iOS · Android · Product design"),
                ("Custom software", "Business systems · APIs · Integrations"),
                ("Digital marketing", "Strategy · Content · Growth"),
            ]
        )
    ) + '<path d="M359 572h614" stroke="#d2e2de" stroke-width="2"/></svg>'


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    save_svg_assets()

    front = make_front()
    back = make_back()
    for name, image in (("business-card-front", front), ("business-card-back", back)):
        image.save(OUTPUT / f"{name}.png", "PNG", dpi=(300, 300), optimize=True)
        save_jpg(image, OUTPUT / f"{name}.jpg")

    front.save(
        OUTPUT / "business-card-print.pdf",
        "PDF",
        resolution=300,
        save_all=True,
        append_images=[back],
    )

    logo = make_logo((1200, 300), light=False)
    logo.save(OUTPUT / "onedown-logo.png", "PNG", optimize=True)
    logo_rgb = Image.new("RGB", logo.size, WHITE)
    logo_rgb.paste(logo, mask=logo.getchannel("A"))
    save_jpg(logo_rgb, OUTPUT / "onedown-logo.jpg")

    white_logo = make_logo((1200, 300), light=True)
    white_logo.save(OUTPUT / "onedown-logo-white.png", "PNG", optimize=True)
    white_logo_rgb = Image.new("RGB", white_logo.size, DEEP)
    white_logo_rgb.paste(white_logo, mask=white_logo.getchannel("A"))
    save_jpg(white_logo_rgb, OUTPUT / "onedown-logo-white.jpg")

    mark = make_icon(512)
    mark.save(OUTPUT / "onedown-icon.png", "PNG", optimize=True)
    mark_rgb = Image.new("RGB", mark.size, WHITE)
    mark_rgb.paste(mark, mask=mark.getchannel("A"))
    save_jpg(mark_rgb, OUTPUT / "onedown-icon.jpg")

    preview = Image.new("RGB", (1080, 340), (233, 240, 238))
    preview.paste(front.resize((510, 291), Image.Resampling.LANCZOS), (20, 24))
    preview.paste(back.resize((510, 291), Image.Resampling.LANCZOS), (550, 24))
    preview.save(OUTPUT / "business-card-preview.png", "PNG", optimize=True)


if __name__ == "__main__":
    main()
