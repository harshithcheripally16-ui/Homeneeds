# generate_icons.py
# Location: Home Needs/generate_icons.py
# Run: python generate_icons.py

import subprocess
import sys
import os


def install_pillow():
    """Install Pillow if not available"""
    try:
        from PIL import Image, ImageDraw
        return True
    except ImportError:
        print("📦 Installing Pillow library...")
        subprocess.check_call(
            [sys.executable, '-m', 'pip', 'install', 'Pillow'],
            stdout=subprocess.DEVNULL
        )
        print("  ✓ Pillow installed\n")
        return True


def create_home_needs_icon(size, output_path):
    """Create a professional Home Needs app icon"""
    from PIL import Image, ImageDraw, ImageFont
    import math

    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # ---- Background: Rounded square with gradient effect ----
    # Outer rounded rectangle
    corner_radius = int(size * 0.22)

    # Create gradient background using multiple rectangles
    for i in range(size):
        # Gradient from #E23744 (top) to #CB202D (bottom)
        ratio = i / size
        r = int(226 + (203 - 226) * ratio)
        g = int(55 + (32 - 55) * ratio)
        b = int(68 + (45 - 68) * ratio)
        color = (r, g, b, 255)
        draw.line([(0, i), (size, i)], fill=color)

    # Apply rounded corner mask
    mask = Image.new('L', (size, size), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle(
        [0, 0, size - 1, size - 1],
        radius=corner_radius,
        fill=255
    )
    img.putalpha(mask)

    # ---- Subtle highlight circle in top-left ----
    highlight = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    h_draw = ImageDraw.Draw(highlight)
    highlight_size = int(size * 0.8)
    h_draw.ellipse(
        [-highlight_size // 3, -highlight_size // 3,
         highlight_size, highlight_size],
        fill=(255, 255, 255, 20)
    )
    # Composite highlight
    img = Image.alpha_composite(img, highlight)
    draw = ImageDraw.Draw(img)

    # ---- House Icon ----
    cx = size * 0.5        # center x
    cy = size * 0.48       # center y (slightly above center)
    s = size * 0.22        # scale factor

    # House roof (triangle)
    roof_points = [
        (cx - s * 1.35, cy + s * 0.1),    # left eave
        (cx, cy - s * 1.2),                 # peak
        (cx + s * 1.35, cy + s * 0.1),    # right eave
    ]
    draw.polygon(roof_points, fill=(255, 255, 255, 240))

    # House body (rectangle)
    body_left = cx - s * 1.0
    body_right = cx + s * 1.0
    body_top = cy + s * 0.1
    body_bottom = cy + s * 1.2
    draw.rounded_rectangle(
        [body_left, body_top, body_right, body_bottom],
        radius=int(s * 0.1),
        fill=(255, 255, 255, 240)
    )

    # Door
    door_w = s * 0.4
    door_h = s * 0.65
    door_left = cx - door_w / 2
    door_top = body_bottom - door_h
    door_radius = int(s * 0.15)
    draw.rounded_rectangle(
        [door_left, door_top, door_left + door_w, body_bottom],
        radius=door_radius,
        fill=(226, 55, 68, 255)
    )

    # Door knob
    knob_r = max(int(s * 0.05), 1)
    knob_x = door_left + door_w * 0.7
    knob_y = door_top + door_h * 0.55
    draw.ellipse(
        [knob_x - knob_r, knob_y - knob_r,
         knob_x + knob_r, knob_y + knob_r],
        fill=(255, 255, 255, 200)
    )

    # Windows (two small squares)
    win_size = s * 0.28
    win_gap = s * 0.15

    # Left window
    wl_x = cx - s * 0.65
    wl_y = cy + s * 0.35
    draw.rounded_rectangle(
        [wl_x, wl_y, wl_x + win_size, wl_y + win_size],
        radius=int(s * 0.05),
        fill=(226, 55, 68, 180)
    )
    # Window cross
    wmid_x = wl_x + win_size / 2
    wmid_y = wl_y + win_size / 2
    line_w = max(int(s * 0.03), 1)
    draw.line([(wmid_x, wl_y + 2), (wmid_x, wl_y + win_size - 2)],
              fill=(255, 255, 255, 150), width=line_w)
    draw.line([(wl_x + 2, wmid_y), (wl_x + win_size - 2, wmid_y)],
              fill=(255, 255, 255, 150), width=line_w)

    # Right window
    wr_x = cx + s * 0.35
    wr_y = wl_y
    draw.rounded_rectangle(
        [wr_x, wr_y, wr_x + win_size, wr_y + win_size],
        radius=int(s * 0.05),
        fill=(226, 55, 68, 180)
    )
    wmid_x2 = wr_x + win_size / 2
    wmid_y2 = wr_y + win_size / 2
    draw.line([(wmid_x2, wr_y + 2), (wmid_x2, wr_y + win_size - 2)],
              fill=(255, 255, 255, 150), width=line_w)
    draw.line([(wr_x + 2, wmid_y2), (wr_x + win_size - 2, wmid_y2)],
              fill=(255, 255, 255, 150), width=line_w)

    # ---- Small leaf accent (bottom-right of house) ----
    leaf_cx = cx + s * 1.1
    leaf_cy = cy + s * 0.85
    leaf_s = s * 0.35

    # Leaf shape using ellipse
    leaf_points = [
        (leaf_cx - leaf_s * 0.1, leaf_cy + leaf_s * 0.5),
        (leaf_cx - leaf_s * 0.6, leaf_cy - leaf_s * 0.2),
        (leaf_cx, leaf_cy - leaf_s * 0.7),
        (leaf_cx + leaf_s * 0.6, leaf_cy - leaf_s * 0.2),
        (leaf_cx + leaf_s * 0.1, leaf_cy + leaf_s * 0.5),
    ]
    draw.polygon(leaf_points, fill=(46, 213, 115, 220))

    # Leaf vein
    vein_w = max(int(s * 0.02), 1)
    draw.line(
        [(leaf_cx, leaf_cy - leaf_s * 0.5), (leaf_cx, leaf_cy + leaf_s * 0.3)],
        fill=(255, 255, 255, 120),
        width=vein_w
    )

    # ---- Text "H" badge (optional small touch) ----
    # Chimney
    chimney_w = s * 0.2
    chimney_h = s * 0.45
    chimney_x = cx + s * 0.45
    chimney_top = cy - s * 0.85
    draw.rounded_rectangle(
        [chimney_x, chimney_top,
         chimney_x + chimney_w, cy - s * 0.2],
        radius=int(s * 0.05),
        fill=(255, 255, 255, 200)
    )

    # Save
    final = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    final.paste(img, (0, 0), img)
    final.save(output_path, 'PNG', optimize=True)


def create_adaptive_icon(size, output_path):
    """Create adaptive icon with safe zone for Android"""
    from PIL import Image, ImageDraw

    # Adaptive icons need 108dp with 72dp safe zone
    # Add padding around the icon
    padding = int(size * 0.1)
    inner_size = size - (padding * 2)

    # Create the main icon at inner size
    temp_path = output_path + '.temp.png'
    create_home_needs_icon(inner_size, temp_path)

    # Place on larger canvas
    canvas = Image.new('RGBA', (size, size), (226, 55, 68, 255))
    inner = Image.open(temp_path)
    canvas.paste(inner, (padding, padding), inner)
    canvas.save(output_path, 'PNG', optimize=True)

    # Cleanup temp
    try:
        os.remove(temp_path)
    except Exception:
        pass


def main():
    install_pillow()

    # Determine icons directory
    icons_dir = os.path.join('frontend', 'icons')

    # Also check if old structure exists
    if not os.path.exists('frontend'):
        # Maybe still using old structure
        icons_dir = os.path.join('static', 'icons')

    os.makedirs(icons_dir, exist_ok=True)

    print("=" * 50)
    print("  🎨 Generating Home Needs App Icons")
    print("=" * 50)
    print(f"  Output: {os.path.abspath(icons_dir)}\n")

    sizes = [72, 96, 128, 144, 152, 192, 384, 512]

    for size in sizes:
        filename = f'icon-{size}x{size}.png'
        output_path = os.path.join(icons_dir, filename)
        create_home_needs_icon(size, output_path)
        file_size = os.path.getsize(output_path) / 1024
        print(f"  ✓ {filename:24s} ({file_size:.1f} KB)")

    # Create a foreground icon for adaptive icons
    adaptive_path = os.path.join(icons_dir, 'icon-adaptive-512x512.png')
    create_adaptive_icon(512, adaptive_path)
    file_size = os.path.getsize(adaptive_path) / 1024
    print(f"  ✓ {'icon-adaptive-512x512.png':24s} ({file_size:.1f} KB)")

    print(f"\n{'=' * 50}")
    print(f"  ✅ All {len(sizes) + 1} icons generated successfully!")
    print(f"  📁 Location: {os.path.abspath(icons_dir)}")
    print(f"{'=' * 50}")

    # Verify all files exist
    print(f"\n  Verification:")
    all_good = True
    for size in sizes:
        path = os.path.join(icons_dir, f'icon-{size}x{size}.png')
        if os.path.exists(path):
            print(f"    ✓ icon-{size}x{size}.png")
        else:
            print(f"    ✗ icon-{size}x{size}.png MISSING")
            all_good = False

    if all_good:
        print(f"\n  All icons ready for manifest.json and Play Store! 🚀")


if __name__ == '__main__':
    main()
