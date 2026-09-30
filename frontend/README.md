# Parkindraw AI - Frontend

Frontend web application for **Parkindraw AI**, a neuromotor risk screening platform for Parkinson's Disease based on hand-drawn pattern analysis (*Circle, Meander, Spiral*) powered by Computer Vision (ResNet-18) models and a Late Multi-Modal Probability Fusion strategy.

Built with a modular, maintainable, and production-oriented architecture that strictly separates concerns across UI components, feature-driven business logic, decoupled content localization, theme and locale state management, and the API integration layer.

---

## Tech Stack

- **Framework**: [React 19](https://react.dev/) + [TypeScript](https://www.typescriptlang.org/)
- **Bundler & Tooling**: [Vite 8](https://vite.dev/)
- **Styling**: [Tailwind CSS v4](https://tailwindcss.com/) (`@tailwindcss/vite`)
- **Typography**: [Figtree Variable Font](https://fontsource.org/fonts/figtree) (`@fontsource-variable/figtree`)
- **Icons**: [Lucide React](https://lucide.dev/)
- **HTTP Client**: [Axios](https://axios-http.com/)

---

## Directory Structure

```text
frontend/
├── public/                     # Static public assets
├── src/
│   ├── app/                    # Application configuration, routing & context providers
│   │   ├── layouts/
│   │   │   └── RootLayout.tsx  # Main application shell (Navbar, Footer, Container)
│   │   ├── AppRouter.tsx       # Client-side router & navigation context
│   │   ├── LocaleProvider.tsx  # Internationalization (i18n: id/en) context provider
│   │   ├── ThemeProvider.tsx   # Dark/light theme management provider
│   │   ├── localeContext.ts    # Locale context definition & custom hook
│   │   ├── themeContext.ts     # Theme context definition & custom hook
│   │   └── routes.ts           # Application route definitions & types
│   │
│   ├── assets/                 # Internal media assets (images, logos, icons)
│   │
│   ├── components/             # Reusable UI component library
│   │   ├── shared/             # Shared layout, navigation & utility components
│   │   │   ├── Footer.tsx
│   │   │   ├── LanguageSwitch.tsx
│   │   │   ├── Navbar.tsx
│   │   │   ├── NetworkStatusBadge.tsx
│   │   │   ├── PageHeader.tsx
│   │   │   ├── SectionContainer.tsx
│   │   │   ├── SettingsMenu.tsx
│   │   │   └── ThemeSwitch.tsx
│   │   │
│   │   └── ui/                 # Design system primitives (Headless/UI atoms)
│   │       ├── Accordion.tsx
│   │       ├── Alert.tsx
│   │       ├── Badge.tsx
│   │       ├── Button.tsx
│   │       ├── Card.tsx
│   │       ├── ProgressBar.tsx
│   │       └── Tabs.tsx
│   │
│   ├── content/                # Decoupled static content & bilingual localization
│   │   ├── about.content.ts    # Methodology, model metadata, & dataset provenance
│   │   ├── faq.content.ts      # Frequently asked questions & educational categories
│   │   ├── home.content.ts     # Homepage hero, workflow steps, & digital biomarkers
│   │   ├── navigation.content.ts # Brand metadata, menu links, & legal disclaimers
│   │   ├── screening.content.ts  # Drawing guides, instructions, & report texts
│   │   ├── ui.content.ts       # Common interactive UI strings & feedback labels
│   │   └── types.ts            # TypeScript interfaces for content structures
│   │
│   ├── features/               # Feature-Driven Architecture modules
│   │   ├── about/              # About & Methodology feature module
│   │   │   └── components/
│   │   │       ├── ArchitectureOverview.tsx
│   │   │       ├── BenchmarkMetricsTable.tsx
│   │   │       ├── Chapter.tsx
│   │   │       ├── DatasetProvenance.tsx
│   │   │       └── ModelMetadataTable.tsx
│   │   │
│   │   ├── faq/                # FAQ presentation components
│   │   │   └── components/
│   │   │       └── FaqItem.tsx
│   │   │
│   │   └── screening/          # Core Neuromotor Screening feature
│   │       ├── components/
│   │       │   ├── AnalysisLoadingView.tsx   # Inference progress & loading animation
│   │       │   ├── CanvasToolbar.tsx         # Drawing tool controls (undo, clear, stroke)
│   │       │   ├── ClinicalDisclaimerBox.tsx # Medical disclaimer & notice banner
│   │       │   ├── DigitalCanvas.tsx         # Interactive HTML5 touch/mouse canvas
│   │       │   ├── DrawingInstructions.tsx   # Active pattern guide & target template
│   │       │   ├── FileUploadDropzone.tsx    # Fallback image file upload dropzone
│   │       │   ├── ModalityBreakdownGrid.tsx # 3-modality individual metric cards
│   │       │   ├── ProbabilityScale.tsx      # Risk tier gauge & probability indicator
│   │       │   ├── ReportSummaryCard.tsx     # Session result summary & aggregate badge
│   │       │   ├── ScreeningWizard.tsx       # Multi-step screening wizard workflow
│   │       │   └── StepIndicator.tsx         # Visual progress step navigation
│   │       ├── hooks/
│   │       │   ├── useCanvasDrawing.ts       # Canvas stroke geometry & event handling
│   │       │   └── useScreeningSession.ts    # Screening state machine & session manager
│   │       └── types/
│   │           └── index.ts                  # Screening domain models & types
│   │
│   ├── hooks/                  # Global custom React hooks
│   │   └── useBackendHealth.ts # Live polling for FastAPI backend connectivity
│   │
│   ├── pages/                  # Top-level page views
│   │   ├── AboutPage.tsx       # Methodology, models & dataset transparency view
│   │   ├── HomePage.tsx        # Landing page (Hero, Workflow, Biomarkers, FAQ)
│   │   └── ScreeningPage.tsx   # Self-administered neuromotor screening view
│   │
│   ├── services/               # API integration & backend communication
│   │   ├── api.ts              # Axios instance, endpoints, & multipart requests
│   │   └── types.ts            # Backend DTOs & response schemas
│   │
│   ├── types/                  # Global application types
│   │   └── navigation.types.ts
│   │
│   ├── App.css
│   ├── App.tsx                 # Root application component
│   ├── index.css               # Tailwind CSS v4 directives & theme variables
│   └── main.tsx                # React application entry point
│
├── eslint.config.js            # ESLint flat configuration
├── index.html                  # HTML5 document template
├── package.json                # Project dependencies & npm scripts
├── tsconfig.json               # Root TypeScript configuration
├── tsconfig.app.json           # Application TypeScript configuration
├── tsconfig.node.json          # Vite tooling TypeScript configuration
└── vite.config.ts              # Vite configuration & backend proxy rules
```

---

## Architecture & Key Features

- **Multi-Modal Screening Wizard**: Guides participants through Circle, Meander, and Spiral drawing tasks with real-time canvas rendering, undo/redo history, and image dropzone fallbacks.
- **Late Fusion Risk Assessment**: Combines predictions across the three drawing patterns into an aggregate risk probability score alongside individual modality breakdowns.
- **Decoupled Bilingual Localization (i18n)**: Content is structured in decoupled files supporting English (`en`) and Indonesian (`id`) with instant runtime switching without page reload.
- **Privacy-First & In-Memory Pipeline**: Drawing data is processed as in-memory binary blobs without storing sensitive biometrics on the client device or server databases.
- **Adaptive Medical UI**: Engineered using Tailwind CSS v4 with dark/light themes, high contrast ratios, and accessible typography.

---

## Getting Started & Local Development

### 1. Prerequisites
- **Node.js**: v18+ or v20+
- **npm**: v9+ or v10+
- **Backend API**: Running at `http://127.0.0.1:8000` (refer to `backend/README.md`)

### 2. Installation
```bash
npm install
```

### 3. Running the Development Server
```bash
npm run dev
```
Open your browser and navigate to `http://localhost:5173/`.

Requests to `/api/*` are automatically proxied to the backend server at `http://127.0.0.1:8000`.

### 4. Production Build & Preview
```bash
# Build production bundle
npm run build

# Preview production build locally
npm run preview
```
Production assets will be generated in the `dist/` directory.

---

## Quality Assurance & Testing

```bash
# Run code quality and linting checks
npm run lint

# Validate TypeScript type compilation
npx tsc --noEmit
```

---

## License & Disclaimers

The Parkindraw frontend codebase is licensed under the [MIT License](../LICENSE).
