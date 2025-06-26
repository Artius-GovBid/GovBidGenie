# Project Brief: Government Lead Genie

## Executive Summary

This project, Government Lead Genie, is a fully automated lead generation, outreach, and appointment booking platform designed to secure prime contractors for federal projects. The system begins by identifying relevant contract opportunities on SAM.gov. It then uses a designated Facebook business page to engage with potential prime contractors by liking, commenting on, and sharing their business content.

Upon engagement from a business, the tool initiates a personalized direct message conversation about a specific, relevant contract. The system's intelligence guides the conversation to a point of interest, then integrates with a Microsoft Outlook calendar to find and offer available 15-minute appointment slots. The core workflow concludes successfully only when the business owner has confirmed their attendance for the scheduled meeting.

The primary problem it solves is the complete, time-consuming, and manual process of identifying, engaging, and scheduling meetings with potential prime contractors. The target market is businesses on Facebook with the capabilities to act as prime contractors for U.S. federal government opportunities. The key value proposition is the end-to-end automation of the business development pipeline, seamlessly converting a raw government contract listing into a confirmed sales appointment in the calendar.

## Problem Statement

For the vast majority of businesses, the world of U.S. federal government contracting represents a massive, untapped revenue stream they are completely unaware of. They are experts in providing their products and services, but have no insight into the fact that the government is one of the largest potential buyers for what they offer. The primary problem is a **barrier of awareness and complexity**.

Even if a business were to become aware, the process to enter this market is fragmented, labor-intensive, and inefficient. The current state for a newcomer involves several disconnected, manual processes:

1.  **Invisible Opportunities:** Businesses are not actively looking for federal contracts because they don't know the opportunities exist or assume they are not qualified. SAM.gov is not a part of their world.
2.  **Lack of Connection:** There is no bridge connecting their existing commercial services to specific, lucrative government contracts they could fulfill as a prime contractor.
3.  **Inefficient Outreach (from the perspective of a partnership builder):** Manually identifying and educating potential prime contractors on platforms like Facebook is a monumental effort. It requires speculative, one-on-one outreach to explain the opportunity, a process that is unscalable and has a low probability of success.
4.  **Scheduling Friction:** Even if interest is piqued, the final step of booking a meeting is often a tedious back-and-forth of emails and messages, creating a high risk of the potential partner losing interest.

Existing solutions are non-existent for this target market. They are not using government portals. CRMs are irrelevant. This lack of an automated, educational, and engagement-driven platform means countless capable businesses are locked out of the federal marketplace, and potential partnerships that could fulfill government needs are never formed.

## Proposed Solution

We will build an automated platform, Government Lead Genie, that acts as a bridge between the lucrative federal contracting market and the millions of businesses currently unaware of it. The platform will manage the entire engagement funnel, from identifying an opportunity to booking a confirmed meeting, requiring zero manual intervention.

The core concept is a three-part automated system:

1.  **Opportunity & Prospecting Engine:** The system will continuously scan SAM.gov for new contract opportunities. For each opportunity, it will then identify and target suitable businesses on Facebook that have the capabilities to fulfill the contract, even if they have never engaged with the government sector before.
2.  **Automated Engagement & Education Funnel:** Using a dedicated Facebook Business Page, the platform will initiate contact by intelligently engaging with a target business's content (liking, sharing, commenting). Once the business responds, a personalized and automated direct message sequence will begin. This conversation will educate the business owner about the specific, relevant government contract, framing it as a direct extension of the services they already provide.
3.  **Intelligent Scheduling Assistant:** As the conversation progresses and the business owner shows interest, the system will seamlessly transition to a scheduling assistant. It will access an integrated Microsoft Outlook calendar to find and propose available 15-minute meeting slots. The workflow is designed to drive towards a single goal: securing a confirmed "yes" from the business owner for the appointment.

This solution will succeed because it is proactive, personalized, and removes all friction. It doesn't wait for businesses to come looking; it brings the opportunity directly to them in a context they already understand (their business services). By fully automating the most time-consuming aspects of business development, it creates a scalable and efficient new channel for growth.

## Target Users

### Primary User Segment: The Unaware, Capable Business Owner

*   **Profile:** These are small to medium-sized business owners in the United States, typically active on Facebook for promoting their services. They are experts in their domain (e.g., IT services, construction, marketing, office supplies) but have little to no knowledge of the federal contracting marketplace. Their business is their primary focus, and they are likely not seeking out new, complex revenue channels.
*   **Current Behaviors:** They use their Facebook Business Page as a primary tool for marketing and customer engagement. They post updates about their services, share successes, and interact with their existing community. Their daily workflow is focused on running their business, not on navigating government bureaucracy.
*   **Specific Needs and Pain Points:**
    *   They need new revenue streams but may not know where to look.
    *   They are likely intimidated by the perceived complexity and red tape of government work.
    *   They lack the time and resources for speculative business development efforts.
    *   They respond to clear, direct opportunities that align with what they already do.
*   **Goals:** Their primary goals are to grow their business, increase revenue, and find new customers for the services they already offer. They are motivated by concrete opportunities, not abstract possibilities.

## Goals & Success Metrics

### Business Objectives
*   **Primary Objective:** To automate the generation of qualified sales appointments, measured by the number of confirmed meetings scheduled per week/month.
*   **Secondary Objective:** To create a new, scalable channel for business development that does not require proportional increases in manual effort.
*   **Tertiary Objective:** To validate the effectiveness of the automated outreach funnel, measured by the conversion rate from initial contact to confirmed meeting.

### User Success Metrics
*   **Perceived Value:** The target business owner feels they have been presented with a genuine, valuable, and relevant opportunity they would not have found otherwise.
*   **Ease of Use:** The process of learning about the opportunity and booking a meeting is seamless and requires minimal effort on their part.
*   **Positive Engagement:** The interaction with the automated system feels personal and professional, not like a generic chatbot.

### Key Performance Indicators (KPIs)
*   **KPI 1: Confirmed Appointments:** The number of meetings successfully scheduled and confirmed per week. **Target: 5 confirmed appointments per week for the MVP.**
*   **KPI 2: Funnel Conversion Rate:** The percentage of businesses that move from initial engagement (e.g., replying to a comment) to a confirmed appointment. **Target: 2% conversion rate for the MVP.**
*   **KPI 3: Engagement Rate:** The percentage of initial outreach actions (comments, likes, shares) that result in a response from the target business. **Target: 10% engagement rate for the MVP.**

## MVP Scope

### Core Features (Must-Haves)

*   **1. SAM.gov Data Ingestion:** The backend script will fetch contract opportunities and store them in the Supabase database.
*   **2. Facebook Business Search & Comprehensive Engagement:** The system must be able to perform a search on Facebook for businesses that match the contract opportunity. It will then execute a sequence of automated engagement actions: **liking, commenting on, and sharing** a relevant post from the target business's page onto your own business page.
*   **3. Advanced Conversational AI for DMs:** The system will initiate a DM conversation using a sophisticated, context-aware **conversational AI**. It will generate dynamic, non-generic responses in real-time to maintain a personalized and authentic tone.
*   **4. Outlook Calendar Read/Write Integration & Confirmation Loop:** The system must connect to a specified Microsoft Outlook calendar to both read availability and **create new tentative appointments**. It will manage a confirmation loop, waiting for an explicit confirmation from the business owner.
*   **5. User-Facing Admin Dashboard:** A web-based user interface will be developed. This dashboard will allow you to manage the system, monitor the status of all outreach efforts, view conversation logs, and see key performance indicators.
*   **6. Funnel State Tracking:** The Supabase database will be extended to track the detailed state of each engagement, visible through the admin dashboard.
*   **7. Automated Rescheduling and Follow-ups:** The system will automatically handle no-shows by sending follow-up messages and will allow business owners to reschedule their appointments through the conversational AI.
*   **8. Self-Learning AI Model:** The conversational AI will incorporate a self-learning mechanism, allowing it to adapt and improve its outreach and conversation strategies over time based on the outcomes of past interactions.

### Out of Scope for MVP

*   **Multi-Platform Outreach:** The MVP will focus exclusively on Facebook.

### MVP Success Criteria

The MVP will be considered a success when the integrated system (backend, self-learning conversational AI, and admin dashboard) can, without manual intervention, successfully manage the full engagement lifecycle: from fetching an opportunity, securing a confirmed meeting, and handling potential follow-ups or rescheduling, with the entire process being observable and manageable through the admin UI.

## Post-MVP Vision

### Phase 2 Features

*   **Multi-Platform Expansion:** Integrate the outreach and engagement engine with other professional platforms, starting with LinkedIn, and potentially extending to email outreach.
*   **Advanced Analytics Dashboard:** Enhance the admin dashboard with detailed analytics on funnel performance, conversation outcomes, and the effectiveness of the AI's strategies.
*   **CRM Integration:** Add the ability to push confirmed appointments and contact details to popular CRMs like HubSpot or Salesforce.

### Long-term Vision

*   In 1-2 years, Government Lead Genie aims to be the industry-leading platform for automated business-to-government (B2G) partnership development. It will be an indispensable tool for any business looking to enter or expand its footprint in the federal contracting space. The platform could evolve into a full-fledged marketplace, connecting prime contractors and subcontractors.

### Expansion Opportunities

*   **Subcontractor Marketplace:** Create a feature where prime contractors can post opportunities, and the system finds suitable subcontractors, automating another layer of the supply chain.
*   **State and Local Government Contracts:** Expand the data ingestion engine to include contract opportunities from state and local government portals, not just the federal SAM.gov.
*   **Enterprise Tier:** Offer a premium version for larger organizations with features like team management, advanced security, and dedicated support.

## Technical Considerations

### Established & Preferred Technologies

*   **Backend:** **Python**, using the existing libraries: `supabase-py` for database interaction, `requests` for API calls, and `schedule` for task scheduling.
*   **Database:** **Supabase (Postgres)**, as currently implemented.
*   **Frontend:** A modern JavaScript framework like **React, Vue, or Svelte** is recommended to build the interactive admin dashboard that will communicate with the Python backend.
*   **Hosting/Infrastructure:** A platform like **Heroku or AWS** for the Python backend, and **Vercel or Netlify** for the frontend dashboard.
*   **Conversational AI:** An API-driven Large Language Model like **OpenAI's GPT-4**.
*   **Self-Learning Mechanism:** This will be a new Python module that analyzes conversation data stored in Supabase to refine AI strategies.

### Architecture Considerations

*   **Repository Structure:** A **monorepo** containing the existing `backend/` directory and a new `frontend/` directory is recommended.
*   **Service Architecture:** The existing **monolithic Python backend** will be expanded to include new modules for the conversational AI, Facebook integration, and Outlook integration. It will also expose a REST API to communicate with the frontend admin dashboard.
*   **Integration Requirements:**
    *   **SAM.gov API** (existing)
    *   **Facebook Graph API** (new)
    *   **Microsoft Graph API** (new)
*   **Security/Compliance:** All API keys and credentials will be managed securely using `python-dotenv` in development and environment variables in production.

## Constraints & Assumptions

### Constraints

*   **Platform:** The initial outreach channel is exclusively Facebook. The solution's success is tied to the capabilities and limitations of the Facebook Graph API.
*   **Timeline:** To be determined. This is a complex MVP, and the timeline will depend on development resources.
*   **Budget:** To be determined. Costs will include cloud hosting and API usage for the LLM.

### Key Assumptions

*   **API Access:** We assume we can get approved and maintain sufficient access to both the Facebook Graph API and Microsoft Graph API for the required functionalities.
*   **Target Audience:** We assume that a significant number of businesses that are viable prime contractors are active on Facebook and responsive to this form of engagement.
*   **AI Viability:** We assume that a conversational AI can be engineered to be personal and effective enough to achieve the desired conversion rates without feeling generic or alienating users.

## Risks & Open Questions

### Key Risks

*   **Risk 1: API Restrictions or Rejection (High Impact):** Our application could be denied API access, or our access could be rate-limited or revoked by Facebook or Microsoft, which would be a critical failure point.
*   **Risk 2: Low Engagement/Conversion (High Impact):** The core business model may be unviable if target businesses do not respond to the automated outreach or if the AI cannot successfully convert interest into appointments.
*   **Risk 3: Technical Complexity (Medium Impact):** Integrating multiple complex systems (LLM, Facebook API, Outlook API, a self-learning loop) and building a reliable admin dashboard is a significant technical challenge for an MVP.

### Open Questions

*   What are the specific terms of service for the Facebook and Microsoft APIs regarding automated engagement and messaging, and how can we ensure full compliance?
*   What is the most effective "personality" and conversational strategy for the AI to maximize genuine engagement?
*   What is the most robust and cost-effective way to architect the self-learning feedback loop for the AI?
 

# Government Lead Genie Product Requirements Document (PRD)

## Goals and Background Context

### Goals

*   To create a fully automated platform that converts raw government contract opportunities into confirmed sales appointments with qualified, previously unaware businesses.
*   To eliminate the manual labor associated with lead generation, outreach, and scheduling in the government contracting space.
*   To provide a seamless, personalized, and valuable experience for the target business owners, making them aware of a new and lucrative revenue stream.
*   To build a scalable system, including a self-learning AI and an admin dashboard, that can manage the entire engagement funnel from end to end.

### Background Context

The U.S. federal government represents a massive, multi-billion dollar market. However, for the vast majority of small and medium-sized businesses, it is an invisible and inaccessible one. They are unaware that the government is a potential buyer for their services. This project, Government Lead Genie, was conceived to bridge this awareness and complexity gap.

The platform will proactively find contract opportunities, identify suitable businesses on Facebook, and use a sophisticated conversational AI to engage them. By automating the entire process�from initial contact to a confirmed meeting in an Outlook calendar�it aims to unlock a significant new market for these businesses while creating a highly efficient, automated business development engine.

### Change Log

| Date       | Version | Description              | Author |
| :--------- | :------ | :----------------------- | :----- |
| 2024-07-26 | 1.0     | Initial draft of the PRD | PM Bot |

## Requirements

### Functional

*   **FR1:** The system must periodically fetch new contract opportunities from the SAM.gov API.
*   **FR2:** The system must perform searches on Facebook to identify potential business partners based on keywords from the contract opportunities.
*   **FR3:** The system must, via a connected Facebook Business Page, be able to like, comment on, and share posts made by a target business.
*   **FR4:** The system must initiate and manage a direct message conversation with a business that responds to the initial engagement.
*   **FR5:** The conversation must be powered by a conversational AI capable of generating dynamic, context-aware, and non-generic responses.
*   **FR6:** The system must connect to a Microsoft Outlook calendar to read availability and identify open appointment slots.
*   **FR7:** The system must be able to write new tentative appointments to the Microsoft Outlook calendar.
*   **FR8:** The system must manage a confirmation loop via direct message, ensuring the business owner explicitly confirms their attendance before finalizing the appointment.
*   **FR9:** The system must automatically send follow-up messages if a business owner is unresponsive or does not show up for a meeting.
*   **FR10:** The system must provide a mechanism for business owners to reschedule their appointment through the conversational AI.
*   **FR11:** The conversational AI must have a self-learning mechanism to analyze past conversation outcomes and refine its strategies over time.
*   **FR12 (Revised):** The system must integrate with the Azure DevOps REST API to programmatically create and update work items.
*   **FR13 (Revised):** The state of the outreach funnel must be represented by work items on a specific Azure Board, with lead progression shown by moving work items across columns.
*   **FR14 (Revised):** The system must append conversation logs as comments to the appropriate work item in Azure DevOps.
*   **FR15 (New):** The system will require credentials (like a Personal Access Token) with sufficient permissions to interact with the target Azure DevOps project.
*   **FR16 (New):** The system will be architected so that changes in the Supabase database (e.g., a new lead, a status change) trigger **Microsoft Power Automate flows**.
*   **FR17 (New):** Power Automate flows will be responsible for creating, updating, and moving work items on the Azure DevOps board.
*   **FR18 (New):** Power Automate flows will be responsible for posting conversation logs and other relevant data as comments to the appropriate work item in Azure DevOps.

### Non Functional

*   **NFR1:** The conversational AI's persona must be consistently authentic, personal, and professional, avoiding any language that feels robotic or generic.
*   **NFR2:** The system must securely store and manage all API keys, access tokens, and other credentials.
*   **NFR3:** The admin dashboard must be responsive and have a page load time of under 3 seconds for all primary views.
*   **NFR4:** The system's architecture must be scalable to handle an increasing volume of concurrent conversations and API calls.
*   **NFR5:** The system must operate within the terms of service and rate limits of the Facebook Graph API and Microsoft Graph API.
*   **NFR6:** All user data and conversation logs must be handled with strict privacy controls.
*   **NFR7:** The backend services must be reliable and include error handling and logging to ensure fault tolerance.

## Management Interface: Azure DevOps Integration

*   **Overall Vision:** Instead of a custom-built dashboard, the system will use **Azure DevOps** as its primary management interface. The Python backend will be responsible for creating and updating work items in an Azure DevOps project, effectively turning Azure Boards into the "mission control" for the lead generation funnel.
*   **Kanban Funnel Implementation:** The outreach funnel will be represented by a **Kanban board within Azure Boards**.
    *   **Columns:** The board's columns will map directly to the lead stages (e.g., "Identified," "Engaged," "Messaged," "Appointment Set," "Confirmed").
    *   **Lead Cards:** Each lead will be represented as a **Work Item** (e.g., a "User Story" or a custom "Lead" type). The backend will automatically move these cards across the board as the lead progresses through the funnel.
*   **Data Representation:**
    *   **Lead Details:** Key information about the lead (business name, contact info, relevant contract) will be stored in the fields of the Azure DevOps Work Item.
    *   **Conversation Logs:** The full transcript of the conversation with a lead will be added to the **"Discussion" or "Comments" section** of the corresponding Work Item, providing a complete historical record.

## Technical Assumptions

### Repository Structure: { Monorepo, Polyrepo, etc...}

### Service Architecture

The architecture will be composed of three main parts:
1.  The **Python Backend** for core logic and external API communication.
2.  The **Supabase Database** as the central "source of truth" for system state.
3.  **Microsoft Power Automate** as the automation and integration layer connecting the database to Azure DevOps.

### Testing requirements

[[LLM: CRITICAL DECISION - Document the testing requirements, unit only, integration, e2e, manual, need for manual testing convenience methods).]]

### Additional Technical Assumptions and Requests

*   **Automation Layer:** Add **Microsoft Power Automate** as a key component of the technology stack.

## Epics

*   **Epic 1: Foundational Setup & Core Data Pipeline:** Establish the project's core infrastructure, including the expanded database schema for lead and conversation management, and to ensure the SAM.gov data ingestion populates this new structure correctly.
*   **Epic 2: Facebook Engagement & Conversational AI:** Develop the modules for searching Facebook, performing the initial engagement (like, comment, share), and handling the full conversational AI flow for direct messages.
*   **Epic 3: Calendar Integration & Appointment Booking:** Build the integration with the Microsoft Outlook calendar for reading availability, writing tentative appointments, and managing the confirmation loop.
*   **Epic 4: Azure DevOps & Power Automate Integration:** Create the Power Automate flows and configure the Azure DevOps board to act as our management dashboard, ensuring the state from our database is perfectly mirrored.
*   **Epic 5: AI Self-Learning & Follow-up Automation:** Build the mechanism for the AI to learn from past conversations and implement the automated logic for handling no-shows and rescheduling requests.

## Epic 1: Foundational Setup & Core Data Pipeline

**Goal:** To establish the project's core infrastructure, including the expanded database schema for lead and conversation management, and to ensure the SAM.gov data ingestion populates this new structure correctly.

### Story 1.1: Extend Database Schema for Lead Management

**As a** system administrator,
**I want** to have a robust database schema in Supabase
**so that** I can track each prospective lead and their status throughout the entire engagement funnel.

#### Acceptance Criteria

1.  A new `leads` table must be created in the Supabase database.
2.  The `leads` table must include columns for:
    *   `id` (Primary Key)
    *   `created_at`
    *   `source_opportunity_id` (Foreign Key to the existing `opportunities` table)
    *   `business_name` (text)
    *   `facebook_page_url` (text)
    *   `status` (text, e.g., 'Identified', 'Engaged', 'Messaged', 'Appointment Offered', 'Confirmed', 'Disqualified')
    *   `last_updated_at` (timestamp)
3.  A new `conversation_logs` table must be created.
4.  The `conversation_logs` table must include columns for `id`, `lead_id` (Foreign Key to `leads`), `timestamp`, `sender` (e.g., 'AI', 'Business'), and `message` (text).

### Story 1.2: Update SAM.gov Script to Create Lead Records

**As a** system,
**I want** to automatically create new records in the `leads` table after finding relevant opportunities
**so that** potential partners are formally entered into the engagement funnel.

#### Acceptance Criteria

1.  After the existing `main.py` script successfully fetches and stores a new opportunity, it must be updated to perform a basic prospecting step (for the MVP, this can be a placeholder or a simple keyword match).
2.  For each potential business partner identified, a new row must be created in the `leads` table.
3.  The new lead record must have its `source_opportunity_id` correctly linked to the new opportunity and its initial `status` set to 'Identified'.
4.  The script must handle errors gracefully and log any failures during the lead creation process. 
