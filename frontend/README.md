# ParkinDraw AI - Frontend

Frontend aplikasi web **ParkinDraw AI**, platform penapisan risiko neuromotorik (Penyakit Parkinson) berbasis analisis gambar goresan tangan (*Circle, Meander, Spiral*) menggunakan model Computer Vision (ResNet-18) dan strategi *Late Multi-Modal Probability Fusion*.

Dibangun dengan arsitektur **modular, maintainable, dan production-oriented**, memisahkan concerns antara UI components, business logic/features, data copy/content, serta API layer.

---

## 🛠️ Tech Stack

- **Framework**: [React 19](https://react.dev/) + [TypeScript](https://www.typescriptlang.org/)
- **Bundler & Tooling**: [Vite 8](https://vite.dev/)
- **Styling**: [Tailwind CSS v4](https://tailwindcss.com/) (`@tailwindcss/vite`)
- **Icons**: [Lucide React](https://lucide.dev/)
- **HTTP Client**: [Axios](https://axios-http.com/)

---

## 📁 Struktur Folder Proyek

```text
frontend/
├── public/                     # Aset statis publik
├── src/
│   ├── app/                    # Konfigurasi aplikasi & routing
│   │   ├── layouts/
│   │   │   └── RootLayout.tsx  # Shell utama (Navbar, Footer, Container)
│   │   ├── AppRouter.tsx       # Router client-side & context navigasi
│   │   └── routes.ts           # Definisi path & tipe rute aplikasi
│   │
│   ├── assets/                 # Aset internal (gambar, logo, ikon)
│   │
│   ├── components/             # Komponen UI umum & reusable
│   │   ├── shared/             # Komponen layout & navigasi bersama
│   │   │   ├── Footer.tsx
│   │   │   ├── Navbar.tsx
│   │   │   ├── NetworkStatusBadge.tsx
│   │   │   ├── PageHeader.tsx
│   │   │   └── SectionContainer.tsx
│   │   │
│   │   └── ui/                 # Primitif design system (Headless/UI atoms)
│   │       ├── Accordion.tsx
│   │       ├── Alert.tsx
│   │       ├── Badge.tsx
│   │       ├── Button.tsx
│   │       ├── Card.tsx
│   │       ├── ProgressBar.tsx
│   │       └── Tabs.tsx
│   │
│   ├── content/                # Pemisahan teks & konten statis (Decoupled Copy)
│   │   ├── about.content.ts    # Konten metodologi, model meta, & dataset
│   │   ├── faq.content.ts      # Pertanyaan umum & kategori edukasi
│   │   ├── home.content.ts     # Konten beranda, alur kerja, & biomarker
│   │   ├── navigation.content.ts # Brand, menu navigasi, & peringatan medis
│   │   ├── screening.content.ts  # Panduan & teks laporan penapisan
│   │   └── types.ts            # Tipe data TypeScript untuk seluruh konten
│   │
│   ├── features/               # Modul berbasis fitur (Feature-Driven Architecture)
│   │   ├── about/              # Fitur halaman Tentang & Metodologi
│   │   │   └── components/
│   │   │       ├── ArchitectureOverview.tsx
│   │   │       ├── BenchmarkMetricsTable.tsx
│   │   │       ├── DatasetProvenance.tsx
│   │   │       └── ModelMetadataTable.tsx
│   │   │
│   │   ├── faq/                # Komponen Tanya Jawab
│   │   │   └── components/
│   │   │       └── FaqItem.tsx
│   │   │
│   │   └── screening/          # Fitur inti Penapisan Neuromotorik
│   │       ├── components/
│   │       │   ├── AnalysisLoadingView.tsx   # Animasi status inferensi
│   │       │   ├── CanvasToolbar.tsx         # Toolbar alat gambar & undo/redo
│   │       │   ├── ClinicalDisclaimerBox.tsx # Kotak disclaimer medis resmi
│   │       │   ├── DigitalCanvas.tsx         # Kanvas HTML5 interaktif
│   │       │   ├── DrawingInstructions.tsx   # Panduan pola gambar aktif
│   │       │   ├── FileUploadDropzone.tsx    # Upload gambar fallback
│   │       │   ├── ModalityBreakdownGrid.tsx # Kartu rincian 3 modalitas
│   │       │   ├── ReportSummaryCard.tsx     # Ringkasan hasil & probabilitas
│   │       │   ├── ScreeningWizard.tsx       # Wizard langkah 1 s.d. selesai
│   │       │   └── StepIndicator.tsx         # Indikator progres tahapan
│   │       ├── hooks/
│   │       │   ├── useCanvasDrawing.ts       # Logika stroke & touch/mouse canvas
│   │       │   └── useScreeningSession.ts    # State management sesi skrining
│   │       └── types/
│   │           └── index.ts                  # Tipe domain skrining
│   │
│   ├── hooks/                  # Custom React hooks global
│   │   └── useBackendHealth.ts # Polling status koneksi backend FastAPI
│   │
│   ├── pages/                  # Komposisi halaman utama
│   │   ├── AboutPage.tsx       # Halaman Metodologi & Transparansi Model
│   │   ├── HomePage.tsx        # Halaman Beranda (Hero, Workflow, Biomarker, FAQ)
│   │   └── ScreeningPage.tsx   # Halaman Skrining Mandiri
│   │
│   ├── services/               # Integrasi API & Komunikasi Backend
│   │   ├── api.ts              # Axios instance & pemanggilan endpoint
│   │   └── types.ts            # Interface DTO request/response backend
│   │
│   ├── types/                  # Deklarasi tipe global
│   │   └── navigation.types.ts
│   │
│   ├── App.css
│   ├── App.tsx                 # Root component aplikasi
│   ├── index.css               # Setup Tailwind CSS v4 & base styles
│   └── main.tsx                # Entry point aplikasi React
│
├── eslint.config.js            # Konfigurasi linter
├── index.html                  # Dokumen HTML utama
├── package.json                # Dependensi & script proyek
├── tsconfig.json               # Konfigurasi TypeScript root
├── tsconfig.app.json           # Konfigurasi TypeScript untuk aplikasi
├── tsconfig.node.json          # Konfigurasi TypeScript untuk tooling Vite
└── vite.config.ts              # Konfigurasi Vite & proxy backend
```

---

## 🚀 Menjalankan Proyek Secara Lokal

### 1. Prasyarat
- Node.js (v18+ atau v20+)
- Backend FastAPI berjalan di `http://127.0.0.1:8000`

### 2. Instalasi Dependensi
```bash
npm install
```

### 3. Menjalankan Server Pengembangan
```bash
npm run dev
```
Aplikasi dapat diakses di `http://localhost:5173/`.

### 4. Build untuk Produksi
```bash
npm run build
```
Hasil build akan tersimpan di direktori `dist/`.
