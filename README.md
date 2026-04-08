# Upphandling24 - Tender Monitoring SaaS

## Projektöversikt

**Mål:** Bygga ett system som automatiskt bevakar offentliga upphandlingar och skickar notiser till företag.

## 🎯 Affärsmodell

- SaaS för B2B (subscription-based)
- Målgrupp: Små och medelstora företag i Sverige
- Värde: Företag missar aldrig en relevant upphandling

## 🏗️ Arkitektur

### Modulär struktur (byggs i ordning)

```
tender-system/
├── modules/
│   ├── 01_landing/       # ✅ KLAR - Landing page (lead capture)
│   ├── 02_onboarding/    # ⏳ Kundregistrering + preferenser
│   ├── 03_database/      # ⏳ Google Sheets databas
│   ├── 04_scraper/       # ⏳ Hämta tendrar från Opic, Visma, TED
│   ├── 05_filter/        # ⏳ AI-matchning tendrar till kund
│   ├── 06_email/         # ⏳ Email-leverans via Gmail SMTP
│   └── 07_auth/          # ⏳ Enkel authentication
├── tests/                 # Modulär test-suite
├── config.py              # Central konfiguration
└── main.py               # Integration av alla moduler
```

### Stack (100% gratis)

| Komponent | Verktyg | Kostnad |
|-----------|---------|---------|
| Hosting | GitHub Pages | $0 |
| Scraper | Python + Playwright + GitHub Actions | $0 |
| Databas | Google Sheets | $0 |
| AI | Gemini Flash (1,500 req/day) | $0 |
| Email | Gmail SMTP (100/day) | $0 |

## 📋 Byggstatus

| Modul | Status | Testar |
|-------|--------|--------|
| 01 Landing | ✅ Klar | 6/6 passed |
| 02 Onboarding | ⏳ Inte startad | - |
| 03 Database | ⏳ Inte startad | - |
| 04 Scraper | ⏳ Inte startad | - |
| 05 Filter | ⏳ Inte startad | - |
| 06 Email | ⏳ Inte startad | - |
| 07 Auth | ⏳ Inte startad | - |

## 🚀 Kom igång

### 1. Klona projektet
```bash
git clone https://github.com/your-username/tender-system.git
cd tender-system
```

### 2. Testa enskild modul
```bash
cd modules/01_landing
python3 test.py
```

### 3. Testa allt
```bash
python3 main.py
```

## 📁 Modul-specifikationer

### Modul 01: Landing Page
**Syfte:** Fånga leads (email + preferenser)
**Filer:** `index.html`, `test.py`, `README.md`
**Status:** ✅ BULLETPROOF

### Modul 02: Onboarding
**Syfte:** Registrera nya kunder
**Input:** Email, bransch, region
**Output:** Kundprofil sparad i databasen

### Modul 03: Database
**Syfte:** Lagra tendrar och kunddata
**Input:** Tender-data, kundprofiler
**Output:** CRUD-operationer på Google Sheets

### Modul 04: Scraper
**Syfte:** Hämta upphandlingar från källor
**Input:** -
**Output:** Lista med tendrar (titel, link, datum, beskrivning)

### Modul 05: Filter
**Syfte:** Matcha tendrar mot kundpreferenser
**Input:** Tender + Kundprofil
**Output:** Relevans-score (0-1)

### Modul 06: Email
**Syfte:** Skicka notiser till kunder
**Input:** Kund-email + matchade tendrar
**Output:** Mejl levererat

### Modul 07: Auth
**Syfte:** Hantera inloggning
**Input:** Email + lösenord
**Output:** Session/token

## 🧪 Testning

Varje modul har egna tester. Kör alla:

```bash
# Testa alla moduler
python3 -m pytest tests/ -v

# Testa en specifik modul
python3 modules/01_landing/test.py
```

## 📈 Framtida skalning

När systemet är stabilt kan vi byta ut:
- GitHub Actions → Hetzner VPS (€3-4/mån)
- Google Sheets → PostgreSQL
- Gmail SMTP → AWS SES (62,000 gratis/mån)

## 👥 Team

- Alexor: Product Owner, affärsbeslut
- Larry (AI-agent): Teknisk utveckling, drift

## 📝 Licens

Proprietär - Endast för internt bruk
