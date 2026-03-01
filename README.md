# Radio Fleet Simulator

A Python-based simulator for tracking a fleet of radios with dynamic movement, battery drain, and signal strength simulation.

## Prerequisites

- Python 3.14+
- PostgreSQL database (e.g., Neon.tech)

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd "Radio Simulator"
```

### 2. Create and Activate Virtual Environment

```bash
python -m venv venv
# Windows
.\venv\Scripts\activate
# Linux/macOS
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Variables

Create a `.env` file from the provided template:

```bash
cp .env.example .env
```

Edit the `.env` file and provide your `DATABASE_URL`.

### 5. Initialize Database

Run the database generation script to create tables and populate them with initial data:

```bash
python -m scripts.generate_db
```

### 6. Run the Simulator

Start the radio simulation:

```bash
python -m app.main
```

## Features

- **Dynamic Movement**: Radios move within predefined zones and routes.
- **Battery Simulation**: Realistic battery drain over time.
- **Signal Strength**: Dynamically calculated based on distance from base station.
- **Geofencing**: Detection of radios moving outside their assigned zones.
