# Full-Stack Architecture: Government Lead Genie

## 1. Introduction

### 1.1. Document Purpose
This document outlines the comprehensive technical architecture for the Government Lead Genie platform. It serves as a blueprint for development, defining the structure, components, technologies, and interactions required to build the system as described in the Project Brief and PRD.

### 1.2. Project Overview
Government Lead Genie is an automated platform designed to bridge the gap between U.S. federal contract opportunities and capable businesses unaware of them. The system will manage the entire engagement funnel by:
1. Ingesting opportunities from SAM.gov.
2. Identifying and engaging potential prime contractors on Facebook.
3. Conducting personalized conversations using a self-learning AI.
4. Scheduling confirmed appointments in a Microsoft Outlook calendar.
5. Visualizing the entire funnel and managing leads via an Azure DevOps board, updated automatically by Power Automate.

## 2. High-Level Architecture (Revised)

### 2.1. Architectural Style
We will adopt a **Headless Automation Engine** architecture. This consists of:
- A **Modular Python Backend** that acts as a "headless" service. Its sole job is to run the core business logic and update the state in the database.
- A central **Supabase (Postgres) Database** acting as the single source of truth.
- An **Automation Layer** using **Microsoft Power Automate** to sync state changes from the database to our management interface.
- A **Management Interface** provided by **Azure DevOps Boards**, which will serve as our interactive dashboard and Kanban funnel.

### 2.2. Component Diagram (Revised)
This revised diagram shows how Azure DevOps becomes our new user interface.
```mermaid
graph TD
    subgraph "External Services"
        SAM_API[SAM.gov API]
        FB_API[Facebook Graph API]
        MS_API[Microsoft Graph API]
    end

    subgraph "Government Lead Genie Platform"
        Backend[Python Backend<br/>(Headless Automation Engine)]
        Database[(Supabase DB)]
        Automation[Microsoft Power Automate]
    end
    
    subgraph "Management Interface"
        Azure_DevOps[Azure DevOps Board]
    end

    subgraph "User"
        Admin[System Administrator]
    end

    Admin -- Manages & Monitors Funnel --> Azure_DevOps
    
    Backend -- Orchestrates --> SAM_API
    Backend -- Orchestrates --> FB_API
    Backend -- Orchestrates --> MS_API
    Backend -- Is Source of Truth For --> Database

    Database -- Triggers Flows --> Automation
    Automation -- Creates & Updates Work Items --> Azure_DevOps
```

### 2.3. Technology Stack (Revised)
| Category | Technology | Justification |
| :--- | :--- | :--- |
| **Backend** | **Python** with **FastAPI** | FastAPI is an excellent choice for its async capabilities and structured nature. |
| **Database** | **Supabase (Postgres)** | Its ability to trigger webhooks or connect to Power Automate is now even more critical. |
| **Automation Layer**| **Microsoft Power Automate**| The critical bridge between our database and the management interface. |
| **Management Interface**| **Azure DevOps Boards** | Provides a robust, pre-built Kanban interface for visualizing the lead funnel. |
| **Conversational AI**| **OpenAI GPT-4** | State-of-the-art for our conversational needs. |
| **Hosting** | **Heroku** or **AWS** | Recommended for the Python backend. |

### 2.4. Testing Strategy
- **Unit Testing (Pytest):** Each function within the Python modules will be tested in isolation, using mocks for external services.
- **Integration Testing:** We will test the interaction between our services and a test database.
- **E2E and Power Automate Testing (Manual for MVP):** The full workflow from data ingestion to the Azure DevOps board update will be tested manually.

## 3. Backend Architecture (Revised)

### 3.1. Directory Structure (Revised)
The headless backend structure is focused on services and jobs.
```
backend/
├── app/
│   ├── core/
│   │   └── config.py
│   ├── services/
│   │   ├── calendar_service.py
│   │   ├── conversation_service.py
│   │   ├── facebook_service.py
│   │   ├── learning_service.py
│   │   └── sam_service.py
│   ├── db/
│   │   ├── client.py
│   │   └── models.py
│   ├── jobs/
│   │   └── scheduler.py
│   └── main.py
├── tests/
│   └── test_services.py
├── .env.example
├── Dockerfile
└── requirements.txt
```

### 3.2. Core Modules Explained
- **`main.py`**: Entry point to start the scheduled jobs.
- **`services/`**: The heart of the application, with each module encapsulating logic for a specific external service or business process.
- **`db/`**: Manages the connection to Supabase and defines Pydantic models for data validation.
- **`core/config.py`**: Manages all environment variables and application settings.
- **`jobs/scheduler.py`**: Contains the logic for running the recurring tasks, such as checking SAM.gov.

### 3.3. Core Automation Flow: Appointment Scheduling (Refined with Conversational Logic)
This describes the step-by-step process for booking a meeting using a natural, multi-turn conversational approach.

1.  **Trigger**: The `conversation_service` determines the business owner is ready to schedule a meeting.
2.  **Fetch Full Availability (Internal Step)**: The `calendar_service` queries the Microsoft Graph API for all available slots in the next 5-7 business days and returns this list to the `conversation_service`.
3.  **Conversational-Driven Filtering**:
    *   **Step A (Week Part):** The AI asks a broad question: *"What works better for you, the beginning of this week or the end of the week?"*
    *   **Step B (Time of Day):** Based on the response, the AI asks a follow-up: *"Great. And are you generally more of a morning or afternoon person for a quick chat?"*
4.  **Propose Final Times**: The `conversation_service` filters its internal list of available slots and presents 2-3 highly relevant options.
5.  **Create Tentative Event**: Upon selection, the `calendar_service` creates a **tentative** appointment in Outlook. The backend updates the lead's status in Supabase to `'Appointment Offered'`.
6.  **Confirmation Loop**: The AI sends a message asking the user to reply 'confirm'.
7.  **Finalize Event**: Upon receiving confirmation, the `calendar_service` updates the Outlook event's status to **"Busy"**. The backend updates the lead's status in Supabase to `'Confirmed'`.

## 4. Management Interface: Azure DevOps & Power Automate

### 4.1. Vision
The entire management and monitoring of the lead funnel will occur within Azure DevOps, leveraging a powerful, existing ecosystem.

### 4.2. Kanban Funnel Implementation
-   **Columns:** The board's columns will map directly to the lead stages (e.g., `Identified`, `Engaged`, `Messaged`, `Appointment Offered`, `Confirmed`, `Disqualified`).
-   **Lead Cards:** Each lead will be a **Work Item**.

### 4.3. Automation Flow
1.  **Trigger**: A change occurs in our Supabase `leads` table.
2.  **Action**: A Power Automate flow is triggered.
3.  **Logic**: The flow will find the corresponding Work Item in Azure DevOps (or create one), update its state (move it to the correct column), and post the latest conversation log as a comment. 