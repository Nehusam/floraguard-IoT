import sys
import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
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
            self.drawString(54, 842 - 36, "FLORAGUARD IOT — PLANT DISEASE DETECTION & EARLY WARNING SYSTEM")
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

    # Exact Clean Styling matching the standard academic template
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=19,
        textColor=colors.black,
        alignment=1,
        spaceAfter=14
    )

    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=colors.black,
        spaceBefore=11,
        spaceAfter=4,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=13,
        textColor=colors.black,
        spaceBefore=6,
        spaceAfter=3,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13.5,
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
        spaceAfter=2.5
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

    # Title Banner (All Caps matching reference standard)
    story.append(Paragraph("FLORAGUARD: IOT-BASED PLANT DISEASE DETECTION & EARLY WARNING SYSTEM", title_style))
    story.append(Spacer(1, 4))

    # 1. INTRODUCTION
    story.append(Paragraph("1. INTRODUCTION", h1_style))
    intro_p1 = (
        "Agriculture is the primary livelihood for millions and forms the backbone of global food security. "
        "However, unpredictable environmental fluctuations and the unchecked spread of crop diseases, particularly "
        "foliar fungal blights and mildews, result in catastrophic yield losses each season. Traditional farming "
        "methodologies depend heavily on manual physical observation of visual leaf symptoms. Often, by the time visible "
        "foliar damage or necrotic spotting appears to the naked eye, the pathogen incubation cycle is already advanced, "
        "rendering late fungicide applications expensive and largely ineffective."
    )
    intro_p2 = (
        "To address this critical issue, this project proposes an IoT-based Plant Disease Detection and Microclimate "
        "Early Warning System named <b>FloraGuard IoT</b>. The system continuously acquires ambient temperature and "
        "humidity via a DHT11 sensor, volumetric soil moisture through a capacitive soil sensor, and surface leaf wetness "
        "via a conductive precipitation grid. These microclimatic variables are processed by an ESP32 microcontroller and "
        "streamed via Wi-Fi to a containerized FastAPI cloud server and SQLite3 database. The backend executes an "
        "automated epidemiological Mills Period infection model to compute real-time disease risk indexes and alert "
        "growers before visible foliar destruction occurs."
    )
    intro_p3 = (
        "This solution provides a low-cost, accurate, and scalable approach to precision crop health management, "
        "minimizing unnecessary chemical spray cycles while drastically reducing manual field scouting effort."
    )
    story.append(Paragraph(intro_p1, body_style))
    story.append(Paragraph(intro_p2, body_style))
    story.append(Paragraph(intro_p3, body_style))

    # 2. AIM OF THE PROJECT
    story.append(Paragraph("2. AIM OF THE PROJECT", h1_style))
    aim_text = (
        "The primary aim of this project is to design, develop, and deploy an IoT-enabled microclimate telemetry and "
        "automated plant disease early warning system that continuously monitors crop canopy metrics, calculates fungal "
        "pathogen germination risks in real time, and alerts farmers through an interactive live dashboard."
    )
    story.append(Paragraph(aim_text, body_style))

    # 3. OBJECTIVES
    story.append(Paragraph("3. OBJECTIVES", h1_style))
    objs = [
        "To acquire real-time ambient temperature and humidity using a calibrated DHT11 digital sensor module.",
        "To measure volumetric soil moisture levels using a corrosion-resistant capacitive soil moisture probe.",
        "To monitor surface leaf wetness and precipitation events using a nickel-coated conductive rain sensor grid.",
        "To aggregate, filter, and transmit sensor telemetry from an ESP32 microcontroller to the cloud backend via Wi-Fi.",
        "To implement an algorithmic disease risk assessment engine based on the botanical Mills Period infection model.",
        "To provide long-term historical persistence of sensor records using an SQLite3 relational database.",
        "To build a responsive, zero-latency web dashboard with WebSocket streaming and cloud accessibility (Render/Docker)."
    ]
    for obj in objs:
        story.append(Paragraph(f"• {obj}", bullet_style))

    # 4. EXISTING SYSTEM
    story.append(Paragraph("4. EXISTING SYSTEM", h1_style))
    story.append(Paragraph("Existing agricultural disease monitoring methods primarily rely on physical inspections and static weather forecasts.", body_style))
    story.append(Paragraph("Disadvantages:", h2_style))
    disadvs = [
        "Manual leaf scouting is labor-intensive, error-prone, and impractical for large acreages.",
        "Visual symptoms appear only after pathogen colonization and cellular tissue damage have already occurred.",
        "Regional weather forecasts lack localized canopy microclimate precision (temperature, dew point, leaf wetness).",
        "Over-reliance on routine calendar-based fungicide sprays leads to chemical wastage, soil toxicity, and pest resistance.",
        "Lack of centralized historical telemetry persistence and automated notification mechanisms."
    ]
    for d in disadvs:
        story.append(Paragraph(f"• {d}", bullet_style))

    # 5. PROPOSED SYSTEM
    story.append(Paragraph("5. PROPOSED SYSTEM", h1_style))
    prop_text = (
        "The proposed system introduces an autonomous IoT sensing station combined with edge processing and cloud-hosted "
        "epidemiological analytics. Multi-parameter sensor nodes acquire continuous canopy metrics. The ESP32 edge processor "
        "applies digital moving-average noise filtering and posts structured JSON packets to the cloud service. "
        "The FastAPI backend correlates sustained humidity (>75%), optimal spore incubation temperatures (18–28°C), and "
        "leaf surface moisture duration to compute a 0–100 Disease Risk Index. When critical thresholds are breached, the system "
        "automatically triggers risk level warnings (Low, Moderate, High) with immediate agronomic remediation guidance on the "
        "live dashboard. This eliminates guesswork and enables preventative crop defense."
    )
    story.append(Paragraph(prop_text, body_style))

    # 6. SYSTEM ARCHITECTURE
    story.append(Paragraph("6. SYSTEM ARCHITECTURE", h1_style))
    story.append(Paragraph("The architecture comprises two main operational tiers — Device Layer and Cloud/Application Layer.", body_style))
    
    story.append(Paragraph("6.1 Hardware Components", h2_style))
    hw_comps = [
        "<b>ESP32 DevKit V1:</b> 32-bit dual-core 240MHz microcontroller with built-in 2.4 GHz Wi-Fi and 12-bit ADC channels.",
        "<b>DHT11 Sensor:</b> Single-bus digital sensor measuring temperature (0–50°C) and relative humidity (20–90% RH).",
        "<b>Capacitive Soil Moisture Probe v1.2:</b> Dielectric permittivity analog sensor resistant to soil electrolytic corrosion.",
        "<b>Rain / Leaf Wetness Module:</b> Conductive interdigital trace board tracking raindrop impact and foliar dew moisture.",
        "<b>Breadboard & Jumper Wires:</b> Breadboard layout for stable sensor bus routing and 3.3V power rails.",
        "<b>Power Supply (5V / Micro-USB):</b> Regulated power distribution for continuous edge acquisition."
    ]
    for hw in hw_comps:
        story.append(Paragraph(f"• {hw}", bullet_style))

    story.append(Paragraph("6.2 Software Components", h2_style))
    sw_comps = [
        "<b>Arduino IDE & C++:</b> Embedded firmware development, ADC moving-average calibration, and WiFiClientSecure HTTP POST engine.",
        "<b>FastAPI (Python 3.11):</b> Asynchronous high-performance RESTful API backend handling telemetry ingestion and risk evaluation.",
        "<b>SQLite3 Database:</b> Embedded SQL relational database (`floraguard.db`) storing structured historical sensor readings.",
        "<b>WebSockets Protocol:</b> Full-duplex persistent stream pushing real-time metrics to browser sessions with zero latency.",
        "<b>Responsive Web Dashboard:</b> User interface built using HTML5, Tailwind CSS, Lucide icons, and Chart.js rolling line charts.",
        "<b>Docker & Docker Compose:</b> Multi-platform containerization for isolated packaging and automated cloud deployment."
    ]
    for sw in sw_comps:
        story.append(Paragraph(f"• {sw}", bullet_style))

    # 7. WORKING PRINCIPLE
    story.append(Paragraph("7. WORKING PRINCIPLE", h1_style))
    steps = [
        "<b>Initialization:</b> The ESP32 boots, establishes secure Wi-Fi association with the local wireless network, and tests sensor pins.",
        "<b>Data Acquisition:</b> On a 3-second cycle, the ESP32 reads DHT11 digital frames and samples 10 consecutive ADC conversions for soil and leaf wetness.",
        "<b>Data Normalization:</b> Analog ADC values (0–4095) are mathematically calibrated to percentage scales (0.0% – 100.0%).",
        "<b>JSON Serialization:</b> Telemetry is formatted into structured JSON and dispatched via HTTP/HTTPS POST to `/api/telemetry`.",
        "<b>Pathogen Risk Analysis:</b> The backend executes Mills Period rule matrices, grading spore germination viability from Low to Critical.",
        "<b>Database Archival:</b> All readings, calculated risk scores, device identity, and timestamps are committed to SQLite3 table `sensor_telemetry`.",
        "<b>Real-Time Visualization:</b> Records are broadcast through WebSockets and displayed live on dashboard cards, gauges, charts, and table."
    ]
    for i, st in enumerate(steps, 1):
        story.append(Paragraph(f"{i}. {st}", bullet_style))

    # 8. CONNECTION DETAILS
    story.append(Paragraph("8. CONNECTION DETAILS", h1_style))
    pin_data = [
        [Paragraph("Component", table_head), Paragraph("Pin Name", table_head), Paragraph("Signal Type", table_head), Paragraph("ESP32 Pin", table_head), Paragraph("Voltage", table_head)],
        [Paragraph("DHT11", table_cell_bold), Paragraph("DATA / OUT", table_cell), Paragraph("Digital GPIO", table_cell), Paragraph("GPIO 4", table_cell_bold), Paragraph("3.3V", table_cell)],
        [Paragraph("DHT11", table_cell_bold), Paragraph("VCC / GND", table_cell), Paragraph("Power Rails", table_cell), Paragraph("3.3V / GND", table_cell), Paragraph("3.3V / 0V", table_cell)],
        [Paragraph("Capacitive Soil Probe", table_cell_bold), Paragraph("AOUT (Analog)", table_cell), Paragraph("ADC1_CH7", table_cell), Paragraph("GPIO 35", table_cell_bold), Paragraph("3.3V", table_cell)],
        [Paragraph("Capacitive Soil Probe", table_cell_bold), Paragraph("VCC / GND", table_cell), Paragraph("Power Rails", table_cell), Paragraph("3.3V / GND", table_cell), Paragraph("3.3V / 0V", table_cell)],
        [Paragraph("Rain / Leaf Wetness", table_cell_bold), Paragraph("AOUT (Analog)", table_cell), Paragraph("ADC1_CH6", table_cell), Paragraph("GPIO 34", table_cell_bold), Paragraph("3.3V", table_cell)],
        [Paragraph("Rain / Leaf Wetness", table_cell_bold), Paragraph("VCC / GND", table_cell), Paragraph("Power Rails", table_cell), Paragraph("3.3V / GND", table_cell), Paragraph("3.3V / 0V", table_cell)],
        [Paragraph("Status Indicator LED", table_cell_bold), Paragraph("Anode (+)", table_cell), Paragraph("Digital Output", table_cell), Paragraph("GPIO 2", table_cell_bold), Paragraph("3.3V", table_cell)],
    ]
    t_pin = Table(pin_data, colWidths=[100, 85, 95, 95, 105])
    t_pin.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#EEEEEE")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_pin)

    # 9. CLOUD & CONTAINER HOSTING
    story.append(Paragraph("9. CLOUD & CONTAINER HOSTING", h1_style))
    cloud_p = (
        "The backend server is containerized and hosted in the cloud using standard container orchestration tooling:"
    )
    story.append(Paragraph(cloud_p, body_style))
    cloud_items = [
        "<b>Cloud Web Service:</b> Deployed on <b>Render.com</b> via automated CI/CD directly synced to GitHub repository (`https://github.com/Nehusam/floraguard-IoT.git`).",
        "<b>Public Endpoint:</b> Live public HTTPS service accessible at <b>https://floraguard-iot.onrender.com</b>.",
        "<b>Docker Setup:</b> Standard `Dockerfile` with Python 3.11-slim, multi-stage dependency isolation, and port 8000 exposed.",
        "<b>Deployment via Docker Compose:</b> Unified orchestration mounting `floraguard.db` onto a persistent storage volume.",
        "<b>Database Management Viewer:</b> Dedicated administrative web route at `/database` for visual inspection of persistent SQLite3 records during evaluations."
    ]
    for ci in cloud_items:
        story.append(Paragraph(f"• {ci}", bullet_style))

    # 10. RESULTS
    story.append(Paragraph("10. RESULTS", h1_style))
    story.append(Paragraph("The implemented FloraGuard IoT system successfully achieves:", body_style))
    res_items = [
        "Measures real-time air temperature, canopy humidity, volumetric soil moisture, and leaf wetness accurately.",
        "Calculates botanical Mills Period infection risks continuously and categorizes pathogen severity (Low, Moderate, High).",
        "Dispatches immediate microclimate remediation guidance when humidity exceeds 80% or leaf surface wetness is prolonged.",
        "Stores over 900+ consecutive hardware telemetry records in persistent SQLite database storage.",
        "Presents dynamic rolling telemetry charts and live metric cards across both local and public cloud dashboards without manual browser refreshes."
    ]
    for r in res_items:
        story.append(Paragraph(f"• {r}", bullet_style))

    # 11. ADVANTAGES
    story.append(Paragraph("11. ADVANTAGES", h1_style))
    adv_items = [
        "<b>Preventative Defense:</b> Detects favorable disease environments hours before visible tissue rot takes hold.",
        "<b>Automated Monitoring:</b> Eliminates repetitive manual physical field inspections and reduces labor expenditure.",
        "<b>Chemical Optimization:</b> Eliminates unnecessary preventative fungicide spraying, reducing environmental chemical load.",
        "<b>Zero-Latency Telemetry:</b> WebSocket push architecture updates browser gauges instantly upon each 3-second cycle.",
        "<b>Cost-Effective Hardware:</b> Built using readily available, modular, low-power components ideal for rural farm adoption.",
        "<b>Dual Local/Cloud Accessibility:</b> Operates equally well on isolated local farm networks and public cloud endpoints."
    ]
    for a in adv_items:
        story.append(Paragraph(f"• {a}", bullet_style))

    # 12. APPLICATIONS
    story.append(Paragraph("12. APPLICATIONS", h1_style))
    app_items = [
        "<b>Greenhouse Climate Automation:</b> Automated trigger of ventilation fans and dehumidifiers when mildew risk escalates.",
        "<b>Horticulture & Vineyards:</b> Early detection of Black Rot and Downy Mildew in high-value grape and berry crops.",
        "<b>Open Field Precision Farming:</b> Microclimate mapping to optimize localized drip irrigation timing.",
        "<b>Agricultural Research Institutes:</b> Accurate epidemiological record keeping for crop cultivar disease resistance trials."
    ]
    for ap in app_items:
        story.append(Paragraph(f"• {ap}", bullet_style))

    # 13. FUTURE ENHANCEMENTS
    story.append(Paragraph("13. FUTURE ENHANCEMENTS", h1_style))
    enh_items = [
        "<b>Automated Actuator Integration:</b> Relay module triggering automated misting systems, exhaust fans, or solenoid irrigation valves.",
        "<b>GSM/SMS Push Alerts:</b> Direct SMS notification to farmers' phones when cellular network connectivity is the only option.",
        "<b>LoRaWAN Long-Range Nodes:</b> Multi-node mesh spanning expansive hectares without requiring local Wi-Fi coverage.",
        "<b>Solar Power Harvesting:</b> Standalone battery-buffered solar charging for continuous off-grid outdoor deployment."
    ]
    for e in enh_items:
        story.append(Paragraph(f"• {e}", bullet_style))

    # 14. CONCLUSION
    story.append(Paragraph("14. CONCLUSION", h1_style))
    concl_text = (
        "The <b>FloraGuard IoT</b> system delivers an effective, intelligent, and affordable microclimate early warning "
        "solution to mitigate crop pathogen risks. By combining physical sensor acquisition (ESP32), algorithmic disease "
        "risk models (Mills Period baseline), SQLite3 relational persistence, containerized cloud hosting (Docker/Render), "
        "and a real-time web dashboard, the project lays a scalable, modern foundation for precision smart agriculture."
    )
    story.append(Paragraph(concl_text, body_style))

    # 15. PROJECT DESIGN & DATA FLOW
    story.append(Paragraph("15. PROJECT DESIGN (DATA FLOW)", h1_style))
    flow_steps = [
        "1. Physical Sensors (DHT11, Soil, Rain) → ESP32: Samples analog and digital microclimate readings.",
        "2. ESP32 → FastAPI Backend (HTTP/HTTPS): Packages JSON payload and posts to `/api/telemetry` over Wi-Fi.",
        "3. FastAPI → SQLite3 (`floraguard.db`): Automatically commits verified reading into `sensor_telemetry` table.",
        "4. FastAPI → Mills Period Engine: Evaluates fungal infection factors and determines real-time risk score.",
        "5. FastAPI → Dashboard UI (WebSockets & HTTP Sync): Broadcasts live metrics to browser cards, charts, and table."
    ]
    for fs in flow_steps:
        story.append(Paragraph(fs, body_style))

    # Build Document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Matched format PDF generated successfully: {filename}")

if __name__ == "__main__":
    build_pdf()
