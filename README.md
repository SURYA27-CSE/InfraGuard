# InfraGuard

InfraGuard is a real-time infrastructure monitoring dashboard. It collects live CPU, memory, disk, and process information from the local computer, then presents alerts, recommendations, risk scores, and incident history in a web dashboard.

## Features

- Live CPU, memory, and disk monitoring
- Detection of high resource usage
- Process health table with CPU and memory usage
- Risk score and risk-level assessment
- Alerts and remediation recommendations
- Incident history
- REST API for system metrics

## Technology

- Python
- FastAPI
- Uvicorn
- psutil
- HTML, CSS, and JavaScript

## Run locally

1. Clone the repository.

2. Create and activate a Python virtual environment.

3. Install the required packages:

```powershell
.\.venv\Scripts\python.exe -m pip install -r .\backend\requirements.txt
```

4. Start the application:

```powershell
.\.venv\Scripts\python.exe -m uvicorn main:app --app-dir .\backend --reload
```

5. Open the dashboard:

```text
http://127.0.0.1:8000
```

## API endpoints

| Endpoint | Description |
| --- | --- |
| `/` | InfraGuard dashboard |
| `/metrics` | Live system metrics in JSON format |
| `/docs` | Interactive FastAPI API documentation |

## Project structure

```text
InfraGuard/
├── backend/
│   ├── frontend/
│   │   └── index.html
│   ├── agent.py
│   ├── main.py
│   └── requirements.txt
├── .gitignore
└── README.md
```

## Note

InfraGuard reports live information from the computer running the application. Do not publish screenshots or logs containing sensitive system details.