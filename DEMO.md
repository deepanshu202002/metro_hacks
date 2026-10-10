# DevFest Gandhinagar 2023 - Metro Hacks (PS-08) Demo Script
**Team**: One Journey
**Problem Statement**: PS-08 "One City, One Journey"
**Pitch Duration**: 2 Minutes

## Setup
1. Unplug wifi/mobile data. Ensure the laptop is 100% OFFLINE.
2. Run `npm run demo` to start both the Python FastApi server and the Next.js frontend locally.
3. Open `http://localhost:3000?demo=1` in your browser.

## The Pitch

### 0:00 - 0:30 (The Problem & The Offline-First Paradigm)
- "Welcome to One Journey. Ahmedabad's transit network is growing, but it's fragmented across GMRC (Metro), BRTS, and AMTS."
- "A user travelling from Sabarmati to a distant AMTS stop shouldn't have to buy three different tickets, nor should they need constant 5G to plan a route."
- **Action**: Show that Wi-Fi is OFF. 
- "Our entire progressive web app, including search, routing algorithms, and SVG map generation, works fully offline. We process the graph locally."

### 0:30 - 1:15 (Multi-Operator Routing & Fare Splitting)
- **Action**: Click the "Sabarmati -> BRTS Hub" quick chip on the planner.
- "We search Sabarmati to BRTS Hub. It calculates the fastest multi-modal route."
- **Action**: Expand the timeline to show the transfer walking distance.
- "Notice the seamless transfer. More importantly, notice the 'Integrated Fare' badge. Instead of paying two separate fares, the user pays one integrated, discounted fare."
- **Action**: Scroll down in the expanded card to show the **Operator Settlement (PPP)** table.
- "But how do operators get their money? We've built an on-device clearing simulator. A clearing entity takes a 1.5% fee, and the rest is distributed pro-rata based on distance and leg fare."

### 1:15 - 1:45 (The Ecosystem view)
- **Action**: Navigate to `http://localhost:3000/settlement` or the hidden Settlement Dashboard.
- "This dashboard aggregates 200 synthetic trips run offline."
- "It shows total integrated revenue and how the pool is split among operators (Metro, BRTS, AMTS) without requiring an overarching monopolistic AFC system."
- "We use 'One City, One Journey' to incentivize transfers through a transfer bonus pool."

### 1:45 - 2:00 (Q&A & Wrap Up)
- "We've essentially decoupled the user experience (One Ticket) from the underlying operator fragmentation."
- "Everything you saw today runs entirely locally, ready for deployment in the real world."

**End of Demo**
