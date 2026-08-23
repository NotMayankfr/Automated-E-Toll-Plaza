# Automated E-Toll Plaza

An intelligent electronic toll collection prototype that simulates automated vehicle identification, optimized route selection, payment handling, and toll analytics.

## Highlights

- Reduces average processing time by more than 70% in the default simulation by automating identification and payment flow.
- Uses Dijkstra and A* to recommend cost- and time-optimized routes.
- Exposes a RESTful payment API with transport security enabled for local development.
- Tracks toll usage trends and pricing signals through a lightweight analytics dashboard.
- Includes simulation-driven testing and a companion C++ implementation of routing logic.

## Project Structure

- `src/etoll/routing.py`: Graph model, Dijkstra, and A*.
- `src/etoll/simulation.py`: Vehicle flow simulation, toll queue logic, and metrics.
- `src/etoll/payment_api.py`: Flask payment service with HTTPS support.
- `src/etoll/security.py`: Basic secure storage helpers for user and payment metadata.
- `dashboard.py`: Streamlit analytics dashboard for simulation outputs.
- `cpp/route_engine.cpp`: C++ route-planning reference implementation.
- `tests/`: Unit tests for routing and simulation behavior.

## Quick Start

```bash
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1

pip install -r requirements.txt
pip install -e .

# Generate reproducible dashboard data (default: 150 vehicles, seed=42).
python run_simulation.py

# In separate terminals, start the HTTPS payment API and analytics dashboard.
python -m flask --app etoll.payment_api run --cert=adhoc --port 8443
streamlit run dashboard.py
```

Open `https://127.0.0.1:8443/health` and accept the local development certificate warning. The dashboard command prints its local URL.

## Verify the Project

```bash
pytest -q
g++ -std=c++17 -Wall -Wextra -pedantic cpp/route_engine.cpp -o /tmp/etoll-route-engine
/tmp/etoll-route-engine
```

To try an end-to-end payment locally after starting the API:

```bash
curl -k -X POST https://127.0.0.1:8443/register_vehicle \
  -H "Content-Type: application/json" \
  -d '{"vehicle_id":"VH-DEMO","owner_name":"Demo User","tag_id":"TAG-DEMO","vehicle_class":"car"}'

curl -k -X POST https://127.0.0.1:8443/process_payment \
  -H "Content-Type: application/json" \
  -d '{"vehicle_id":"VH-DEMO","route":["Entry-North","Hub-East","Airport"],"amount":6.50,"payment_token":"demo-token"}'
```

## API Endpoints

- `GET /health`
- `POST /register_vehicle`
- `POST /process_payment`
- `GET /transactions`

## Simulation Notes

The default scenario compares manual toll processing against automated identification plus prepaid settlement. Metrics are exported to `data/simulation_results.json`, which the dashboard reads for charts and KPI cards.

## Security Notes

- TLS is enabled in development through Flask's ad hoc certificate mode; use a managed certificate and a production WSGI server before deployment.
- Sensitive identifiers are hashed before storage in local JSON artifacts.
- The project is designed as a prototype and can be extended with production-grade tokenization, HSM-backed key management, and PCI-compliant payment flows.
