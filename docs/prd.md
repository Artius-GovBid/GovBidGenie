# Brownfield PRD: GovBidGenie Automation Enhancements

## 1. Introduction

This document outlines the requirements for enhancing the GovBidGenie application. The goal is to implement a fully automated, inbound lead generation and appointment-setting funnel. The system will leverage content engagement on Facebook to attract leads, use an AI-powered conversational agent to qualify them, and seamlessly book sales appointments, with all progress tracked on an Azure DevOps board.

---

## 2. Epics and User Stories

### Epic 1: Government Opportunity Ingestion

**Goal:** To build a robust system that automatically fetches, processes, and stores government contract opportunities from SAM.gov.

-   **User Story 1.1:** As the Genie, I need to fetch new contract opportunities from the SAM.gov API and store them in the `opportunities` table, ensuring that no duplicate opportunities are created.
-   **User Story 1.2:** As the Genie, I need to correctly map the required data fields from the SAM.gov API response (like `sam_gov_id`, `title`, `url`, `agency`, `posted_date`) to the corresponding columns in our database.
-   **User Story 1.3:** As the Genie, I need a scheduled, recurring job that automatically runs the fetching process on a regular basis (e.g., daily) to keep our opportunities up to date.

---

### Epic 2: Inbound Lead Generation via Content Engagement

**Goal:** To attract and capture leads by sharing relevant content from followed Facebook pages and engaging with users who comment.

-   **User Story 2.1:** As the Genie, I need to be able to follow a curated list of relevant business pages to build a source of shareable content.
-   **User Story 2.2:** As the Genie, I need to be able to share posts from the business pages I follow onto my own business's page.
-   **User Story 2.3:** As the Genie, I need to monitor my shared posts and detect when a new comment is made by a potential lead.
-   **User Story 2.4:** As the Genie, when a new comment is detected, I need to analyze the commenter's public profile to identify keywords about their business or profession.
-   **User Story 2.5:** As the Genie, I need to create a new entry in the `leads` table for the commenter and match them with the most relevant opportunity from the database using their profile keywords.
-   **User Story 2.6:** As the Genie, I need to send a personalized direct message to the commenter, referencing their comment and presenting the matched government contract opportunity.

---

### Epic 3: Conversational AI & Appointment Setting

**Goal:** To manage a context-aware conversation with a lead, determine their interest, and seamlessly schedule a sales appointment in an Outlook calendar.

-   **User Story 3.1:** As the Genie, I need to conduct a conversation that is context-aware, referencing the lead's business, the specific opportunity, and our previous interactions.
-   **User Story 3.2:** As the Genie, I need to be able to access a Microsoft Outlook calendar to read the sales team's availability in real-time.
-   **User Story 3.3:** As the Genie, when a lead expresses interest, I need to be able to propose available meeting times to them directly in the chat.
-   **User Story 3.4:** As the Genie, upon the lead's confirmation of a time, I need to automatically create a new appointment in the Outlook calendar with all the relevant details (lead name, opportunity, etc.).
-   **User Story 3.5:** As the Genie, I need to send a final confirmation message to the lead, including the date and time of the scheduled appointment.

---

### Epic 4: Azure DevOps Funnel Management

**Goal:** To automate the management of the sales funnel by representing leads as work items on an Azure DevOps board.

-   **User Story 4.1:** As the System, when a new lead is created in the database, I need to automatically create a corresponding "Work Item" on the Azure DevOps board, placing it in the initial "Identified" or "Engaged" column.
-   **User Story 4.2:** As the System, I need to automatically update the state of the Azure DevOps work item by moving it across the Kanban board columns (e.g., to "Appointment Set") whenever the lead's `status` field changes in our database.
-   **User Story 4.3:** As the System, I need to store the full conversation log and other key lead information within the Azure DevOps work item to provide a complete, centralized historical record for every interaction. 