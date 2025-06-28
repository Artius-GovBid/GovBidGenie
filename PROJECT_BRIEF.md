# Project Brief: GovBidGenie

## 1. Background and Problem Statement

The U.S. federal government represents a massive, multi-billion dollar market. However, for the vast majority of small and medium-sized businesses, it is an invisible and inaccessible one. They are unaware that the government is a potential buyer for their services, and the process of finding and bidding on contracts is complex and labor-intensive. 

GovBidGenie was conceived to bridge this awareness and complexity gap by fully automating the process of converting raw government contract opportunities into confirmed sales appointments with qualified, previously unaware businesses.

## 2. Core Goals

- **Automate Lead Generation:** Eliminate the manual labor associated with lead generation, outreach, and scheduling in the government contracting space.
- **Unlock a New Market:** Provide a seamless, personalized, and valuable experience for target business owners, making them aware of a new and lucrative revenue stream.
- **Build a Scalable Engine:** Create a scalable, self-learning system that can manage the entire engagement funnel from end to end, from initial contact to a confirmed meeting.

## 3. High-Level Functional Requirements

The system is designed to perform the following core functions:

- **FR1:** Periodically fetch new contract opportunities from the SAM.gov API.
- **FR2:** Search Facebook to identify potential business partners based on keywords from the opportunities.
- **FR3 & FR4:** Engage with businesses on Facebook (likes, comments, shares) and initiate direct message conversations.
- **FR5:** Power conversations with a context-aware, non-generic conversational AI.
- **FR6 & FR7:** Integrate with a Microsoft Outlook calendar to read availability and book appointments.
- **FR12 & FR13:** Integrate with Azure DevOps to create and update work items, using an Azure Board as the primary management interface for the sales funnel.
- **FR16 & FR17:** Use Supabase database triggers and webhooks as the primary automation layer to connect the database state changes to actions in Azure DevOps.

## 4. Vision for Project Management & Operations

Instead of building a custom administrative dashboard, this project will use **Azure DevOps** as its primary management interface. 

- **The Funnel as a Kanban Board:** The lead generation funnel will be visually represented on an Azure DevOps Kanban board. Columns will map directly to lead stages (e.g., "Identified," "Engaged," "Appointment Set").
- **Leads as Work Items:** Each lead will be a "Work Item" (card) on the board. The system's backend will automatically move these cards across the columns as a lead progresses through the funnel.
- **Centralized Data:** Key lead information and full conversation logs will be stored within the Azure DevOps work item, providing a complete, centralized historical record for every interaction.

This approach leverages a robust, existing platform for all operational management, allowing development to focus on the core automation engine. 