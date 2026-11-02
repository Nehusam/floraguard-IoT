import sys
import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

def create_deck(filename="FloraGuard_IoT_Presentation.pptx"):
    prs = Presentation()
    # 16:9 Widescreen dimensions
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    blank_layout = prs.slide_layouts[6]

    # Clean Modern Color Palette
    PRIMARY = RGBColor(26, 92, 46)        # Deep Forest Green (#1A5C2E)
    SECONDARY = RGBColor(45, 138, 78)     # Fresh Green (#2D8A4E)
    ACCENT = RGBColor(245, 158, 11)       # Amber Gold (#F59E0B)
    DARK = RGBColor(26, 32, 44)           # Charcoal / Slate (#1A202C)
    MUTED = RGBColor(100, 116, 139)       # Muted Slate (#64748B)
    LIGHT_BG = RGBColor(248, 250, 252)    # Off-white / light slate (#F8FAFC)
    WHITE = RGBColor(255, 255, 255)
    CARD_BORDER = RGBColor(226, 232, 240)
    BOX_BG = RGBColor(241, 245, 249)

    def add_header(slide, title_text, category="FLORAGUARD IOT"):
        # Header category
        cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.45), Inches(11.5), Inches(0.35))
        tf_c = cat_box.text_frame
        tf_c.word_wrap = True
        tf_c.margin_left = tf_c.margin_right = tf_c.margin_top = tf_c.margin_bottom = 0
        p_c = tf_c.paragraphs[0]
        p_c.text = category.upper()
        p_c.font.size = Pt(10)
        p_c.font.bold = True
        p_c.font.color.rgb = SECONDARY

        # Main Title
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.75), Inches(11.5), Inches(0.65))
        tf_t = title_box.text_frame
        tf_t.word_wrap = True
        tf_t.margin_left = tf_t.margin_right = tf_t.margin_top = tf_t.margin_bottom = 0
        p_t = tf_t.paragraphs[0]
        p_t.text = title_text
        p_t.font.size = Pt(22)
        p_t.font.bold = True
        p_t.font.color.rgb = DARK

        # Subtle divider rule
        divider = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.45), Inches(11.733), Inches(0.02))
        divider.fill.solid()
        divider.fill.fore_color.rgb = CARD_BORDER
        divider.line.fill.background()

    def add_card(slide, left, top, width, height, bg_color=WHITE, border_color=CARD_BORDER):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = bg_color
        if border_color:
            card.line.color.rgb = border_color
            card.line.width = Pt(1)
        else:
            card.line.fill.background()
        return card

    # ==========================================================
    # SLIDE 0: TITLE SLIDE
    # ==========================================================
    s0 = prs.slides.add_slide(blank_layout)
    # Background
    bg0 = s0.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg0.fill.solid()
    bg0.fill.fore_color.rgb = LIGHT_BG
    bg0.line.fill.background()

    # Accent top border
    bar0 = s0.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(0.12))
    bar0.fill.solid()
    bar0.fill.fore_color.rgb = PRIMARY
    bar0.line.fill.background()

    # Title Card container
    add_card(s0, Inches(1.2), Inches(1.2), Inches(10.933), Inches(5.1), WHITE, CARD_BORDER)

    # Pill badge
    pill = s0.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.8), Inches(1.8), Inches(2.2), Inches(0.4))
    pill.fill.solid()
    pill.fill.fore_color.rgb = RGBColor(230, 245, 235)
    pill.line.fill.background()
    p_tf = pill.text_frame
    p_p = p_tf.paragraphs[0]
    p_p.text = "SMART AGRICULTURE IoT"
    p_p.alignment = PP_ALIGN.CENTER
    p_p.font.size = Pt(10)
    p_p.font.bold = True
    p_p.font.color.rgb = PRIMARY

    # Title text
    t_box = s0.shapes.add_textbox(Inches(1.8), Inches(2.4), Inches(9.8), Inches(1.8))
    t_tf = t_box.text_frame
    t_tf.word_wrap = True
    p1 = t_tf.paragraphs[0]
    p1.text = "FloraGuard IoT"
    p1.font.size = Pt(36)
    p1.font.bold = True
    p1.font.color.rgb = PRIMARY

    p2 = t_tf.add_paragraph()
    p2.text = "Plant Disease Detection & Microclimate Early Warning System"
    p2.font.size = Pt(20)
    p2.font.color.rgb = DARK
    p2.space_before = Pt(8)

    p3 = t_tf.add_paragraph()
    p3.text = "Real-time edge sensing (ESP32), Mills Period infection modeling, SQLite persistence & cloud dashboard"
    p3.font.size = Pt(13)
    p3.font.color.rgb = MUTED
    p3.space_before = Pt(6)

    # Meta footer inside card
    meta_box = s0.shapes.add_textbox(Inches(1.8), Inches(4.7), Inches(9.8), Inches(1.1))
    m_tf = meta_box.text_frame
    m_p1 = m_tf.paragraphs[0]
    m_p1.text = "Course: 24MCAT213 - Internet of Things  |  Department of Computer Applications"
    m_p1.font.size = Pt(11)
    m_p1.font.bold = True
    m_p1.font.color.rgb = DARK

    m_p2 = m_tf.add_paragraph()
    m_p2.text = "Amal Jyothi College of Engineering, Kanjirappally  |  MCA (2025–2027)"
    m_p2.font.size = Pt(11)
    m_p2.font.color.rgb = MUTED
    m_p2.space_before = Pt(4)

    # ==========================================================
    # SLIDE 1: INTRODUCTION - PAGE 1 (Problem & Significance)
    # ==========================================================
    s1 = prs.slides.add_slide(blank_layout)
    add_header(s1, "Introduction: Agricultural Challenges & Problem Statement", "01 / INTRODUCTION (PAGE 1 OF 2)")

    # Left Card: Traditional Farming Bottlenecks
    add_card(s1, Inches(0.8), Inches(1.75), Inches(5.6), Inches(5.1))
    h_box1 = s1.shapes.add_textbox(Inches(1.1), Inches(2.0), Inches(5.0), Inches(0.5))
    h_tf1 = h_box1.text_frame
    hp1 = h_tf1.paragraphs[0]
    hp1.text = "The Problem in Traditional Farming"
    hp1.font.size = Pt(16)
    hp1.font.bold = True
    hp1.font.color.rgb = PRIMARY

    b_box1 = s1.shapes.add_textbox(Inches(1.1), Inches(2.6), Inches(5.0), Inches(4.0))
    btf1 = b_box1.text_frame
    btf1.word_wrap = True

    points_s1_left = [
        ("Crop Loss Vulnerability:", " Fungal pathogens (e.g. Late Blight, Downy Mildew) cause devastating agricultural crop yield losses worldwide."),
        ("Delayed Manual Scouting:", " Conventional disease monitoring relies on visual human inspection. By the time lesions appear on leaves, the infection is already established."),
        ("Microclimate Blindness:", " Regional weather forecasts lack canopy-level precision regarding micro-humidity, soil saturation, and foliar moisture films."),
        ("Excess Chemical Sprays:", " Without predictive warnings, farmers overuse chemical fungicides reactively, leading to soil toxicity and high input costs.")
    ]
    for idx, (head, desc) in enumerate(points_s1_left):
        p = btf1.paragraphs[0] if idx == 0 else btf1.add_paragraph()
        run1 = p.add_run()
        run1.text = "• " + head
        run1.font.bold = True
        run1.font.size = Pt(12)
        run1.font.color.rgb = DARK
        run2 = p.add_run()
        run2.text = desc
        run2.font.size = Pt(11.5)
        run2.font.color.rgb = MUTED
        p.space_after = Pt(10)

    # Right Card: The Need for an IoT-Driven Paradigm
    add_card(s1, Inches(6.9), Inches(1.75), Inches(5.6), Inches(5.1))
    h_box2 = s1.shapes.add_textbox(Inches(7.2), Inches(2.0), Inches(5.0), Inches(0.5))
    h_tf2 = h_box2.text_frame
    hp2 = h_tf2.paragraphs[0]
    hp2.text = "The Opportunity with IoT & Edge Telemetry"
    hp2.font.size = Pt(16)
    hp2.font.bold = True
    hp2.font.color.rgb = SECONDARY

    b_box2 = s1.shapes.add_textbox(Inches(7.2), Inches(2.6), Inches(5.0), Inches(4.0))
    btf2 = b_box2.text_frame
    btf2.word_wrap = True

    points_s1_right = [
        ("Pre-Symptomatic Detection:", " Pathogen viability correlates strictly with prolonged moisture and warm canopy temperatures before tissue decay occurs."),
        ("Continuous 24/7 Monitoring:", " Low-cost physical sensors allow uninterrupted canopy telemetry without requiring physical presence in the field."),
        ("Evidence-Based Interventions:", " Early warnings give growers actionable advice (e.g., increase ventilation, delay sprinkler cycles) during early incubation."),
        ("Scalable Cloud Architecture:", " Centralized dashboards enable multi-plot monitoring from any desktop or mobile device over the Internet.")
    ]
    for idx, (head, desc) in enumerate(points_s1_right):
        p = btf2.paragraphs[0] if idx == 0 else btf2.add_paragraph()
        run1 = p.add_run()
        run1.text = "• " + head
        run1.font.bold = True
        run1.font.size = Pt(12)
        run1.font.color.rgb = DARK
        run2 = p.add_run()
        run2.text = desc
        run2.font.size = Pt(11.5)
        run2.font.color.rgb = MUTED
        p.space_after = Pt(10)

    # ==========================================================
    # SLIDE 2: INTRODUCTION - PAGE 2 (Proposed Solution & Objectives)
    # ==========================================================
    s2 = prs.slides.add_slide(blank_layout)
    add_header(s2, "Introduction: FloraGuard IoT Solution & Objectives", "01 / INTRODUCTION (PAGE 2 OF 2)")

    # Top Full-width Banner Card: What FloraGuard Does
    add_card(s2, Inches(0.8), Inches(1.75), Inches(11.733), Inches(1.5), RGBColor(240, 248, 243), RGBColor(180, 220, 195))
    b_top = s2.shapes.add_textbox(Inches(1.1), Inches(1.9), Inches(11.1), Inches(1.2))
    btf_top = b_top.text_frame
    btf_top.word_wrap = True
    p_t1 = btf_top.paragraphs[0]
    p_t1.text = "What is FloraGuard IoT?"
    p_t1.font.size = Pt(14)
    p_t1.font.bold = True
    p_t1.font.color.rgb = PRIMARY

    p_t2 = btf_top.add_paragraph()
    p_t2.text = "FloraGuard IoT is an automated precision farming system combining physical microclimate sensing (ESP32) with a containerized FastAPI backend and real-time botanical dashboard. It continuously measures air temperature, humidity, soil moisture, and leaf wetness to evaluate disease risks before visible damage strikes."
    p_t2.font.size = Pt(11.5)
    p_t2.font.color.rgb = DARK
    p_t2.space_before = Pt(4)

    # 3 Column Objective Cards
    col_w = Inches(3.64)
    gap = Inches(0.4)
    left_start = Inches(0.8)
    top_cols = Inches(3.55)
    height_cols = Inches(3.3)

    obj_cards = [
        ("01. Edge Telemetry", PRIMARY, [
            "Sample DHT11 digital temperature & relative humidity.",
            "Acquire 12-bit analog soil volumetric moisture (0–100%).",
            "Monitor foliar leaf wetness / rain grid precipitation.",
            "10-sample moving average filter to reject ADC noise."
        ]),
        ("02. Risk Engine & DB", SECONDARY, [
            "Compute 0–100 Disease Risk Index via Mills Period model.",
            "Assess Late Blight, Mildew, and Botrytis germination zones.",
            "Persist all readings in SQLite3 database (floraguard.db).",
            "Full audit logging with HARDWARE source verification."
        ]),
        ("03. Live Visual Platform", ACCENT, [
            "Dual-channel updates: WebSockets + 3s polling fallback.",
            "Dynamic charts for atmospheric and hydrological trends.",
            "Instant agronomic remediation alerts for farm operators.",
            "Cloud-hosted on Render via Docker for global access."
        ])
    ]

    for i, (ctitle, ccolor, clist) in enumerate(obj_cards):
        cx = left_start + i * (col_w + gap)
        add_card(s2, cx, top_cols, col_w, height_cols)

        # Card Title
        tb = s2.shapes.add_textbox(cx + Inches(0.25), top_cols + Inches(0.25), col_w - Inches(0.5), Inches(0.5))
        tf = tb.text_frame
        p = tf.paragraphs[0]
        p.text = ctitle
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = ccolor

        # Card List
        tb_l = s2.shapes.add_textbox(cx + Inches(0.25), top_cols + Inches(0.75), col_w - Inches(0.5), height_cols - Inches(0.9))
        tf_l = tb_l.text_frame
        tf_l.word_wrap = True
        for j, item in enumerate(clist):
            pl = tf_l.paragraphs[0] if j == 0 else tf_l.add_paragraph()
            pl.text = "• " + item
            pl.font.size = Pt(10.5)
            pl.font.color.rgb = DARK
            pl.space_after = Pt(6)

    # ==========================================================
    # SLIDE 3: HARDWARE & SOFTWARE COMPONENTS
    # ==========================================================
    s3 = prs.slides.add_slide(blank_layout)
    add_header(s3, "System Components: Hardware & Software Stack", "02 / COMPONENTS")

    # Left Column: Hardware Table & Details
    add_card(s3, Inches(0.8), Inches(1.75), Inches(6.8), Inches(5.1))
    hw_tb = s3.shapes.add_textbox(Inches(1.1), Inches(1.95), Inches(6.2), Inches(0.4))
    hwp = hw_tb.text_frame.paragraphs[0]
    hwp.text = "Hardware Components & Interfacing Pinout"
    hwp.font.size = Pt(15)
    hwp.font.bold = True
    hwp.font.color.rgb = PRIMARY

    # Hardware Table
    rows = 6
    cols = 4
    left = Inches(1.1)
    top = Inches(2.45)
    width = Inches(6.2)
    height = Inches(2.6)

    table_shape = s3.shapes.add_table(rows, cols, left, top, width, height)
    tbl = table_shape.table
    tbl.columns[0].width = Inches(1.7)
    tbl.columns[1].width = Inches(1.5)
    tbl.columns[2].width = Inches(1.3)
    tbl.columns[3].width = Inches(1.7)

    headers = ["Component", "Function", "ESP32 Pin", "Signal / Voltage"]
    for c_idx, h in enumerate(headers):
        cell = tbl.cell(0, c_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = PRIMARY
        p = cell.text_frame.paragraphs[0]
        p.text = h
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = WHITE
        p.alignment = PP_ALIGN.CENTER

    data_hw = [
        ("ESP32 DevKit V1", "Dual-Core 240MHz + Wi-Fi", "Core Node", "3.3V System Logic"),
        ("DHT11 Sensor", "Air Temp & Humidity", "GPIO 4", "1-Wire Digital (3.3V)"),
        ("Capacitive Soil v1.2", "Volumetric Soil Moisture", "GPIO 35", "ADC1_CH7 Analog (3.3V)"),
        ("Rain Sensor Grid", "Precipitation / Leaf Film", "GPIO 34", "ADC1_CH6 Analog (3.3V)"),
        ("Status LED", "Tx Heartbeat Indicator", "GPIO 2", "Digital Output (3.3V)")
    ]
    for r_idx, row in enumerate(data_hw):
        for c_idx, val in enumerate(row):
            cell = tbl.cell(r_idx + 1, c_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = WHITE if r_idx % 2 == 0 else LIGHT_BG
            p = cell.text_frame.paragraphs[0]
            p.text = val
            p.font.size = Pt(9.5)
            p.font.color.rgb = DARK
            if c_idx == 2:
                p.font.bold = True
                p.alignment = PP_ALIGN.CENTER

    # Additional hardware note
    hw_note = s3.shapes.add_textbox(Inches(1.1), Inches(5.2), Inches(6.2), Inches(1.4))
    hwn_tf = hw_note.text_frame
    hwn_tf.word_wrap = True
    np1 = hwn_tf.paragraphs[0]
    np1.text = "Key Hardware Characteristics:"
    np1.font.size = Pt(11)
    np1.font.bold = True
    np1.font.color.rgb = DARK

    np2 = hwn_tf.add_paragraph()
    np2.text = "• Capacitive probe resists soil electrolysis corrosion compared to resistive probes.\n• 12-bit SAR ADC with 10-sample moving average filter removes ambient electrical jitter.\n• WiFiClientSecure handles HTTPS transmission directly to Render cloud."
    np2.font.size = Pt(10)
    np2.font.color.rgb = MUTED
    np2.space_before = Pt(3)

    # Right Column: Software Stack
    add_card(s3, Inches(7.9), Inches(1.75), Inches(4.633), Inches(5.1))
    sw_tb = s3.shapes.add_textbox(Inches(8.2), Inches(1.95), Inches(4.0), Inches(0.4))
    swp = sw_tb.text_frame.paragraphs[0]
    swp.text = "Software Architecture Stack"
    swp.font.size = Pt(15)
    swp.font.bold = True
    swp.font.color.rgb = SECONDARY

    sw_items = [
        ("Embedded Firmware (C++/Arduino):", "FreeRTOS single-thread loop, analog moving average, ArduinoJson serialization, WiFiClientSecure HTTP POST."),
        ("FastAPI Backend (Python 3.11):", "Asynchronous high-throughput ASGI server handling REST endpoints (/api/telemetry) and WebSocket streaming."),
        ("Relational Database (SQLite3):", "Persistent storage in floraguard.db table sensor_telemetry. Audited >900 real hardware records."),
        ("Dashboard (HTML5/Tailwind/JS):", "Clean responsive UI with Chart.js line graphs, Lucide icons, and zero-polling WebSockets."),
        ("Docker Containerization:", "Lightweight Linux container deployed on Render.com with persistent volume for zero-downtime execution.")
    ]
    sw_desc = s3.shapes.add_textbox(Inches(8.2), Inches(2.45), Inches(4.033), Inches(4.2))
    sw_tf = sw_desc.text_frame
    sw_tf.word_wrap = True
    for idx, (sh, sd) in enumerate(sw_items):
        p = sw_tf.paragraphs[0] if idx == 0 else sw_tf.add_paragraph()
        r1 = p.add_run()
        r1.text = "• " + sh
        r1.font.bold = True
        r1.font.size = Pt(11)
        r1.font.color.rgb = DARK
        r2 = p.add_run()
        r2.text = " " + sd
        r2.font.size = Pt(10)
        r2.font.color.rgb = MUTED
        p.space_after = Pt(7)

    # ==========================================================
    # SLIDE 4: BLOCK DIAGRAM & DATA FLOW
    # ==========================================================
    s4 = prs.slides.add_slide(blank_layout)
    add_header(s4, "System Block Diagram & End-to-End Data Flow", "03 / BLOCK DIAGRAM")

    # Main Canvas Card
    add_card(s4, Inches(0.8), Inches(1.75), Inches(11.733), Inches(5.1))

    # 4 Architecture Stages as distinct visual blocks
    b_width = Inches(2.4)
    b_height = Inches(3.9)
    b_top = Inches(2.4)
    b_gap = Inches(0.55)
    b_left = Inches(1.15)

    blocks = [
        ("LAYER 1", "SENSING NODE", PRIMARY, [
            "DHT11 Sensor\n(Air Temp & RH)",
            "Capacitive Probe\n(Volumetric Soil %)",
            "Rain Grid\n(Leaf Wetness %)",
            "Power Supply\n(3.3V / 5V DC)"
        ]),
        ("LAYER 2", "EDGE CONTROLLER", SECONDARY, [
            "ESP32 DevKit\n(Xtensa Dual-Core)",
            "10-Sample Moving\nAverage Filter",
            "ArduinoJson\nPacket Serialization",
            "Wi-Fi Client\n(HTTPS ClientSecure)"
        ]),
        ("LAYER 3", "CLOUD BACKEND", RGBColor(15, 118, 110), [
            "FastAPI Python\nREST /api/telemetry",
            "Mills Period Risk\nScoring Engine",
            "SQLite3 Relational DB\n(sensor_telemetry)",
            "Docker on Render\n(Auto CI/CD)"
        ]),
        ("LAYER 4", "USER INTERFACE", ACCENT, [
            "WebSocket Broadcast\n(/ws/telemetry)",
            "3s Poll Fallback\n(/api/telemetry/latest)",
            "Dual Rolling Charts\n(Chart.js Analytics)",
            "Dedicated DB Viewer\n(/database Route)"
        ])
    ]

    for idx, (tag, title, color, sub_items) in enumerate(blocks):
        bx = b_left + idx * (b_width + b_gap)
        # Block Card
        add_card(s4, bx, b_top, b_width, b_height, RGBColor(250, 250, 252), CARD_BORDER)

        # Header Pill
        hp = s4.shapes.add_shape(MSO_SHAPE.RECTANGLE, bx, b_top, b_width, Inches(0.65))
        hp.fill.solid()
        hp.fill.fore_color.rgb = color
        hp.line.fill.background()

        hptf = hp.text_frame
        p_tag = hptf.paragraphs[0]
        p_tag.text = tag
        p_tag.font.size = Pt(8.5)
        p_tag.font.bold = True
        p_tag.font.color.rgb = RGBColor(230, 245, 235) if color != ACCENT else RGBColor(100, 60, 0)
        p_tag.alignment = PP_ALIGN.CENTER

        p_tit = hptf.add_paragraph()
        p_tit.text = title
        p_tit.font.size = Pt(11)
        p_tit.font.bold = True
        p_tit.font.color.rgb = WHITE
        p_tit.alignment = PP_ALIGN.CENTER

        # Sub items inside block
        item_y = b_top + Inches(0.85)
        item_h = Inches(0.65)
        for sidx, item in enumerate(sub_items):
            iy = item_y + sidx * (item_h + Inches(0.08))
            sub_card = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, bx + Inches(0.15), iy, b_width - Inches(0.3), item_h)
            sub_card.fill.solid()
            sub_card.fill.fore_color.rgb = WHITE
            sub_card.line.color.rgb = CARD_BORDER
            sub_card.line.width = Pt(0.75)

            sc_tf = sub_card.text_frame
            sc_tf.word_wrap = True
            sc_p = sc_tf.paragraphs[0]
            sc_p.text = item
            sc_p.font.size = Pt(9.5)
            sc_p.font.bold = True
            sc_p.font.color.rgb = DARK
            sc_p.alignment = PP_ALIGN.CENTER

        # Connective arrows between stages
        if idx < 3:
            arrow_x = bx + b_width + Inches(0.1)
            arrow_y = b_top + Inches(1.8)
            arr = s4.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, arrow_x, arrow_y, Inches(0.35), Inches(0.3))
            arr.fill.solid()
            arr.fill.fore_color.rgb = MUTED
            arr.line.fill.background()

    # Flow summary text banner below
    f_bar = s4.shapes.add_textbox(Inches(1.2), Inches(6.45), Inches(10.933), Inches(0.35))
    f_tf = f_bar.text_frame
    fp = f_tf.paragraphs[0]
    fp.text = "Data Flow:  [Sensors] ──(ADC/Digital)──> [ESP32] ──(HTTPS/JSON)──> [FastAPI Cloud & SQLite] ──(WebSockets)──> [Botanical Dashboard]"
    fp.font.size = Pt(10)
    fp.font.bold = True
    fp.font.color.rgb = PRIMARY
    fp.alignment = PP_ALIGN.CENTER

    # ==========================================================
    # SLIDE 5: WORKING PRINCIPLE - PAGE 1 (Edge to Cloud Acquisition)
    # ==========================================================
    s5 = prs.slides.add_slide(blank_layout)
    add_header(s5, "Working Principle: Sensor Acquisition & Edge Telemetry", "04 / WORKING (PAGE 1 OF 2)")

    # 3 Sequential Step Cards
    step_w = Inches(3.64)
    step_gap = Inches(0.4)
    s_top = Inches(1.75)
    s_h = Inches(5.1)

    steps_p1 = [
        ("Step 1: Signal Sampling & Noise Filtering", PRIMARY, [
            ("3-Second Cycle:", "Every 3,000 ms, the ESP32 initiates synchronous sensor sampling."),
            ("DHT11 Digital Read:", "One-wire protocol samples ambient air temperature (°C) and relative humidity (%)."),
            ("10-Sample Moving Average:", "The 12-bit ADC reads 10 consecutive analog conversions for soil moisture (GPIO 35) and rain wetness (GPIO 34)."),
            ("Electrical Noise Rejection:", "Averaging eliminates inductive transients and fluctuating ADC readings from long jumper leads.")
        ]),
        ("Step 2: Voltage Calibration & JSON Packaging", SECONDARY, [
            ("Moisture Calibration:", "ADC integer counts (0–4095) map onto calibrated 0.0% to 100.0% moisture percentages."),
            ("Inverted Rain Sensitivity:", "Low wetness voltage is inverted so 0% = dry foliage, 100% = heavy saturation / rainfall."),
            ("ArduinoJson Document:", "Packaged into standard payload: device_id, temperature, humidity, soil_moisture, rain_intensity, source."),
            ("Status LED Flash:", "GPIO 2 triggers a brief blue LED heartbeat verifying active packet construction.")
        ]),
        ("Step 3: HTTPS Dispatch to FastAPI Cloud", RGBColor(15, 118, 110), [
            ("WiFiClientSecure Layer:", "ESP32 creates a TLS/HTTPS connection directly to the public Render domain."),
            ("HTTP POST Ingestion:", "Dispatched to https://floraguard-iot.onrender.com/api/telemetry."),
            ("Zero Cloud Division Protection:", "Firmware checks Wi-Fi connectivity state and safely retries if connection drops."),
            ("HTTP 200 Handshake:", "FastAPI acknowledges receipt and returns computed pathogen indices back in response body.")
        ])
    ]

    for i, (title, color, items) in enumerate(steps_p1):
        sx = Inches(0.8) + i * (step_w + step_gap)
        add_card(s5, sx, s_top, step_w, s_h)

        # Header box
        hb = s5.shapes.add_textbox(sx + Inches(0.25), s_top + Inches(0.25), step_w - Inches(0.5), Inches(0.65))
        hp = hb.text_frame.paragraphs[0]
        hp.text = title
        hp.font.size = Pt(13)
        hp.font.bold = True
        hp.font.color.rgb = color

        # Content
        cb = s5.shapes.add_textbox(sx + Inches(0.25), s_top + Inches(0.95), step_w - Inches(0.5), s_h - Inches(1.1))
        ctf = cb.text_frame
        ctf.word_wrap = True
        for j, (ih, idesc) in enumerate(items):
            p = ctf.paragraphs[0] if j == 0 else ctf.add_paragraph()
            r1 = p.add_run()
            r1.text = "• " + ih
            r1.font.bold = True
            r1.font.size = Pt(10.5)
            r1.font.color.rgb = DARK
            r2 = p.add_run()
            r2.text = " " + idesc
            r2.font.size = Pt(10)
            r2.font.color.rgb = MUTED
            p.space_after = Pt(8)

    # ==========================================================
    # SLIDE 6: WORKING PRINCIPLE - PAGE 2 (Mills Period Risk & Dashboard)
    # ==========================================================
    s6 = prs.slides.add_slide(blank_layout)
    add_header(s6, "Working Principle: Mills Period Infection Model & UI", "04 / WORKING (PAGE 2 OF 2)")

    # Left Card: Disease Risk Engine
    add_card(s6, Inches(0.8), Inches(1.75), Inches(5.6), Inches(5.1))
    e_tb = s6.shapes.add_textbox(Inches(1.1), Inches(2.0), Inches(5.0), Inches(0.5))
    ep = e_tb.text_frame.paragraphs[0]
    ep.text = "Mills Period Pathogen Risk Calculation"
    ep.font.size = Pt(15)
    ep.font.bold = True
    ep.font.color.rgb = PRIMARY

    e_desc = s6.shapes.add_textbox(Inches(1.1), Inches(2.55), Inches(5.0), Inches(4.1))
    etf = e_desc.text_frame
    etf.word_wrap = True

    model_points = [
        ("Mills Period Baseline:", "Fungal spores (Phytophthora, Downy Mildew) require specific leaf surface moisture duration and temperature to germinate."),
        ("Leaf Wetness Factor (45% Weight):", "Foliar water films >70% strongly accelerate spore penetration through plant stomata."),
        ("Relative Humidity (35% Weight):", "Canopy RH >80% prevents evaporative spore desiccation and fosters mycelium growth."),
        ("Optimal Temperature Window (20% Weight):", "Temperatures between 18°C and 28°C provide peak metabolic incubation conditions."),
        ("Risk Classification Output:", "0–40: LOW (Optimal Microclimate)\n41–70: MODERATE (Elevated Mildew Risk)\n71–100: HIGH (Critical Late Blight Alert)")
    ]
    for idx, (mh, md) in enumerate(model_points):
        p = etf.paragraphs[0] if idx == 0 else etf.add_paragraph()
        r1 = p.add_run()
        r1.text = "• " + mh
        r1.font.bold = True
        r1.font.size = Pt(11)
        r1.font.color.rgb = DARK
        r2 = p.add_run()
        r2.text = " " + md
        r2.font.size = Pt(10)
        r2.font.color.rgb = MUTED
        p.space_after = Pt(7)

    # Right Card: Live Dashboard & Database Persistence
    add_card(s6, Inches(6.9), Inches(1.75), Inches(5.6), Inches(5.1))
    d_tb = s6.shapes.add_textbox(Inches(7.2), Inches(2.0), Inches(5.0), Inches(0.5))
    dp = d_tb.text_frame.paragraphs[0]
    dp.text = "Database Persistence & Live Dashboard"
    dp.font.size = Pt(15)
    dp.font.bold = True
    dp.font.color.rgb = SECONDARY

    d_desc = s6.shapes.add_textbox(Inches(7.2), Inches(2.55), Inches(5.0), Inches(4.1))
    dtf = d_desc.text_frame
    dtf.word_wrap = True

    dash_points = [
        ("SQLite3 Persistence:", "Every reading is committed to floraguard.db table sensor_telemetry with device ID, timestamps, and risk level."),
        ("Zero-Polling WebSockets:", "Live packets are pushed via /ws/telemetry instantly to all connected browser sessions."),
        ("3-Second Auto-Sync Loop:", "Client-side fallback fetches /api/telemetry/latest every 3 seconds to guarantee real-time sync across cloud proxies."),
        ("Dual Interactive Line Charts:", "Chart 1 tracks Atmospheric trends (Temp vs Humidity); Chart 2 tracks Hydrological balance (Soil vs Rain)."),
        ("Dedicated DB Presentation Page:", "Accessible at /database with audit counters (900+ real readings), filters, and color-coded risk tags.")
    ]
    for idx, (dh, dd) in enumerate(dash_points):
        p = dtf.paragraphs[0] if idx == 0 else dtf.add_paragraph()
        r1 = p.add_run()
        r1.text = "• " + dh
        r1.font.bold = True
        r1.font.size = Pt(11)
        r1.font.color.rgb = DARK
        r2 = p.add_run()
        r2.text = " " + dd
        r2.font.size = Pt(10)
        r2.font.color.rgb = MUTED
        p.space_after = Pt(7)

    # ==========================================================
    # SLIDE 7: CONCLUSION & FUTURE ENHANCEMENTS
    # ==========================================================
    s7 = prs.slides.add_slide(blank_layout)
    add_header(s7, "Conclusion & Future Enhancements", "05 / CONCLUSION")

    # Left Column: Project Outcomes & Achievements
    add_card(s7, Inches(0.8), Inches(1.75), Inches(5.6), Inches(5.1))
    c_tb = s7.shapes.add_textbox(Inches(1.1), Inches(2.0), Inches(5.0), Inches(0.5))
    cp = c_tb.text_frame.paragraphs[0]
    cp.text = "Project Outcomes & Achievements"
    cp.font.size = Pt(15)
    cp.font.bold = True
    cp.font.color.rgb = PRIMARY

    c_desc = s7.shapes.add_textbox(Inches(1.1), Inches(2.6), Inches(5.0), Inches(4.0))
    ctf = c_desc.text_frame
    ctf.word_wrap = True

    concl_points = [
        ("Complete Assignment Fulfillment:", "Successfully demonstrated physical multi-sensor interfacing on ESP32, wireless communication, Docker containerization, SQLite database persistence, and a real-time web dashboard."),
        ("High-Reliability Hardware Ingestion:", "Recorded >900 real hardware telemetry rows from ESP32 with zero dropped packets under live Wi-Fi."),
        ("Public Cloud Deployment:", "Operational 24/7 on Render.com (https://floraguard-iot.onrender.com) using Docker."),
        ("Actionable Farmer Guidance:", "Transforms raw microclimate numbers into clear preventative agronomic advisories (Low/Moderate/High).")
    ]
    for idx, (ch, cd) in enumerate(concl_points):
        p = ctf.paragraphs[0] if idx == 0 else ctf.add_paragraph()
        r1 = p.add_run()
        r1.text = "• " + ch
        r1.font.bold = True
        r1.font.size = Pt(11.5)
        r1.font.color.rgb = DARK
        r2 = p.add_run()
        r2.text = " " + cd
        r2.font.size = Pt(10.5)
        r2.font.color.rgb = MUTED
        p.space_after = Pt(10)

    # Right Column: Future Roadmap
    add_card(s7, Inches(6.9), Inches(1.75), Inches(5.6), Inches(5.1))
    f_tb = s7.shapes.add_textbox(Inches(7.2), Inches(2.0), Inches(5.0), Inches(0.5))
    fp_h = f_tb.text_frame.paragraphs[0]
    fp_h.text = "Future Technical Enhancements"
    fp_h.font.size = Pt(15)
    fp_h.font.bold = True
    fp_h.font.color.rgb = SECONDARY

    f_desc = s7.shapes.add_textbox(Inches(7.2), Inches(2.6), Inches(5.0), Inches(4.0))
    ftf = f_desc.text_frame
    ftf.word_wrap = True

    future_points = [
        ("Automated Actuator Relays:", "Interface relay modules to trigger misting systems, exhaust fans, or solenoid irrigation valves when thresholds breach."),
        ("GSM / SMS Push Alerts:", "Direct SMS alerts to farmers' basic mobile phones in rural regions without smartphone connectivity."),
        ("LoRaWAN Long-Range Mesh:", "Expand coverage across expansive farm acreage without requiring individual Wi-Fi routers."),
        ("Solar Harvesting Unit:", "Add small PV panel and Li-ion battery charging for 100% off-grid outdoor farm deployment.")
    ]
    for idx, (fh, fd) in enumerate(future_points):
        p = ftf.paragraphs[0] if idx == 0 else ftf.add_paragraph()
        r1 = p.add_run()
        r1.text = "• " + fh
        r1.font.bold = True
        r1.font.size = Pt(11.5)
        r1.font.color.rgb = DARK
        r2 = p.add_run()
        r2.text = " " + fd
        r2.font.size = Pt(10.5)
        r2.font.color.rgb = MUTED
        p.space_after = Pt(10)

    prs.save(filename)
    print(f"Presentation saved successfully: {filename}")

if __name__ == "__main__":
    create_deck()
