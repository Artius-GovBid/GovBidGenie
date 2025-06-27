# Government Lead Genie

Government Lead Genie is a fully automated lead generation, outreach, and appointment booking platform designed to secure prime contractors for federal projects. The system identifies relevant contract opportunities on SAM.gov, engages potential partners on Facebook, holds AI-driven conversations to qualify interest, and books confirmed appointments directly into a Microsoft Outlook calendar.

The primary problem it solves is the complete automation of the time-consuming, manual process of identifying, engaging, and scheduling meetings with potential prime contractors for U.S. federal government opportunities.

## Core Features

- **Automated Opportunity Sourcing**: Continuously scans SAM.gov for new contract opportunities.
- **AI-Powered Engagement**: Uses a sophisticated conversational AI (GPT-4) to engage potential partners on Facebook with personalized, context-aware messaging.
- **Intelligent Scheduling**: Integrates directly with Microsoft Outlook to read availability and book confirmed 15-minute appointments.
- **Self-Learning Model**: Incorporates a feedback loop to analyze past conversations and improve outreach strategies over time.
- **Kanban-Style Management**: Leverages Azure DevOps Boards as the primary management interface, with lead progression and conversation logs automatically updated by Power Automate.

## Architecture Overview

The platform is built with a decoupled frontend/backend architecture:

- **Backend**: A modular monolith built with **Python** and **FastAPI**.
- **Frontend**: An admin dashboard built with **React**.
- **Database**: **Supabase (Postgres)** serves as the single source of truth.
- **Automation Layer**: **Microsoft Power Automate** connects database changes to Azure DevOps.
- **Hosting**: The backend is designed for **Heroku** or **AWS**, with the frontend on **Vercel** or **Netlify**.

## Getting Started

### Prerequisites

- Python 3.9+
- Node.js & npm (for frontend development)
- Access to a Supabase project
- API keys for:
  - OpenAI
  - Facebook Graph API
  - Microsoft Graph API
- An Azure DevOps project and a Power Automate license.

### Installation

1. **Clone the repository:**

    ```sh
    git clone https://github.com/Artius-GovBid/GovBidGenie.git
    cd GovBidGenie
    ```

2. **Backend Setup:**

    ```sh
    cd backend
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cp .env.example .env
    # Add your API keys and secrets to the .env file
    ```

3. **Frontend Setup (TBD):**

    ```sh
    cd ../frontend
    npm install
    # ... further setup instructions ...
    ```

### Running the Application

**To run the backend:**

```sh
cd backend
uvicorn app.main:app --reload
```

**To run the scheduled jobs:**

The application uses a scheduler to periodically fetch data from SAM.gov. This will be run as part of the main backend process.

## Project Status

This project is currently in the architectural design phase. The backend and frontend structures have been defined, and development is beginning.
