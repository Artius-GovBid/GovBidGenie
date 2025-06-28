# Project Analysis: GovBidGenie

This document provides a comprehensive analysis of the GovBidGenie project, including its architecture, technology stack, database schema, API endpoints, and key business logic.

## 1. High-Level Project Overview

- **Primary Language:** Python
- **Top-Level Directories:** `backend`, `supabase`
- **Key Components:**
    - **`backend/`**: A containerized FastAPI web application that serves as the primary API. It includes a service layer for business logic, database models, and API endpoints.
    - **`supabase/`**: Contains Supabase-specific configurations, including database migrations and serverless Edge Functions.

## 2. Technology Stack

The backend application relies on a modern Python technology stack:

- **Web Framework:** FastAPI
- **ASGI Server:** Uvicorn
- **Database ORM:** SQLAlchemy
- **Database Adapter:** psycopg2-binary (for PostgreSQL)
- **HTTP Client:** requests
- **Environment Management:** python-dotenv

## 3. Database Schema

The application uses a PostgreSQL database with two primary tables defined via SQLAlchemy ORM:

### `opportunities` Table
Represents a government contract opportunity, typically sourced from SAM.gov.
- `id` (Integer, Primary Key)
- `sam_gov_id` (String, Unique)
- `title` (Text)
- `url` (String)
- `agency` (String)
- `posted_date` (DateTime)
- `created_at` (DateTime)

### `leads` Table
Represents a potential sales lead generated from an opportunity.
- `id` (Integer, Primary Key)
- `source` (String)
- `status` (String, Default: 'Identified')
- `azure_devops_work_item_id` (Integer)
- `business_name` (String)
- `facebook_page_url` (String)
- `created_at` (DateTime)
- `last_updated_at` (DateTime)
- `opportunity_id` (Integer, Foreign Key to `opportunities.id`)

## 4. API Endpoints

The API is defined directly within `backend/app/main.py`:

- **`POST /api/v1/leads`**: 
  - **Purpose:** Creates a new `Lead` and its associated `Opportunity` (if new).
  - **Process:** It receives opportunity data, creates the relevant database records, and then calls the `DevOpsService` to create a work item in Azure DevOps.

- **`GET /`**: 
  - **Purpose:** A health check endpoint to confirm the service is running.

## 5. Business Logic & Integrations

The core business logic is handled in the `services` directory and through database triggers.

### `DevOpsService` (Python Backend)
- **Purpose:** Manages integration with the Azure DevOps (ADO) API.
- **Key Functions:**
    - `create_work_item()`: Creates a new "Issue" work item in ADO when a lead is created.
    - `update_work_item_status()`: Updates the state of an ADO work item when the lead's status changes in the application.
- **Authentication:** Requires `ADO_ORG_URL` and `ADO_PAT` environment variables.

### `handle_lead_update` (Supabase Database Trigger)
- **Purpose:** Automates actions directly within the database when a lead is created or its status is updated.
- **Process:**
    1.  Securely fetches Supabase secrets from the Vault.
    2.  Fires on `INSERT` or `UPDATE` events on the `leads` table.
    3.  Makes an authenticated POST request to a Supabase Edge Function named `devops-integration`.
- **Note:** This suggests a dual-integration pattern with Azure DevOps, with one path through the Python backend and another through a Supabase Edge Function triggered by database changes.

## 6. Summary of Architecture

The GovBidGenie project is a well-structured, modern web application. It uses a Python/FastAPI backend to manage data and a Supabase-powered PostgreSQL database for persistence. A key feature is its deep integration with Azure DevOps for project management, which is implemented both in the application's service layer and directly at the database level using triggers and Edge Functions. This dual-integration strategy provides robust automation for tracking leads and opportunities. 