```markdown
# 🌌 Parkham: The Conflux of Conveyances - V1

A multi-dimensional nexus for the management of terrestrial conveyances, forged through the arcane arts of **Flask**, **Jinja2**, **Bootstrap**, and **SQLite** (bound by the SQLAlchemy ORM). This grand endeavor is a testament to the **Modern Application Development I (MAD1)** course.

---

## 📌 The Grand Design

This ethereal web-construct permits:
- **Overseers** to command the parking domains and discern the status of each resting place.
- **Wayfarers** to register their presence, claim their temporary sanctuaries, and chronicle their journeys and tributes.

All designated resting places are solely for **quad-wheeled conveyances**, and the allocation of these sanctuaries is guided by an unseen, automated hand.

---

## 🧰 The Arcane Arts Employed

| Layer           | Ancient Script / Foundational Rune |
|-----------------|------------------------------------|
| Backend Weaving | Flask, Flask-SQLAlchemy            |
| Frontend Glyphs | Jinja2, HTML, CSS, Bootstrap       |
| Knowledge Vault | SQLite (conjured by code, not by hand) |

---

## 🔐 Roles and Edicts

### 👨‍💼 The Grand Overseer
- No initiation rites required (bound within the core essence).
- Conjure, modify, or dissolve Parking Domains.
- Automatically manifest resting places according to domain capacity.
- Gaze upon all registered Wayfarers.
- Witness all claims and the presence of all conveyances.

### 👤 The Wayfarer
- Undertake the rites of Registration/Access.
- Choose a Parking Domain (with automated sanctuary allocation).
- Claim/Release a resting place.
- Peruse personal journey chronicles and tribute summaries.

---

## 🗃️ Data Constructs (Ethereal Overview)

1.  **Wayfarer**
    -   `id`, `name`, `email`, `password`, `pincode`, `created_at`

2.  **ParkingDomain**
    -   `id`, `location_name`, `address`, `pincode`, `price`, `max_spots`, `created_at`

3.  **RestingPlace**
    -   `id`, `domain_id (FK)`, `status`

4.  **Claim**
    -   `id`, `place_id (FK)`, `wayfarer_id (FK)`, `in_time`, `out_time`, `total_cost`, `status`

> The Grand Overseer's essence is woven into the Knowledge Vault upon its initial manifestation.

---

## 📁 Architectural Scrolls

```
project/
│
├── app.py                 # The Main Conflux Orb
├── models.py              # Ethereal Data Schemas
├── routes.py              # Pathways of Interaction
├── extensions.py          # Auxiliary Conduits
├── requirements.txt       # Necessary Components
├── README.md              # This Chronicle
├── instance/              # The Knowledge Vault's Abode
├── static/                # Visual Glyphs and Styles
├── templates/             # Ethereal Display Constructs
├── .venv/                 # Temporal Energy Field (excluded from Git)
└── .gitignore
```

---

## 🧪 The Ritual of Activation (Local Manifestation)

```bash
# Clone the ancient scrolls & enter the sacred grounds
git clone <your-private-repo-url>
cd project

# Forge & Awaken the temporal energy field
python3 -m venv .venv
source .venv/bin/activate

# Install the necessary components
pip install -r requirements.txt

# Invoke the Conflux Orb
python app.py
```

The Knowledge Vault and the Grand Overseer's essence are manifested automatically upon the first invocation.

---

## ✅ Progress Markers

*   Trial 0: GitHub Repository Forged
*   Trial 1: Ethereal Data Schemas & Constructs Defined
*   Trial 2: Access Rites & Role-Based Edicts Established
*   Trial 3: Grand Overseer's Command Nexus + Domain/Place Management
*   Trial 4: Wayfarer's Nexus + Claiming System
*   Trial 5: Chronicle of Journeys Summary
*   Trial 6: Tribute Calculation Module
```