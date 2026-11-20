import os
import struct
import zlib
import math

FONT = {
    ' ': [0, 0, 0, 0, 0, 0, 0],
    'A': [14, 17, 17, 31, 17, 17, 17],
    'B': [30, 17, 17, 30, 17, 17, 30],
    'C': [14, 17, 16, 16, 16, 17, 14],
    'D': [30, 17, 17, 17, 17, 17, 30],
    'E': [31, 16, 16, 30, 16, 16, 31],
    'F': [31, 16, 16, 30, 16, 16, 16],
    'G': [14, 17, 16, 23, 17, 17, 15],
    'H': [17, 17, 17, 31, 17, 17, 17],
    'I': [14, 4, 4, 4, 4, 4, 14],
    'J': [7, 2, 2, 2, 2, 18, 12],
    'K': [17, 18, 20, 24, 20, 18, 17],
    'L': [16, 16, 16, 16, 16, 16, 31],
    'M': [17, 27, 21, 17, 17, 17, 17],
    'N': [17, 25, 21, 19, 17, 17, 17],
    'O': [14, 17, 17, 17, 17, 17, 14],
    'P': [30, 17, 17, 30, 16, 16, 16],
    'Q': [14, 17, 17, 17, 21, 18, 13],
    'R': [30, 17, 17, 30, 20, 18, 17],
    'S': [14, 17, 16, 14, 1, 17, 14],
    'T': [31, 4, 4, 4, 4, 4, 4],
    'U': [17, 17, 17, 17, 17, 17, 14],
    'V': [17, 17, 17, 17, 10, 10, 4],
    'W': [17, 17, 17, 21, 21, 27, 17],
    'X': [17, 17, 10, 4, 10, 17, 17],
    'Y': [17, 17, 10, 4, 4, 4, 4],
    'Z': [31, 1, 2, 4, 8, 16, 31],
    '0': [14, 17, 19, 21, 25, 17, 14],
    '1': [4, 12, 4, 4, 4, 4, 14],
    '2': [14, 17, 1, 6, 8, 16, 31],
    '3': [31, 1, 2, 14, 1, 1, 30],
    '4': [2, 6, 10, 18, 31, 2, 2],
    '5': [31, 16, 30, 1, 1, 17, 14],
    '6': [14, 16, 16, 30, 17, 17, 14],
    '7': [31, 1, 2, 4, 8, 8, 8],
    '8': [14, 17, 17, 14, 17, 17, 14],
    '9': [14, 17, 17, 15, 1, 1, 14],
    ':': [0, 4, 0, 0, 0, 4, 0],
    '.': [0, 0, 0, 0, 0, 4, 4],
    ',': [0, 0, 0, 0, 0, 4, 8],
    '-': [0, 0, 0, 31, 0, 0, 0],
    '&': [12, 18, 18, 12, 21, 18, 13],
    '\'': [4, 4, 2, 0, 0, 0, 0],
    '/': [1, 2, 4, 8, 16, 0, 0],
    '(': [2, 4, 8, 8, 8, 4, 2],
    ')': [8, 4, 2, 2, 2, 4, 8],
    '?': [14, 17, 1, 2, 4, 0, 4],
    '!': [4, 4, 4, 4, 4, 0, 4]
}

class Canvas:
    def __init__(self, w, h, bg_color=(246, 241, 227)):
        self.w = w
        self.h = h
        self.buf = bytearray(w * h * 3)
        self.fill_rect(0, 0, w, h, bg_color)

    def set_pixel(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            idx = (y * self.w + x) * 3
            self.buf[idx] = color[0]
            self.buf[idx+1] = color[1]
            self.buf[idx+2] = color[2]

    def fill_rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        if x0 >= x1 or y0 >= y1:
            return
        r, g, b = color
        for cy in range(y0, y1):
            row_idx = (cy * self.w + x0) * 3
            for cx in range(x0, x1):
                self.buf[row_idx] = r
                self.buf[row_idx+1] = g
                self.buf[row_idx+2] = b
                row_idx += 3

    def draw_line(self, x0, y0, x1, y1, color):
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            self.set_pixel(x0, y0, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def fill_circle(self, cx, cy, r, color):
        for y in range(-r, r + 1):
            for x in range(-r, r + 1):
                if x*x + y*y <= r*r:
                    self.set_pixel(cx + x, cy + y, color)

    def fill_polygon(self, points, color):
        if not points:
            return
        min_y = min(p[1] for p in points)
        max_y = max(p[1] for p in points)
        n = len(points)
        for y in range(max(0, min_y), min(self.h, max_y + 1)):
            nodes = []
            j = n - 1
            for i in range(n):
                xi, yi = points[i]
                xj, yj = points[j]
                if (yi < y and yj >= y) or (yj < y and yi >= y):
                    if yi != yj:
                        nodes.append(int(xi + (y - yi) * (xj - xi) / (yj - yi)))
                j = i
            nodes.sort()
            for i in range(0, len(nodes), 2):
                if i + 1 < len(nodes):
                    x_start = max(0, nodes[i])
                    x_end = min(self.w, nodes[i+1])
                    if x_start < x_end:
                        self.fill_rect(x_start, y, x_end - x_start, 1, color)

    def fill_rounded_rect(self, x, y, w, h, r, color):
        r = min(r, w // 2, h // 2)
        self.fill_rect(x + r, y, w - 2 * r, h, color)
        self.fill_rect(x, y + r, w, h - 2 * r, color)
        self.fill_circle(x + r, y + r, r, color)
        self.fill_circle(x + w - r - 1, y + r, r, color)
        self.fill_circle(x + r, y + h - r - 1, r, color)
        self.fill_circle(x + w - r - 1, y + h - r - 1, r, color)

def wrap_text(s, max_chars):
    words = s.split(' ')
    lines = []
    current_line = []
    current_len = 0
    for w in words:
        w_len = len(w)
        if not current_line:
            current_line.append(w)
            current_len = w_len
        elif current_len + 1 + w_len <= max_chars:
            current_line.append(w)
            current_len += 1 + w_len
        else:
            lines.append(' '.join(current_line))
            current_line = [w]
            current_len = w_len
    if current_line:
        lines.append(' '.join(current_line))
    return lines

def draw_text(canvas, x, y, s, scale, color, align='left'):
    char_w = 5 * scale
    char_gap = 1 * scale
    total_w = 0
    for i, ch in enumerate(s):
        total_w += char_w if i == 0 else char_w + char_gap
    
    start_x = x
    if align == 'center':
        start_x = x - total_w // 2
    elif align == 'right':
        start_x = x - total_w

    curr_x = start_x
    for ch in s:
        glyph = FONT.get(ch, FONT.get('?', [0]*7))
        for r_idx, row_val in enumerate(glyph):
            for bit_idx in range(5):
                if (row_val >> (4 - bit_idx)) & 1:
                    px = curr_x + bit_idx * scale
                    py = y + r_idx * scale
                    canvas.fill_rect(px, py, scale, scale, color)
        curr_x += char_w + char_gap

def draw_text_block(canvas, x, y, lines, scale, color, align='left', line_spacing=2):
    line_h = 7 * scale + line_spacing * scale
    for i, line in enumerate(lines):
        draw_text(canvas, x, y + i * line_h, line, scale, color, align)

def encode_png(buf, w, h, path):
    row_size = w * 3
    filtered_data = bytearray()
    for y in range(h):
        filtered_data.append(0)
        start = y * row_size
        filtered_data.extend(buf[start:start + row_size])
    
    compressed = zlib.compress(filtered_data, 9)
    
    def make_chunk(chunk_type, data):
        return struct.pack('>I', len(data)) + chunk_type + data + struct.pack('>I', zlib.crc32(chunk_type + data) & 0xFFFFFFFF)

    png_bytes = bytearray(b'\x89PNG\r\n\x1a\n')
    ihdr_data = struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0)
    png_bytes.extend(make_chunk(b'IHDR', ihdr_data))
    png_bytes.extend(make_chunk(b'IDAT', compressed))
    png_bytes.extend(make_chunk(b'IEND', b''))
    
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, 'wb') as f:
        f.write(png_bytes)
    return len(png_bytes)

def main():
    canvas = Canvas(1024, 1024, (246, 241, 227))

    NAVY = (22, 35, 63)
    GOLD = (232, 184, 75)
    PALE_BLUE = (188, 211, 232)
    WHITE = (255, 255, 255)
    
    # 1. HEADER band y=0..140, solid navy, thin gold rule at y=140..146
    canvas.fill_rect(0, 0, 1024, 140, NAVY)
    canvas.fill_rect(0, 140, 1024, 6, GOLD)
    draw_text(canvas, 512, 28, '19 NOVEMBER 2026', 6, WHITE, 'center')
    draw_text(canvas, 512, 102, 'WORLD NEWS IN ONE IMAGE', 2, GOLD, 'center')

    # 2. HERO panel y=156..356, x=16..1008
    canvas.fill_rect(16, 156, 992, 200, PALE_BLUE)
    # Skyline buildings across back (y=190..316)
    skyline_color = (30, 45, 74)
    buildings = [
        (40, 220, 50, 96), (95, 200, 60, 116), (160, 240, 40, 76),
        (205, 190, 70, 126), (280, 215, 55, 101), (340, 180, 65, 136),
        (410, 230, 50, 86), (465, 205, 75, 111), (545, 195, 60, 121),
        (610, 220, 50, 96), (665, 185, 70, 131), (740, 210, 55, 106),
        (800, 235, 45, 81), (850, 190, 80, 126), (935, 225, 50, 91)
    ]
    for bx, by, bw, bh in buildings:
        canvas.fill_rect(bx, by, bw, bh, skyline_color)
        # lit windows
        for wy in range(by + 8, by + bh - 8, 12):
            for wx in range(bx + 6, bx + bw - 6, 10):
                canvas.fill_rect(wx, wy, 4, 6, (230, 220, 150))

    # Three flag poles & flags at x=250, 512, 774
    for fx in [250, 512, 774]:
        canvas.fill_rect(fx, 180, 3, 136, (100, 100, 100))
    # Flags
    # Flag 1: Red, White, Blue
    canvas.fill_rect(253, 182, 35, 12, (200, 50, 50))
    canvas.fill_rect(253, 194, 35, 12, WHITE)
    canvas.fill_rect(253, 206, 35, 12, (50, 50, 200))
    # Flag 2: Red
    canvas.fill_rect(515, 182, 35, 24, (200, 50, 50))
    # Flag 3: Blue, White, Red
    canvas.fill_rect(777, 182, 35, 12, (50, 50, 200))
    canvas.fill_rect(777, 194, 35, 12, WHITE)
    canvas.fill_rect(777, 206, 35, 12, (200, 50, 50))

    # Table & three suited figures in front (table y=280..316, x=280..744)
    canvas.fill_rect(280, 280, 464, 36, (35, 25, 18))
    # Three seated figures (heads at y=250, bodies at y=265..280)
    for c_x in [350, 512, 674]:
        canvas.fill_circle(c_x, 252, 10, (232, 195, 158)) # head
        canvas.fill_rect(c_x - 16, 262, 32, 18, (25, 30, 45)) # suit

    # Hero caption bar (y=316..356)
    canvas.fill_rect(16, 316, 992, 40, NAVY)
    draw_text(canvas, 512, 322, 'TRUMP, XI AND PUTIN MEET IN SHENZHEN', 2, WHITE, 'center')
    draw_text(canvas, 512, 340, 'PEACE DECLARATION SIGNED - NO MENTION OF UKRAINE OR IRAN', 2, WHITE, 'center')

    # 3. GRID of 4 panels
    # Row 1: y=372..596 (h=224)
    # Row 2: y=612..836 (h=224)
    # Cols: x=16..504 (w=488), x=520..1008 (w=488)

    # Panel A: World Court (Deep purple #3B2E5E)
    canvas.fill_rect(16, 372, 488, 224, (59, 46, 94))
    # Icon on left half (x=16..240, y=372..596): courthouse + scales
    # Courthouse body
    canvas.fill_rect(60, 450, 130, 90, (235, 235, 235))
    # Columns
    for col_x in [75, 95, 115, 135, 155, 175]:
        canvas.fill_rect(col_x, 460, 6, 75, (180, 180, 180))
    # Roof (triangle)
    canvas.fill_polygon([(50, 450), (200, 450), (125, 405)], (210, 210, 210))
    # Scales of justice in front
    canvas.fill_rect(123, 540, 4, 35, GOLD)
    canvas.fill_rect(105, 545, 38, 3, GOLD)
    canvas.fill_circle(105, 555, 6, GOLD)
    canvas.fill_circle(143, 555, 6, GOLD)

    # Panel A Text (x=248..504)
    title_a = wrap_text('WORLD COURT: MYANMAR GUILTY OF GENOCIDE', 20)
    capt_a = wrap_text('ICJ RULES 9-6 ON ROHINGYA', 20)
    draw_text_block(canvas, 252, 410, title_a, 2, WHITE, 'left', 3)
    draw_text_block(canvas, 252, 510, capt_a, 2, GOLD, 'left', 3)

    # Panel B: Hormuz Tankers Hit (Dark teal #14505C)
    canvas.fill_rect(520, 372, 488, 224, (20, 80, 92))
    # Icon on left half (x=520..744): tanker + waves + explosion
    # Waves
    canvas.fill_rect(530, 520, 204, 50, (15, 60, 70))
    canvas.fill_rect(550, 500, 160, 25, (25, 95, 110))
    # Tanker hull
    canvas.fill_rect(560, 480, 130, 32, (60, 60, 60))
    canvas.fill_rect(650, 455, 35, 25, (100, 100, 100)) # bridge
    # Explosion burst at stern
    canvas.fill_circle(685, 470, 16, (255, 120, 0))
    canvas.fill_circle(685, 470, 9, (255, 220, 0))

    # Panel B Text (x=752..1008)
    title_b = wrap_text('HORMUZ TANKERS HIT', 20)
    capt_b = wrap_text('11 CREW HURT, 1 MISSING', 20)
    draw_text_block(canvas, 756, 430, title_b, 2, WHITE, 'left', 3)
    draw_text_block(canvas, 756, 510, capt_b, 2, (249, 232, 162), 'left', 3)

    # Panel C: Boat Sinks off Senegal (Steel blue #2E5E7A)
    canvas.fill_rect(16, 612, 488, 224, (46, 94, 122))
    # Icon on left half (x=16..240): capsizing boat & waves
    canvas.fill_rect(30, 720, 180, 70, (30, 65, 85))
    # Tilted boat hull polygon
    canvas.fill_polygon([(70, 730), (140, 700), (160, 730), (90, 750)], (130, 85, 40))
    # White wave caps
    canvas.fill_circle(60, 715, 8, WHITE)
    canvas.fill_circle(110, 695, 10, WHITE)
    canvas.fill_circle(170, 720, 8, WHITE)

    # Panel C Text (x=248..504)
    title_c = wrap_text('BOAT SINKS OFF SENEGAL', 20)
    capt_c = wrap_text('DOZENS MISSING OF 100 ABOARD', 20)
    draw_text_block(canvas, 252, 670, title_c, 2, WHITE, 'left', 3)
    draw_text_block(canvas, 252, 750, capt_c, 2, (249, 232, 162), 'left', 3)

    # Panel D: Mongolia President Quits (Deep red #8C2B2B)
    canvas.fill_rect(520, 612, 488, 224, (140, 43, 43))
    # Icon on left half (x=520..744): parliament building + dome + chair
    canvas.fill_rect(560, 700, 100, 90, (180, 70, 70))
    # Dome
    canvas.fill_circle(610, 700, 24, (200, 90, 90))
    canvas.fill_rect(608, 665, 4, 15, WHITE) # flag pole
    canvas.fill_rect(612, 665, 14, 8, (232, 184, 75)) # flag
    # Empty chair beside it
    canvas.fill_rect(680, 730, 22, 35, (100, 30, 30))
    canvas.fill_rect(676, 725, 30, 6, (100, 30, 30))

    # Panel D Text (x=752..1008)
    title_d = wrap_text('MONGOLIA PRESIDENT QUITS', 20)
    capt_d = wrap_text('PARLIAMENT ACCEPTS EXIT', 20)
    draw_text_block(canvas, 756, 670, title_d, 2, WHITE, 'left', 3)
    draw_text_block(canvas, 756, 750, capt_d, 2, GOLD, 'left', 3)

    # 4. FOOTER band y=852..1008, solid navy
    canvas.fill_rect(0, 852, 1024, 156, NAVY)
    draw_text(canvas, 32, 868, 'ALSO TODAY:', 2, GOLD, 'left')
    draw_text(canvas, 32, 906, 'US SENATE REJECTS IRAN WAR POWERS VOTE 51-48', 2, WHITE, 'left')
    draw_text(canvas, 32, 941, 'RUSSIAN STRIKE ON ODESA KILLS 4, WOUNDS 13', 2, WHITE, 'left')
    draw_text(canvas, 32, 976, 'NORTH KOREA EXPANDS URANIUM SITE - GTA VI LAUNCHES', 2, WHITE, 'left')

    out_dir = os.environ.get('MAKEFUN_OUTPUT_DIR', '/output')
    out_path = os.path.join(out_dir, 'entry.png')
    size = encode_png(canvas.buf, canvas.w, canvas.h, out_path)
    print(f"Output path: {out_path}")
    print(f"Byte size: {size}")

if __name__ == '__main__':
    main()
