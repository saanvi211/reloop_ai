# ReLoop AI

ReLoop AI is an AI-assisted e-waste identification and circular recovery platform. The project now includes a **Streamlit frontend** backed by a **FastAPI + SQLite API**.

Assessments, identification results, recycling history, routes, profile details and preferences persist through the API. If the backend is unreachable, the frontend falls back to local demo data so the interface remains usable.

## What is included

- Premium environmental-tech design system with emerald, white and charcoal tones
- Nine connected pages with grouped sidebar navigation
- FastAPI backend with authentication, assessments, history, centres and analytics
- Account-scoped SQLite persistence
- Offline demo fallback when the API is unavailable
- Guided circular flow: Identify, Assess and Route
- Interactive Folium map of fictional Bengaluru collection centres
- Environmental impact dashboard with CSV export
- Settings for profile, preferences, appearance and privacy
- Accent switching between Emerald, Forest and Teal
- Backend regression tests

## Pages

| Section | Page | Purpose |
| --- | --- | --- |
| Overview | Home | Landing page, impact snapshot and circular flow entry points |
| Overview | Dashboard | Impact summary, trends, category mix, activity and next pickup |
| Circular flow | Identify E-Waste | Upload or describe a device and create an identification |
| Circular flow | Assessment | Recyclability score, material estimate, value and guidance |
| Circular flow | Recommendations | Best route, preparation steps, pickup and alternatives |
| Circular flow | Nearby Centres | Filter and explore fictional drop-off points across Bengaluru |
| Insights | History | Search, filter and export assessment and recovery records |
| Insights | Environmental Impact | Period filters, carbon, material recovery, device mix and insights |
| Account | Settings | Profile, notifications, privacy, appearance and session reset |

## Architecture

```text
GenAI_proj/
├── app.py                  # Streamlit entry point and navigation
├── requirements.txt
├── assets/                 # CSS, logos
├── components/             # Reusable UI, chart and map helpers
├── data/                   # Seeded demonstration data
├── styles/                 # Theme and accent handling
├── utils/
│   ├── api_client.py       # Typed HTTP client for the ReLoop API
│   ├── flow.py             # API-backed session/user/history helpers
│   └── ...
├── views/                  # Streamlit pages
└── backend/
    ├── main.py             # FastAPI application
    ├── routers/            # Auth, users, assessments, history, centres, etc.
    ├── services/           # Business logic and seeding
    ├── models.py           # SQLAlchemy models
    ├── database.py
    ├── config.py
    └── tests/              # Backend regression suite
```

## Dependencies

- Python 3.10+
- Streamlit, Plotly, Pandas, NumPy, Folium, streamlit-folium
- FastAPI, Uvicorn, SQLAlchemy, Pydantic, python-multipart, Pillow
- HTTPX and pytest for the API client and tests

## Setup

From the project folder:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

On macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Run

Start the backend in one terminal:

```powershell
uvicorn backend.main:app --reload --port 8000
```

The API is available at `http://127.0.0.1:8000/api` and interactive docs at `http://127.0.0.1:8000/docs`. The database is created and seeded automatically on startup.

Start the frontend in another terminal:

```powershell
streamlit run app.py
```

The app opens at `http://localhost:8501`. If `streamlit` is not on your PATH, use `python -m streamlit run app.py`.

## Demo account

```text
Email:    demo@reloop.example
Password: reloop123
```

The frontend logs in with these credentials by default.

## Configuration

| Variable | Default | Purpose |
| --- | --- | --- |
| `RELOOP_API_URL` | `http://127.0.0.1:8000/api` | Backend URL used by the frontend |
| `DEMO_EMAIL` | `demo@reloop.example` | Default frontend login email |
| `DEMO_PASSWORD` | `reloop123` | Default frontend login password |
| `DATABASE_URL` | `sqlite:///reloop.db` | Backend database connection |
| `UPLOAD_DIR` | `backend/uploads` | Identification image storage |

When the API cannot be reached, the frontend shows a status note in the sidebar and continues with local demonstration data.

## Tests

```powershell
pytest backend/tests -q
```

## Notes

- Navigation is defined in `app.py` using `st.navigation`.
- Custom HTML uses `st.html()` so indented markup is not parsed as Markdown code blocks.
- Collection partners are fictional demonstration records and are labelled as such in the UI.
- Identification and impact values are deterministic estimates, not verified measurements.
