# Lifeboat Familiarisation Web App

## Overview

Single-page web application for generating lifeboat familiarisation attendance lists. Compares personnel requiring familiarisation against current Personnel On Board (POB) and produces a printable PDF notice.

## Tech Stack

| Component | Technology |
|-----------|------------|
| Framework | **Flask** (lightweight, perfect for single-page apps) |
| Frontend CSS | **Bulma** (modern, clean styling) |
| JavaScript | Vanilla JS (drag-and-drop file handling) |
| Excel Parsing | **openpyxl** (read xlsx files) |
| PDF Generation | **WeasyPrint** (HTML-to-PDF with CSS styling) |
| Python Version | 3.14+ |
| Containerization | **Docker** (handles WeasyPrint system deps) |

## Containerization

### Why Docker?

WeasyPrint requires system libraries (Pango, Cairo, GDK-PixBuf, fontconfig) that vary across operating systems. Docker ensures:
- Consistent environment across development and production
- No manual system dependency installation
- Easy deployment to any Docker-capable host

### Docker Files

**Dockerfile**
```dockerfile
FROM python:3.14-slim

# Install WeasyPrint system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    libffi-dev \
    shared-mime-info \
    fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 10000

CMD ["python", "app.py"]
```

**docker-compose.yml**
```yaml
services:
  web:
    build: .
    ports:
      - "10000:10000"
    volumes:
      - ./uploads:/app/uploads  # Optional: persist uploads
    environment:
      - FLASK_ENV=production
    restart: unless-stopped
```

### Docker Commands

| Command | Description |
|---------|-------------|
| `docker compose up --build` | Build and run the app |
| `docker compose up -d` | Run in background (detached) |
| `docker compose down` | Stop and remove containers |
| `docker compose logs -f` | Follow container logs |

### Development vs Production

- **Development:** Mount source as volume for hot-reload
- **Production:** Copy source into image, use gunicorn/uvicorn

## Application Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    SINGLE PAGE APP                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌─────────────────────┐    ┌─────────────────────┐       │
│   │  DROP ZONE 1        │    │  DROP ZONE 2        │       │
│   │                     │    │                     │       │
│   │  Familiarisation    │    │  Current POB        │       │
│   │  Required List      │    │  List               │       │
│   │  (.xlsx)            │    │  (.xlsx)            │       │
│   └─────────────────────┘    └─────────────────────┘       │
│                                                             │
│              ┌─────────────────────┐                        │
│              │   GENERATE PDF      │                        │
│              └─────────────────────┘                        │
│                        │                                    │
│                        ▼                                    │
│              ┌─────────────────────┐                        │
│              │  Download / Print   │                        │
│              │  PDF Button         │                        │
│              └─────────────────────┘                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Processing Logic

1. **Parse Familiarisation List** - Extract names and expiry dates of personnel requiring familiarisation
2. **Filter by Due Date** - Include only personnel where:
   - Expiry date is "Required" (first-timers), OR
   - Expiry date is <= today (overdue or due today)
3. **Parse POB List** - Extract names of personnel currently on board
4. **Cross-Reference** - Find personnel who are both:
   - On the filtered familiarisation list (due or first-timer)
   - Currently on board (in POB)
5. **Generate PDF** - Create attendance notice with matched personnel

## PDF Template Design

### Visual Theme: "Maritime Notice"

- **Color Palette:**
  - Deep navy blue (#1a3a5c) - headers and borders
  - Ocean teal (#2d7a9c) - accents
  - Clean white (#ffffff) - background
  - Dark charcoal (#2c3e50) - body text

- **Header Section:**
  - Twin-fall lifeboat illustration (SVG or PNG)
  - Official-looking notice banner
  - Title: **"PLEASE ATTEND LIFEBOAT 1 FOR FAMILIARISATION AFTER THE DRILL"**

- **Body Section:**
  - Date and vessel info
  - Clean table with personnel names
  - Checkbox column for attendance tracking

- **Footer:**
  - Safety notice / compliance text
  - Page numbering if multiple pages

### PDF Layout Sketch

```
┌─────────────────────────────────────────────────────────────┐
│  ⚓  [TWIN-FALL LIFEBOAT ILLUSTRATION]  ⚓                   │
│━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━│
│                                                             │
│     PLEASE ATTEND LIFEBOAT 1 FOR FAMILIARISATION           │
│                  AFTER THE DRILL                            │
│                                                             │
│━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━│
│                                                             │
│  Date: ____________           Vessel: ________________      │
│                                                             │
│  ┌─────┬────────────────────────────┬──────────────────┐   │
│  │  #  │  Name                      │  Attended ☐      │   │
│  ├─────┼────────────────────────────┼──────────────────┤   │
│  │  1  │  John Smith                │       ☐          │   │
│  │  2  │  Jane Doe                  │       ☐          │   │
│  │  3  │  ...                       │       ☐          │   │
│  └─────┴────────────────────────────┴──────────────────┘   │
│                                                             │
│─────────────────────────────────────────────────────────────│
│  Safety First • Maritime Compliance Notice                  │
└─────────────────────────────────────────────────────────────┘
```

## Project Structure

```
Lifeboat/
├── app.py                    # Flask application entry point
├── Dockerfile                # Container image definition
├── docker-compose.yml        # Container orchestration
├── .dockerignore             # Files excluded from Docker build
├── requirements.piptools     # Top-level dependencies
├── requirements.txt          # Compiled dependencies (via uv)
├── pytest.ini               # Test configuration
├── ruff.toml                # Linting/formatting config
├── plan.md                  # This file
├── static/
│   ├── css/
│   │   └── style.css        # Custom styles (Bulma extensions)
│   ├── js/
│   │   └── main.js          # Drag-drop and form handling
│   └── images/
│       └── lifeboat.svg     # Twin-fall lifeboat illustration
├── templates/
│   ├── index.html           # Main page template
│   └── pdf_template.html    # PDF generation template
├── services/
│   ├── __init__.py
│   ├── excel_parser.py      # xlsx file parsing logic
│   └── pdf_generator.py     # PDF generation with WeasyPrint
└── tests/
    ├── __init__.py
    ├── test_excel_parser.py
    └── test_pdf_generator.py
```

## Dependencies

### requirements.piptools

```
flask>=3.0
openpyxl>=3.1
weasyprint>=62.0
```

### Development dependencies (requirements-development.piptools)

```
pytest>=8.0
ruff>=0.4
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Serve main page with upload form |
| POST | `/generate` | Accept two xlsx files, return PDF |

## Expected Excel Formats

### Familiarisation Required List
Minimum columns (flexible header matching):
- Name or Full Name
- ID or Employee ID (optional, for matching)

### POB List
Minimum columns:
- Name or Full Name
- ID or Employee ID (optional, for matching)

**Matching Logic:** Primary match by name (case-insensitive, trimmed). If ID columns exist, use as secondary confirmation.

## Implementation Steps

1. **Scaffold project structure** - Create directories and config files
2. **Set up Flask app** - Basic routes and configuration
3. **Build frontend** - HTML with Bulma, drag-drop JS
4. **Implement Excel parser** - Read and normalize xlsx data
5. **Implement PDF generator** - WeasyPrint with styled template
6. **Create lifeboat artwork** - SVG illustration for PDF header
7. **Wire everything together** - Full integration
8. **Add error handling** - User-friendly error messages
9. **Containerize** - Create Dockerfile and docker-compose.yml
10. **Test** - Unit tests for parser and generator

## Sample Excel Data for Testing

### familiarisation_required.xlsx
| Name | Department |
|------|------------|
| John Smith | Deck |
| Jane Doe | Engine |
| Bob Wilson | Catering |

### pob.xlsx
| Name | Cabin | Role |
|------|-------|------|
| Jane Doe | A-12 | 2nd Engineer |
| Mike Brown | B-05 | AB |
| Bob Wilson | C-22 | Chef |

### Expected Output
PDF should list: **Jane Doe**, **Bob Wilson** (present on both lists)

---

## Notes

- WeasyPrint system dependencies (Pango, Cairo) handled by Docker
- PDF designed for A4 paper, landscape optional for long lists
- Consider adding vessel name input field for PDF customization
