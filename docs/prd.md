# Government Lead Genie Product Requirements Document (PRD)

## 1. Goals and Background Context

### 1.1. Goals

- To create a fully automated platform that converts raw government contract opportunities into confirmed sales appointments with qualified, previously unaware businesses.
- To eliminate the manual labor associated with lead generation, outreach, and scheduling in the government contracting space.
- To provide a seamless, personalized, and valuable experience for the target business owners, making them aware of a new and lucrative revenue stream.
- To build a scalable system, including a self-learning AI and an admin dashboard, that can manage the entire engagement funnel from end to end.

### 1.2. Background Context

The U.S. federal government represents a massive, multi-billion dollar market. However, for the vast majority of small and medium-sized businesses, it is an invisible and inaccessible one. They are unaware that the government is a potential buyer for their services. This project, Government Lead Genie, was conceived to bridge this awareness and complexity gap.

The platform will proactively find contract opportunities, identify suitable businesses on Facebook, and use a sophisticated conversational AI to engage them. By automating the entire process—from initial contact to a confirmed meeting in an Outlook calendar—it aims to unlock a significant new market for these businesses while creating a highly efficient, automated business development engine.

### 1.3. Change Log

| Date | Version | Description | Author |
| :--- | :--- | :--- | :--- |
| 2024-07-26 | 1.0 | Initial draft of the PRD | PM Bot |

## 2. Requirements

### 2.1. Functional Requirements

- **FR1:** The system must periodically fetch new contract opportunities from the SAM.gov API.
- **FR2:** The system must perform searches on Facebook to identify potential business partners based on keywords from the contract opportunities.
- **FR3:** The system must, via a connected Facebook Business Page, be able to like, comment on, and share posts made by a target business.
- **FR4:** The system must initiate and manage a direct message conversation with a business that responds to the initial engagement.
- **FR5:** The conversation must be powered by a conversational AI capable of generating dynamic, context-aware, and non-generic responses.
- **FR6:** The system must connect to a Microsoft Outlook calendar to read availability and identify open appointment slots.
- **FR7:** The system must be able to write new tentative appointments to the Microsoft Outlook calendar.
- **FR8:** The system must manage a confirmation loop via direct message, ensuring the business owner explicitly confirms their attendance before finalizing the appointment.
- **FR9:** The system must automatically send follow-up messages if a business owner is unresponsive or does not show up for a meeting.
- **FR10:** The system must provide a mechanism for business owners to reschedule their appointment through the conversational AI.
- **FR11:** The conversational AI must have a self-learning mechanism to analyze past conversation outcomes and refine its strategies over time.
- **FR12 (Revised):** The system must integrate with the Azure DevOps REST API to programmatically create and update work items.
- **FR13 (Revised):** The state of the outreach funnel must be represented by work items on a specific Azure Board, with lead progression shown by moving work items across columns.
- **FR14 (Revised):** The system must append conversation logs as comments to the appropriate work item in Azure DevOps.
- **FR15 (New):** The system will require credentials (like a Personal Access Token) with sufficient permissions to interact with the target Azure DevOps project.
- **FR16 (New):** The system will be architected so that changes in the Supabase database (e.g., a new lead, a status change) trigger database webhooks or functions.
- **FR17 (New):** These database triggers/webhooks will be responsible for creating, updating, and moving work items on the Azure DevOps board.
- **FR18 (New):** The trigger/webhook payload will contain conversation logs and other relevant data to be posted as comments to the appropriate work item in Azure DevOps.

### 2.2. Non-Functional Requirements

- **NFR1:** The conversational AI's persona must be consistently authentic, personal, and professional, avoiding any language that feels robotic or generic.
- **NFR2:** The system must securely store and manage all API keys, access tokens, and other credentials.
- **NFR3:** The admin dashboard must be responsive and have a page load time of under 3 seconds for all primary views.
- **NFR4:** The system's architecture must be scalable to handle an increasing volume of concurrent conversations and API calls.
- **NFR5:** The system must operate within the terms of service and rate limits of the Facebook Graph API and Microsoft Graph API.
- **NFR6:** All user data and conversation logs must be handled with strict privacy controls.
- **NFR7:** The backend services must be reliable and include error handling and logging to ensure fault tolerance.

## 3. Management Interface: Azure DevOps Integration

### 3.1. Overall Vision

Instead of a custom-built dashboard, the system will use **Azure DevOps** as its primary management interface. The Python backend will be responsible for creating and updating work items in an Azure DevOps project, effectively turning Azure Boards into the "mission control" for the lead generation funnel.

### 3.2. Kanban Funnel Implementation

- **Columns:** The board's columns will map directly to the lead stages (e.g., "Identified," "Engaged," "Messaged," "Appointment Set," "Confirmed").
- **Lead Cards:** Each lead will be represented as a **Work Item** (e.g., a "User Story" or a custom "Lead" type). The backend will automatically move these cards across the board as the lead progresses through the funnel.
- **Data Representation:**
  - **Lead Details:** Key information about the lead (business name, contact info, relevant contract) will be stored in the fields of the Azure DevOps Work Item.
  - **Conversation Logs:** The full transcript of the conversation with a lead will be added to the **"Discussion" or "Comments" section** of the corresponding Work Item, providing a complete historical record.

## 4. Technical Considerations

### 4.1. Repository Structure

A **monorepo** containing the existing `backend/` directory and a new `frontend/` directory is recommended.

### 4.2. Service Architecture

The architecture will be composed of three main parts:

1. The **Python Backend** for core logic and external API communication.
2. The **Supabase Database** as the central "source of truth" for system state.
3. **Database Triggers/Webhooks** as the automation and integration layer connecting the database to Azure DevOps.

### 4.3. Testing Requirements

Testing will be comprehensive, including unit tests for individual functions, integration tests for API connections, and end-to-end (e2e) tests for the complete workflow. Manual testing will be facilitated by convenience scripts.

### 4.4. Additional Technical Assumptions and Requests

- **Automation Layer:** Use **Supabase Database Webhooks or Postgres Functions** as the key automation component.

## 5. Epics

- **Epic 1: Foundational Setup & Core Data Pipeline:** Establish the project's core infrastructure, including the expanded database schema for lead and conversation management, and to ensure the SAM.gov data ingestion populates this new structure correctly.
- **Epic 2: Facebook Engagement & Conversational AI:** Develop the modules for searching Facebook, performing the initial engagement (like, comment, share), and handling the full conversational AI flow for direct messages.
- **Epic 3: Calendar Integration & Appointment Booking:** Build the integration with the Microsoft Outlook calendar for reading availability, writing tentative appointments, and managing the confirmation loop.
- **Epic 4: Azure DevOps Integration via Database Triggers:** Create the database functions and triggers to connect to Azure DevOps, ensuring the state from our database is perfectly mirrored on the board.
- **Epic 5: AI Self-Learning & Follow-up Automation:** Build the mechanism for the AI to learn from past conversations and implement the automated logic for handling no-shows and rescheduling requests.

## Epic 1: Foundational Setup & Core Data Pipeline

**Goal:** To establish the project's core infrastructure, including the expanded database schema for lead and conversation management, and to ensure the SAM.gov data ingestion populates this new structure correctly.

### Story 1.1: Extend Database Schema for Lead Management

**As a** system administrator,
**I want** to have a robust database schema in Supabase
**so that** I can track each prospective lead and their status throughout the entire engagement funnel.

#### Acceptance Criteria for Story 1.1

1. A new `leads` table must be created in the Supabase database.
2. The `leads` table must include columns for:
   - `id` (Primary Key)
   - `created_at`
   - `source_opportunity_id` (Foreign Key to the existing `opportunities` table)
   - `business_name` (text)
   - `facebook_page_url` (text)
   - `status` (text, e.g., 'Identified', 'Engaged', 'Messaged', 'Appointment Offered', 'Confirmed', 'Disqualified')
   - `last_updated_at` (timestamp)
3. A new `conversation_logs` table must be created.
4. The `conversation_logs` table must include columns for `id`, `lead_id` (Foreign Key to `leads`), `timestamp`, `sender` (e.g., 'AI', 'Business'), and `message` (text).

### Story 1.2: Update SAM.gov Script to Create Lead Records

**As a** system,
**I want** to automatically create new records in the `leads` table after finding relevant opportunities
**so that** potential partners are formally entered into the engagement funnel.

#### Acceptance Criteria for Story 1.2

1. After the existing `main.py` script successfully fetches and stores a new opportunity, it must be updated to perform a basic prospecting step (for the MVP, this can be a placeholder or a simple keyword match).
2. For each potential business partner identified, a new row must be created in the `leads` table.
3. The new lead record must have its `source_opportunity_id` correctly linked to the new opportunity and its initial `status` set to 'Identified'.
4. The script must handle errors gracefully and log any failures during the lead creation process.

## Epic 2: Facebook Engagement & Conversational AI

**Goal:** To develop the modules for searching Facebook, performing the initial engagement (like, comment, share), and handling the full conversational AI flow for direct messages.

### Story 2.1: Implement Facebook Business Page Search

**As a** system,
**I want** to search for relevant business pages on Facebook based on keywords from a contract opportunity
**so that** I can identify potential prime contractors to engage with.

#### Acceptance Criteria for Story 2.1

1. A new function in the `facebook_service` must accept keywords (e.g., "IT services," "construction") as input.
2. The function must use the Facebook Graph API to search for public business pages matching the keywords.
3. The search results must be filtered to only include businesses located in the United States.
4. The function must return a list of potential leads, including their page URL and business name.
5. The system must update the `leads` table in Supabase with the newly found `business_name` and `facebook_page_url`, and set their status to `'Prospected'`.

**Note:** The process of searching for a `facebook_page_url` is triggered after the system fetches new opportunities from SAM.gov. The keywords for the Facebook search are derived directly from the contract opportunity's details.

### Story 2.2: Perform Automated Engagement Sequence on a Target Page

**As a** system,
**I want** to automatically "warm up" a lead by liking, commenting on, and sharing their content
**so that** the initial outreach feels more organic and increases the chance of a response.

#### Acceptance Criteria for Story 2.2

1. The `facebook_service` must have a function that takes a target `facebook_page_url` as input.
2. The function must find a recent, relevant post on the target's page.
3. The system must programmatically perform the following actions using the Graph API:
   - **Like** the selected post.
   - **Share** the selected post to our own business page.
   - **Post a Comment** on the selected post. The comment content should be generated by the LLM to be positive and relevant.
4. After the sequence is complete, the `leads` table status for that lead must be updated to `'Engaged'`.
5. The system must handle cases where a page has no recent posts or where API permissions fail for any of the actions.

### Story 2.3: Initiate Direct Message Conversation

**As a** system,
**I want** to send a personalized initial direct message to a business that responds to my engagement
**so that** I can begin the process of educating them about the opportunity.

#### Acceptance Criteria for Story 2.3

1. The system must be able to detect a response from a target business. A response is defined as the target business **liking our comment**, **replying to our comment**, or **sending a direct message** to our page.
2. Upon detection, the `conversation_service` must be triggered for that lead.
3. The service must use the LLM to generate a personalized opening message that references the specific government contract.
4. The initial message must be sent as a direct message to the business's page via the `facebook_service`.
5. The sent message and the lead's response must be logged in the `conversation_logs` table in Supabase.
6. The lead's status must be updated to `'Messaged'`.

### Story 2.4: Manage Full Conversational Flow

**As a** system,
**I want** to manage a dynamic, multi-turn conversation with a business owner
**so that** I can answer their questions, provide information, and guide them toward scheduling a meeting.

#### Acceptance Criteria for Story 2.4

1. The `conversation_service` must be able to handle incoming direct messages from a business.
2. For each incoming message, the service must retrieve the conversation history from the `conversation_logs` table.
3. The full history must be sent to the LLM to generate a contextually-aware response.
4. The AI's response must be sent back to the user via the `facebook_service`.
5. Both the incoming message and the AI's response must be saved to the `conversation_logs` table.
6. The service must be able to detect when the conversation has reached the point where scheduling a meeting is the appropriate next step.

### Story 2.5: Ensure Funnel State is Reflected in Azure DevOps

**As a** system administrator,
**I want** every change in a lead's status to be reflected in our Azure DevOps board
**so that** I have a real-time view of the entire engagement funnel.

#### Acceptance Criteria for Story 2.5

1. The database triggers/webhooks must be configured to monitor the `status` column in the `leads` table.
2. When a lead's status changes to `'Prospected'`, `'Engaged'`, or `'Messaged'`, the corresponding trigger/webhook must trigger.
3. The trigger/webhook must successfully move the correct Work Item on the Azure DevOps Kanban board to the column that matches the new status.
4. A brief, automated comment (e.g., "Status updated to: Engaged") should be added to the Work Item's discussion history for traceability.

## Epic 3: Calendar Integration & Appointment Booking

**Goal:** To build the integration with the Microsoft Outlook calendar for reading availability, writing tentative appointments, and managing the confirmation loop.

### Story 3.1: Connect to Microsoft Outlook Calendar

**As a** system,
**I want** to connect to the Microsoft Outlook calendar to read availability and identify open appointment slots
**so that** I can manage the confirmation loop and schedule meetings.

#### Acceptance Criteria for Story 3.1

1. The system must be able to connect to the Microsoft Outlook calendar.
2. The system must be able to read availability and identify open appointment slots.
3. The system must be able to write new tentative appointments to the Microsoft Outlook calendar.
4. The system must manage a confirmation loop via direct message, ensuring the business owner explicitly confirms their attendance before finalizing the appointment.

### Story 3.2: Automated Rescheduling and Follow-ups

**As a** system,
**I want** to automatically handle no-shows and reschedule appointments
**so that** I can ensure timely meetings and maintain business relationships.

#### Acceptance Criteria for Story 3.2

1. The system must automatically send follow-up messages if a business owner is unresponsive or does not show up for a meeting.
2. The system must allow business owners to reschedule their appointment through the conversational AI.
3. The system must handle rescheduling requests and update the Microsoft Outlook calendar accordingly.

## Epic 4: Azure DevOps Integration via Database Triggers

**Goal:** To create the database functions and triggers to connect to Azure DevOps, ensuring the state from our database is perfectly mirrored on the board.

### Story 4.1: Create Database Functions and Triggers

**As a** system administrator,
**I want** to create database functions and triggers to connect Supabase to Azure DevOps
**so that** I can manage the state of the outreach funnel and track lead progression.

#### Acceptance Criteria for Story 4.1

1. The database functions and triggers must be configured to monitor the `status` column in the `leads` table.
2. When a lead's status changes to `'Prospected'`, `'Engaged'`, or `'Messaged'`, the corresponding trigger must trigger.
3. The trigger must successfully move the correct Work Item on the Azure DevOps Kanban board to the column that matches the new status.
4. A brief, automated comment (e.g., "Status updated to: Engaged") should be added to the Work Item's discussion history for traceability.

### Story 4.2: Configure Azure DevOps Board

**As a** system administrator,
**I want** to configure the Azure DevOps board to act as our management dashboard
**so that** I can have a real-time view of the entire engagement funnel.

#### Acceptance Criteria for Story 4.2

1. The Azure DevOps board must be configured to represent the lead stages (e.g., "Identified," "Engaged," "Messaged," "Appointment Set," "Confirmed").
2. The board must be configured to move Work Items across columns based on lead progression.
3. The board must be configured to display key information about each lead (e.g., business name, contact info, relevant contract).
4. The board must be configured to display conversation logs and other relevant data for each lead.

## Epic 5: AI Self-Learning & Follow-up Automation

**Goal:** To make the system smarter over time by creating a structured learning process and to robustly handle common scheduling issues like no-shows and rescheduling requests.

### Story 5.1: Analyze and Tag Conversation Outcomes

**As a** system administrator,
**I want** a background job that uses an LLM to analyze completed conversations and tag them with structured outcomes
**so that** we can create a dataset of which conversational strategies are effective and which are not.

#### Acceptance Criteria for Story 5.1

1. A new background job or service will be created that processes conversations marked as 'complete'.
2. The job will retrieve the full conversation history from the `conversation_logs` table.
3. It will send the transcript to an LLM with a prompt designed to classify the outcome.
4. The LLM will return a structured tag (e.g., `successful_booking`, `objection_cost`, `not_interested`, `ghosted`).
5. This outcome tag will be stored in a way that is associated with the lead and conversation.

### Story 5.2: Create a 'Learnings' Table to Store Insights

**As a** system analyst,
**I want** to store the tagged conversation outcomes in a dedicated `learnings` table
**so that** I can query and analyze our conversational performance over time.

#### Acceptance Criteria for Story 5.2

1. A new table named `learnings` will be created in the Supabase database.
2. The table must include columns for `id`, `conversation_id` (Foreign Key), `outcome_tag`, `summary` (text), and `created_at`.
3. The job from Story 5.1 must populate this table with the results of its analysis.
4. The `summary` field should contain a brief, AI-generated summary of the conversation for quick reference.

### Story 5.3: Implement Automated No-Show Detection and Follow-up

**As a** system,
**I want** to detect when a scheduled appointment has passed without the user attending
**so that** I can automatically trigger a follow-up message to re-engage the lead.

#### Acceptance Criteria for Story 5.3

1. A scheduled job must run periodically to check for appointments in the `appointments` table whose `end_time` is in the past.
2. The system must have a way to verify if the meeting actually occurred (for the MVP, we can assume if the status is still `tentative` or `confirmed` and not `completed`, it was a no-show).
3. If a no-show is detected, the `conversation_service` must be triggered.
4. The conversational AI will generate and send a specific, empathetic follow-up message to the lead via Facebook DM.
5. The lead's status in the `leads` table should be updated to something like `no_show_follow_up`.

### Story 5.4: Handle User-Initiated Rescheduling Requests

**As a** business owner,
**I want** to be able to tell the AI that I need to reschedule my appointment
**so that** I can easily find a new time that works for me without manual intervention.

#### Acceptance Criteria for Story 5.4

1. The `conversation_service` must be updated with a new intent detection for "reschedule".
2. When this intent is detected, the system should cancel the existing calendar event.
3. The system must re-initiate the same logic from Epic 3, using the `calendar_service` to find new available slots.
4. The AI will then present the new options to the user and manage the re-booking conversation flow.
5. The appointment record in the database must be updated with the new time upon confirmation.
