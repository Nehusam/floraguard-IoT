import sys
import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.black)
        
        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, 842 - 36, "FloraGuard IoT — Project & Combined Assignment Report")
            self.setStrokeColor(colors.black)
            self.setLineWidth(0.5)
            self.line(54, 842 - 42, 595 - 54, 842 - 42)
            
        # Footer
        footer_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(595 - 54, 36, footer_text)
        self.drawString(54, 36, "Amal Jyothi College of Engineering • Dept. of Computer Applications • 24MCAT213")
        self.setStrokeColor(colors.black)
        self.setLineWidth(0.5)
        self.line(54, 46, 595 - 54, 46)
        self.restoreState()

def build_pdf(filename="FloraGuard_IoT_Project_Report.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Monochrome Palette (Pure Black, White, Grays)
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.black,
        alignment=1,
        spaceAfter=4
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10.5,
        leading=14,
        textColor=colors.black,
        alignment=1,
        spaceAfter=12
    )

    inst_style = ParagraphStyle(
        'InstTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=colors.black,
        alignment=1,
        spaceAfter=2
    )

    inst_sub = ParagraphStyle(
        'InstSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#333333"),
        alignment=1,
        spaceAfter=10
    )

    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.black,
        spaceBefore=12,
        spaceAfter=5,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=colors.black,
        spaceBefore=7,
        spaceAfter=3,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.black,
        spaceAfter=5
    )

    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.black,
        leftIndent=14,
        firstLineIndent=-10,
        spaceAfter=3
    )

    code_style = ParagraphStyle(
        'Code_Custom',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8,
        leading=11,
        textColor=colors.black
    )

    table_cell = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10.5,
        textColor=colors.black
    )

    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10.5,
        textColor=colors.black
    )

    table_head = ParagraphStyle(
        'TableHead',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10.5,
        textColor=colors.black
    )

    story = []

    # Institution Header
    story.append(Paragraph("AMAL JYOTHI COLLEGE OF ENGINEERING, KANJIRAPPALLY", inst_style))
    story.append(Paragraph("DEPARTMENT OF COMPUTER APPLICATIONS<br/>24MCAT213 - INTERNET OF THINGS (MCA 2025-27, SEMESTER 3)", inst_sub))
    story.append(HRFlowable(width="100%", thickness=1.0, color=colors.black, spaceBefore=2, spaceAfter=10))

    # Title
    story.append(Paragraph("FloraGuard IoT", title_style))
    story.append(Paragraph("Agricultural Microclimate Telemetry & Plant Pathogen Early Warning System<br/>with SQLite3 Persistence, Containerized Backend & Real-Time Dashboard", subtitle_style))

    # Meta Table
    meta_data = [
        [Paragraph("<b>Course Code:</b> 24MCAT213 - Internet of Things", table_cell), Paragraph("<b>Date:</b> November 2026", table_cell)],
        [Paragraph("<b>Target Hardware:</b> ESP32 DevKit v1", table_cell), Paragraph("<b>Cloud Platform:</b> Render.com (Docker)", table_cell)],
        [Paragraph("<b>Public Cloud URL:</b> https://floraguard-iot.onrender.com", table_cell), Paragraph("<b>Database:</b> SQLite3 (floraguard.db)", table_cell)]
    ]
    t_meta = Table(meta_data, colWidths=[240, 240])
    t_meta.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.black),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#AAAAAA")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 8))

    # 1. ABSTRACT
    story.append(Paragraph("1. Abstract & Problem Statement", h1_style))
    abstract_text = (
        "<b>FloraGuard IoT</b> is an end-to-end smart agricultural microclimate telemetry and automated plant pathogen "
        "early warning system. Using an <b>ESP32 microcontroller</b>, the system acquires real-time environmental metrics "
        "from three physical sensors: ambient air temperature and relative humidity via a digital <b>DHT11 sensor</b>, "
        "soil moisture saturation via an <b>analog capacitive probe</b>, and surface precipitation/leaf wetness via a "
        "<b>conductive rain sensor grid</b>. Telemetry readings are packaged into structured JSON payloads and transmitted "
        "over Wi-Fi via HTTP/HTTPS POST to a high-performance <b>FastAPI</b> backend service backed by an <b>SQLite3 relational database</b>. "
        "An integrated epidemiological calculation engine evaluates fungal late blight (<i>Phytophthora infestans</i>) and "
        "downy mildew threats based on the agricultural <b>Mills Period Infection Model</b>. The live readings, historical charts, "
        "and pathogen risk levels are broadcast to a responsive web dashboard via WebSockets and accessible through a visual "
        "database management interface."
    )
    story.append(Paragraph(abstract_text, body_style))

    # 2. HARDWARE SPECIFICATIONS
    story.append(Paragraph("2. Hardware Specifications & Interfacing Matrix", h1_style))
    story.append(Paragraph("The physical node comprises four core hardware modules engineered for stable edge acquisition:", body_style))

    hw_items = [
        "<b>ESP32 Dev Module (ESP-WROOM-32):</b> 240MHz dual-core Xtensa LX6 processor with integrated 2.4 GHz Wi-Fi (802.11 b/g/n), 520 KB SRAM, and 12-bit ADC channels.",
        "<b>DHT11 Sensor:</b> Calibrated digital signal output measuring air temperature (0–50°C, ±2°C) and relative humidity (20–90% RH, ±5%).",
        "<b>Capacitive Soil Moisture Probe v1.2:</b> Corrosion-resistant analog probe measuring volumetric water content by dielectric permittivity.",
        "<b>Rain / Leaf Wetness Module:</b> Interdigital nickel-plated sensor grid tracking liquid precipitation and dew accumulation.",
        "<b>Status LED Indicator:</b> Active GPIO pin signaling network transmission and hardware heartbeat."
    ]
    for item in hw_items:
        story.append(Paragraph(f"• {item}", bullet_style))

    story.append(Spacer(1, 4))
    story.append(Paragraph("Sensor Wiring & Interfacing Pinout", h2_style))

    pin_data = [
        [Paragraph("Sensor Module", table_head), Paragraph("Module Pin", table_head), Paragraph("ESP32 Pin", table_head), Paragraph("Interface / Mode", table_head), Paragraph("Description", table_head)],
        [Paragraph("DHT11", table_cell_bold), Paragraph("DATA / OUT", table_cell), Paragraph("GPIO 4", table_cell_bold), Paragraph("Digital GPIO", table_cell), Paragraph("One-wire digital signal", table_cell)],
        [Paragraph("Soil Moisture", table_cell_bold), Paragraph("AOUT", table_cell), Paragraph("GPIO 35", table_cell_bold), Paragraph("ADC1_CH7", table_cell), Paragraph("Analog 12-bit moisture voltage", table_cell)],
        [Paragraph("Rain Sensor", table_cell_bold), Paragraph("AOUT", table_cell), Paragraph("GPIO 34", table_cell_bold), Paragraph("ADC1_CH6", table_cell), Paragraph("Analog 12-bit precipitation level", table_cell)],
        [Paragraph("Status LED", table_cell_bold), Paragraph("Anode (+)", table_cell), Paragraph("GPIO 2", table_cell_bold), Paragraph("Digital Output", table_cell), Paragraph("Blinks on successful transmission", table_cell)],
        [Paragraph("All Sensors", table_cell_bold), Paragraph("VCC / GND", table_cell), Paragraph("3.3V / GND", table_cell_bold), Paragraph("Power Rails", table_cell), Paragraph("Regulated 3.3V DC rail", table_cell)],
    ]
    t_pin = Table(pin_data, colWidths=[80, 75, 75, 95, 155])
    t_pin.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#EEEEEE")),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_pin)

    # 3. COMMUNICATION ARCHITECTURE
    story.append(Paragraph("3. Data Communication Architecture", h1_style))
    comm_text = (
        "The ESP32 firmware reads sensors on a 3-second cycle (3000 ms), applies a 10-sample moving average filter on analog "
        "channels to reject ADC noise, and serializes the parameters into a JSON object. The payload is posted via HTTP or "
        "HTTPS (utilizing <code>WiFiClientSecure</code> with certificate validation bypass for lightweight IoT transmission) "
        "to the FastAPI backend endpoint <code>/api/telemetry</code>:"
    )
    story.append(Paragraph(comm_text, body_style))

    json_snippet = (
        "{\n"
        '  "device_id": "ESP32-AGRI-01",\n'
        '  "temperature": 27.3,\n'
        '  "humidity": 74.0,\n'
        '  "soil_moisture": 44.0,\n'
        '  "rain_intensity": 23.2,\n'
        '  "source": "HARDWARE"\n'
        "}"
    )
    t_code = Table([[Paragraph(json_snippet.replace('\n', '<br/>').replace(' ', '&nbsp;'), code_style)]], colWidths=[480])
    t_code.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.black),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F5F5F5")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_code)

    # 4. DATABASE DESIGN & PERSISTENCE
    story.append(Paragraph("4. Database Design & Relational Persistence", h1_style))
    db_text = (
        "To fulfill the persistent storage criteria, the application integrates an <b>SQLite3</b> database "
        "(<code>floraguard.db</code>) managed natively by Python. Every incoming hardware or simulated reading is validated "
        "against Pydantic schemas and permanently saved into the <code>sensor_telemetry</code> relational table."
    )
    story.append(Paragraph(db_text, body_style))

    schema_data = [
        [Paragraph("Field", table_head), Paragraph("Type", table_head), Paragraph("Constraints", table_head), Paragraph("Description", table_head)],
        [Paragraph("id", table_cell_bold), Paragraph("INTEGER", table_cell), Paragraph("PRIMARY KEY AUTOINCREMENT", table_cell), Paragraph("Unique sequential reading ID", table_cell)],
        [Paragraph("device_id", table_cell_bold), Paragraph("TEXT", table_cell), Paragraph("NOT NULL", table_cell), Paragraph("Device identity string (e.g. ESP32-AGRI-01)", table_cell)],
        [Paragraph("temperature", table_cell_bold), Paragraph("REAL", table_cell), Paragraph("NOT NULL", table_cell), Paragraph("Air temperature in degrees Celsius", table_cell)],
        [Paragraph("humidity", table_cell_bold), Paragraph("REAL", table_cell), Paragraph("NOT NULL", table_cell), Paragraph("Relative humidity percentage", table_cell)],
        [Paragraph("soil_moisture", table_cell_bold), Paragraph("REAL", table_cell), Paragraph("NOT NULL", table_cell), Paragraph("Volumetric soil moisture percentage", table_cell)],
        [Paragraph("rain_intensity", table_cell_bold), Paragraph("REAL", table_cell), Paragraph("NOT NULL", table_cell), Paragraph("Precipitation intensity percentage", table_cell)],
        [Paragraph("risk_score", table_cell_bold), Paragraph("INTEGER", table_cell), Paragraph("NOT NULL", table_cell), Paragraph("Mills Period pathogen index (0-100)", table_cell)],
        [Paragraph("risk_level", table_cell_bold), Paragraph("TEXT", table_cell), Paragraph("NOT NULL", table_cell), Paragraph("Risk status (LOW / MODERATE / HIGH / CRITICAL)", table_cell)],
        [Paragraph("diagnosis", table_cell_bold), Paragraph("TEXT", table_cell), Paragraph("NOT NULL", table_cell), Paragraph("Epidemiological pathogen diagnosis", table_cell)],
        [Paragraph("source", table_cell_bold), Paragraph("TEXT", table_cell), Paragraph("NOT NULL", table_cell), Paragraph("HARDWARE or SIMULATION marker", table_cell)],
        [Paragraph("timestamp", table_cell_bold), Paragraph("TEXT", table_cell), Paragraph("NOT NULL", table_cell), Paragraph("Packet time (HH:MM:SS)", table_cell)],
        [Paragraph("created_at", table_cell_bold), Paragraph("DATETIME", table_cell), Paragraph("DEFAULT CURRENT_TIMESTAMP", table_cell), Paragraph("Server-side ingestion timestamp", table_cell)],
    ]
    t_schema = Table(schema_data, colWidths=[90, 65, 135, 190])
    t_schema.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#EEEEEE")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_schema)
    story.append(Spacer(1, 4))

    story.append(Paragraph("Database Endpoints & Presentation Viewer", h2_style))
    db_features = [
        "<b>REST API (<code>GET /api/database/records</code>):</b> Supports limit parameters and source filtering (<code>HARDWARE</code> vs <code>SIMULATION</code>), returning full audit counts and JSON data.",
        "<b>Visual Database Viewer (<code>GET /database</code>):</b> A dedicated, clean web UI created specifically for viva and presentation sessions. Features real-time statistics cards, dynamic filtering, structured risk tags, and 10-second auto-refresh."
    ]
    for feat in db_features:
        story.append(Paragraph(f"• {feat}", bullet_style))

    # 5. CONTAINERIZATION & CLOUD DEPLOYMENT
    story.append(Paragraph("5. Containerization & Cloud Deployment", h1_style))
    docker_text = (
        "The application is fully containerized using <b>Docker</b> and <b>Docker Compose</b> to ensure guaranteed consistency "
        "across Windows, Linux, and Cloud environments. The image packages Python 3.11-slim, all dependencies, and persistent "
        "volume mounts for <code>floraguard.db</code>.<br/>"
        "The project is publicly deployed on <b>Render.com</b> directly from the GitHub repository (<code>https://github.com/Nehusam/floraguard-IoT</code>), "
        "providing a high-availability cloud endpoint at <b>https://floraguard-iot.onrender.com</b>."
    )
    story.append(Paragraph(docker_text, body_style))

    # 6. REAL-TIME DASHBOARD
    story.append(Paragraph("6. Real-Time Botanical Dashboard", h1_style))
    dash_items = [
        "<b>Clean Minimalist Interface:</b> Built with HTML5, Tailwind CSS, Lucide icons, and Chart.js, designed specifically for rapid comprehension without visual clutter.",
        "<b>4 Live Telemetry Gauges:</b> Ambient Air Temperature (°C), Canopy Relative Humidity (% RH), Soil Volumetric Moisture (%), and Rain Precipitation (%).",
        "<b>Mills Period Pathogen Risk Engine:</b> Evaluates infection thresholds (e.g. sustained humidity >70%, temperature 18-28°C, and surface moisture) to calculate an aggregate risk score (0-100) and issue instant preventive actions.",
        "<b>WebSocket Real-Time Broadcast (<code>/ws/telemetry</code>):</b> Directly pushes live sensor events to connected browsers with sub-millisecond overhead.",
        "<b>Dual Interactive Historical Charts:</b> Real-time rolling graphs tracking atmospheric trends and hydrological balance over time.",
        "<b>Recent Telemetry Audit Log:</b> Real-time table displaying recent packets with one-click CSV export and a link to the visual database viewer."
    ]
    for item in dash_items:
        story.append(Paragraph(f"• {item}", bullet_style))

    # 7. TEST MATRIX & VERIFICATION
    story.append(Paragraph("7. Test Matrix & Experimental Verification", h1_style))
    
    test_data = [
        [Paragraph("Test ID", table_head), Paragraph("Test Case", table_head), Paragraph("Procedure", table_head), Paragraph("Expected Result", table_head), Paragraph("Status", table_head)],
        [Paragraph("TC-01", table_cell_bold), Paragraph("Wi-Fi Connection", table_cell), Paragraph("Power ESP32; authenticate to AP", table_cell), Paragraph("IP assigned, serial prints success", table_cell), Paragraph("<b>PASS</b>", table_cell)],
        [Paragraph("TC-02", table_cell_bold), Paragraph("DHT11 Sampling", table_cell), Paragraph("Read temp and humidity registers", table_cell), Paragraph("Valid numeric °C and % values (non-NaN)", table_cell), Paragraph("<b>PASS</b>", table_cell)],
        [Paragraph("TC-03", table_cell_bold), Paragraph("Soil Probe ADC", table_cell), Paragraph("Place probe in dry soil vs wet soil", table_cell), Paragraph("Analog percentage scales 15% to 85%", table_cell), Paragraph("<b>PASS</b>", table_cell)],
        [Paragraph("TC-04", table_cell_bold), Paragraph("Rain Sensor Grid", table_cell), Paragraph("Apply water droplet onto sensor plate", table_cell), Paragraph("Rain intensity jumps from 0% to >80%", table_cell), Paragraph("<b>PASS</b>", table_cell)],
        [Paragraph("TC-05", table_cell_bold), Paragraph("HTTP/HTTPS Telemetry", table_cell), Paragraph("ESP32 POST to /api/telemetry", table_cell), Paragraph("HTTP 200 response with risk scoring", table_cell), Paragraph("<b>PASS</b>", table_cell)],
        [Paragraph("TC-06", table_cell_bold), Paragraph("Database Logging", table_cell), Paragraph("Inspect SQLite3 table records", table_cell), Paragraph("460+ rows recorded with HARDWARE tag", table_cell), Paragraph("<b>PASS</b>", table_cell)],
        [Paragraph("TC-07", table_cell_bold), Paragraph("Live Dashboard Sync", table_cell), Paragraph("Open web dashboard on browser", table_cell), Paragraph("Badge switches to LIVE HARDWARE DATA", table_cell), Paragraph("<b>PASS</b>", table_cell)],
        [Paragraph("TC-08", table_cell_bold), Paragraph("Cloud Deployment", table_cell), Paragraph("Access Render public URL", table_cell), Paragraph("Fully operational live cloud service", table_cell), Paragraph("<b>PASS</b>", table_cell)],
    ]
    t_test = Table(test_data, colWidths=[40, 95, 130, 165, 50])
    t_test.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#EEEEEE")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('ALIGN', (4,1), (4,-1), 'CENTER'),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_test)

    # 8. CONCLUSION
    story.append(Paragraph("8. Conclusion", h1_style))
    concl_text = (
        "The <b>FloraGuard IoT</b> platform completely fulfills all five core assignment requirements prescribed by the "
        "MCA 24MCAT213 curriculum: (1) physical multi-sensor interfacing on ESP32, (2) reliable wireless telemetry transmission, "
        "(3) standardized containerization with Docker, (4) robust relational database persistence in SQLite3, and (5) an "
        "advanced, responsive real-time web dashboard with cloud accessibility. The solution provides a scalable, industrial-grade "
        "foundation for modern automated microclimate and precision crop disease monitoring."
    )
    story.append(Paragraph(concl_text, body_style))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Monochrome PDF generated successfully: {filename}")

if __name__ == "__main__":
    build_pdf()
