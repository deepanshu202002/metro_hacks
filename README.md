# 🚇 One Journey (એક યાત્રા)
**DevFest Gandhinagar 2026 - Metro Hacks Submission**

### Problem Statement: PS-08 "One City, One Journey"
Ahmedabad and Gandhinagar have multiple transit operators (GMRC Metro, BRTS, AMTS) with separate ticketing systems and confusing transfers. 
**Our Solution**: A unified, offline-first multimodal journey planner that seamlessly combines Metro, BRTS, AMTS, and Feeder Shuttles into a single route, offering **ONE combined fare estimate** and walking transfer times.

---

## 🌟 Key Features Built for the Hackathon

1. **Multimodal Routing Engine (Offline)**
   - Custom Dijkstra-based routing engine running entirely locally (no external APIs).
   - Combines GMRC Metro (Red, Blue, Yellow, Violet lines), BRTS, and AMTS.
   - Calculates combined fares, smart card discounts, and transfer walking times.
   - Includes real-world transit quirks (e.g., Direct APMC-GIFT City trains, free GIFT City corporate shuttles).

2. **Smart Geolocation & POI Search**
   - Built-in fuzzy search resolver! Users don't need to know exact station names.
   - 15+ major Points of Interest (POIs) added (e.g., *Akshardham Temple, Gujarat University, Airport*).
   - Searching a POI automatically maps to GPS coordinates, routes to the nearest metro station, and injects a "Walking" leg.

3. **Offline-First PWA (Progressive Web App)**
   - Built with Next.js, Vite, and React. 
   - All maps are drawn as lightweight SVG schematic networks (zero dependency on online map tiles).
   - Designed to run seamlessly even on a moving train with patchy network.

4. **Operator Analytics Dashboard (Bonus)**
   - Advanced Insights Dashboard securely separated for Operators (`/operator`).
   - Visualizes simulated corridor flows, interchange bottlenecks, and fare-splitting (PPP) models between GMRC, BRTS, and AMTS operators.

---

## 🛠️ Tech Stack
- **Frontend**: Next.js (React), TypeScript, Tailwind CSS, Lucide Icons.
- **Backend**: FastAPI (Python), Uvicorn.
- **Data**: JSON-based local datasets (`data/stations.json`, `data/edges.json`).

---

## 🚀 How to Run Locally

### 1. Start the Backend (FastAPI)
```bash
cd backend
python -m venv venv

# On Windows:
.\venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

### 2. Start the Frontend (Next.js)
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:3000` in your browser. 

*(Note: Ensure you allow popups or bypass CORS if running in a strict environment, though the backend is pre-configured with open CORS for development).*

---

## 📊 Assumptions & Synthetic Data
As per the 2-hour hackathon constraints:
- **Synthetic Data**: Live timetables, exact BRTS/AMTS coordinates, and live crowd data are synthesized via probabilistic models in `/backend/services/routing.py`. They are marked with a "Demo data" badge in the UI.
- **Fare Split Model**: The PPP settlement between operators uses a pro-rata distance calculation which is simulated for demonstration purposes.
- **No Database**: For extreme portability, all graph logic runs in-memory.

---
*Built with ❤️ for DevFest Gandhinagar*
