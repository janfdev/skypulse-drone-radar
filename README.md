# SkyPulse: Autonomous Fleet & Drone Telemetry Radar

![SkyPulse Radar Dark Mode](./screenshots/skypulse_shadcn_dark.png)

**SkyPulse** adalah sistem komando telemetri radar armada drone otonom berlatensi ultra-rendah (*ultra-low latency C2 Command & Control*), dibangun dengan **Svelte 5 (Runes `$state`, `$derived`, `$props`)**, desain sistem **Shadcn UI** yang bersih, berpedoman pada filter kualitas **Antislop**, dan didukung oleh **FastAPI (Python Asynchronous ASGI & WebSocket)** di sisi komputasi telemetri & geofencing.

---

## 1. Arsitektur Sistem

```
┌────────────────────────────────────────────────────────┐
│            Svelte 5 + Shadcn UI Tactical C2            │
│  - Runes: $state, $derived, $props, $effect            │
│  - Tactical Polar Radar HUD (PPI Scope 20Hz)           │
│  - Target Kinematics & Mission Command Strip           │
│  - Dual Theme: Native Dark & Light Mode (WCAG AA)      │
└──────────────────────────▲─────────────────────────────┘
                           │  WebSocket Stream (20Hz)
                           │  REST API (Missions & Config)
┌──────────────────────────▼─────────────────────────────┐
│                 FastAPI Async Engine                   │
│  - Kinematic Motion & Battery Drain Simulator          │
│  - Spatial Geofencing (Haversine & Proximity Buffers)  │
│  - Autonomous Mission State Machine (RTH, HOLD, DIVERT)│
│  - OpenAPI Auto-Documentation (/docs)                  │
└────────────────────────────────────────────────────────┘
```

---

## 2. Fitur Utama & Standar Antislop Craftsmanship

1. **Desain Sistem Shadcn UI Berbasis Token**:
   - Komponen berbasis Shadcn UI: `Card`, `Badge`, `Button`, `Table`, `Tabs`, `Separator`.
   - Dukungan tema ganda **Dark Mode** dan **Light Mode** yang mulus dengan kontras tinggi (lulus standar WCAG AA) dan bebas silau.

2. **Bebas AI Slop (Antislop Filter)**:
   - Tidak menggunakan *em dash* (`—`) di teks antarmuka (R-02).
   - Tidak ada emoji dekoratif pada label atau tombol (R-04): digantikan ikon SVG terarah yang bersih.
   - Hirarki aksi misi taktis yang jelas: *RTH (Home)* berstatus darurat, *Resume* sebagai aksi primer, serta *Hold* dan *Divert* sebagai aksi sekunder (R-26).
   - Status UI lengkap: Empty state, Loading skeleton, dan Reconnect alert banner (R-27).
   - Aksesibilitas keyboard penuh dengan indikator fokus yang terlihat jelas (R-32).

3. **High-Frequency Tactical Radar HUD (60 FPS / 20Hz Stream)**:
   - Tampilan Plan Position Indicator (PPI) dengan ring jarak dinamis (15 km, 30 km, 50 km) serta azimuth derajat mata angin.
   - Efek sapuan radar terarah (*sweeping beam*) dan visualisasi vektor orientasi heading drone.
   - Peta batas zona larangan terbang (*No-Fly Zones*) seperti bandara, pangkalan udara militer, dan fasilitas strategis.

4. **Geofencing & Spatial Collision Engine**:
   - Algoritma perhitungan jarak Haversine bola bumi dengan zona penyangga peringatan (*warning buffer* 400m).
   - Deteksi otomatis pelanggaran batas wilayah udara dan penandaan status *WARNING* secara *real-time*.

5. **Autonomous Mission Command Strip**:
   - Pengiriman perintah kendali misi langsung ke armada:
     - **RTH (Return To Home)**: Drone otomatis menghitung azimuth balik menuju pangkalan awal dan mendarat.
     - **HOLD**: Drone menghentikan laju horizontal dan beralih ke mode melayang (*hover*).
     - **RESUME**: Melanjutkan penerbangan rute logistik pada kecepatan jelajah nominal.
     - **DIVERT**: Manuver penghindaran benturan (*collision avoidance*) dengan deviasi heading +90°.

---

## 3. Pratinjau Tampilan

### Dark Mode Cockpit (Default)
![Dark Mode](./screenshots/skypulse_shadcn_dark.png)

### Light Mode Cockpit (WCAG AA High-Contrast)
![Light Mode](./screenshots/skypulse_shadcn_light.png)

### Mobile Responsive Layout (Zero Horizontal Overflow)
![Mobile View](./screenshots/skypulse_mobile.png)

---

## 4. Panduan Menjalankan Sistem

### A. Menjalankan Backend (FastAPI)

1. Masuk ke direktori backend dan aktifkan virtual environment:
   ```bash
   cd /root/skypulse/backend
   source venv/bin/activate
   ```
2. Jalankan server FastAPI:
   ```bash
   PYTHONPATH=. python app/main.py
   ```
3. Akses dokumentasi interaktif Swagger UI di:
   `http://localhost:8008/docs`

4. Menjalankan Automated Test Suite (Pytest):
   ```bash
   PYTHONPATH=. pytest tests -v
   ```

### B. Menjalankan Frontend (Svelte 5)

1. Masuk ke direktori frontend:
   ```bash
   cd /root/skypulse/frontend
   bun install
   ```
2. Build dan jalankan preview:
   ```bash
   bun run build
   bun run preview --host 0.0.0.0 --port 5173
   ```
3. Buka dashboard di browser pada:
   `http://localhost:5173`

---

## 5. Struktur Berkas Projek

```
/root/skypulse/
├── backend/
│   ├── app/
│   │   ├── main.py                    # Entrypoint FastAPI & Lifespan task runner
│   │   ├── models/schemas.py          # Pydantic v2 domain schemas
│   │   ├── services/
│   │   │   ├── geofence.py            # Haversine spatial & No-Fly Zone engine
│   │   │   └── telemetry_engine.py    # Autonomous fleet simulator & WebSocket hub
│   │   └── api/routes.py              # REST & WebSocket endpoints
│   ├── tests/test_telemetry.py        # Automated test suite (Pytest + AsyncClient)
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.svelte                 # Root cockpit component (Svelte 5 Runes)
│   │   ├── main.ts                    # Mount entrypoint
│   │   ├── app.css                    # Tailwind CSS v4, Shadcn tokens, radar sweep
│   │   ├── types.ts                   # TypeScript interfaces
│   │   └── components/
│   │       ├── ThemeToggle.svelte     # Working Light/Dark theme switcher
│   │       ├── RadarDisplay.svelte    # Polar radar HUD & SVG vector plotter
│   │       ├── TelemetryCards.svelte  # Fleet aggregate KPI cards
│   │       ├── DroneDetailPanel.svelte# Selected drone cockpit & mission command strip
│   │       ├── FleetListTable.svelte  # Live tabular fleet directory with tabs
│   │       └── ui/                    # Shadcn UI primitives (Card, Badge, Button, Tabs)
│   ├── package.json
│   └── vite.config.ts
├── screenshots/
│   ├── skypulse_shadcn_dark.png
│   ├── skypulse_shadcn_light.png
│   └── skypulse_mobile.png
└── README.md
```
