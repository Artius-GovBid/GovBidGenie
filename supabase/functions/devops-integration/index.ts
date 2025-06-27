// Follow this setup guide to integrate the Deno language server with your editor:
// https://deno.land/manual/getting_started/setup_your_environment
// This enables autocomplete, go to definition, etc.

// Setup type definitions for built-in Supabase Runtime APIs
import "jsr:@supabase/functions-js/edge-runtime.d.ts"

import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

// Helper function to create a Supabase admin client
const createAdminClient = () => {
  return createClient(
    Deno.env.get("PROJECT_URL")!,
    Deno.env.get("SERVICE_ROLE_KEY")!
  );
}

// Azure DevOps API details
const DEVOPS_ORG_URL = "https://dev.azure.com/artiusit"; // <-- IMPORTANT: REPLACE THIS
const DEVOPS_PROJECT_NAME = "GovBidGenie"; // Or your project name
const DEVOPS_PAT = Deno.env.get("DEVOPS_PAT");

// Main function to handle incoming database webhooks
serve(async (req) => {
  const payload = await req.json();

  try {
    if (payload.type === "INSERT") {
      console.log(`Handling INSERT for: ${payload.record.id}`);
      await handleNewLead(payload.record);
    } else if (payload.type === "UPDATE") {
      console.log(`Handling UPDATE for: ${payload.record.id}`);
      // Only process the update if the status has actually changed
      if (payload.record.status !== payload.old_record.status) {
        console.log(`Status changed from ${payload.old_record.status} to ${payload.record.status}. Processing...`);
        await handleUpdatedLead(payload.record);
      } else {
        console.log("Status unchanged. Ignoring update.");
      }
    }

    return new Response("Webhook processed successfully", { status: 200 });
  } catch (error) {
    console.error("Error processing webhook:", error.message);
    return new Response(`Webhook Error: ${error.message}`, { status: 400 });
  }
})

// Function to handle creating a new work item in Azure DevOps
async function handleNewLead(lead: any) {
  const url = `${DEVOPS_ORG_URL}/${DEVOPS_PROJECT_NAME}/_apis/wit/workitems/$Issue?api-version=7.1-preview.3`;
  const body = [
    { "op": "add", "path": "/fields/System.Title", "value": lead.business_name },
    { "op": "add", "path": "/fields/System.Description", "value": `Initial lead created for opportunity ID: ${lead.opportunity_id}` },
    { "op": "add", "path": "/fields/System.State", "value": "Identified" }
  ];

  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json-patch+json',
      'Authorization': `Basic ${btoa(":" + DEVOPS_PAT)}`
    },
    body: JSON.stringify(body)
  });

  if (!response.ok) {
    throw new Error(`Azure DevOps API Error: ${await response.text()}`);
  }

  const workItem = await response.json();
  const workItemId = workItem.id;
  console.log(`Created work item ${workItemId} for lead ${lead.id}`);

  // Now, update the lead in Supabase with the new work item ID
  const supabase = createAdminClient();
  const { error } = await supabase
    .from('leads')
    .update({ azure_devops_work_item_id: workItemId })
    .eq('id', lead.id);

  if (error) {
    throw new Error(`Supabase update error: ${error.message}`);
  }
  console.log(`Updated lead ${lead.id} with work item ID ${workItemId}`);
}

// Function to handle updating an existing work item in Azure DevOps
async function handleUpdatedLead(lead: any) {
  if (!lead.azure_devops_work_item_id) {
    console.log(`Lead ${lead.id} has no work item ID, skipping update.`);
    return;
  }

  // Map Supabase status to Azure DevOps state
  const stateMap: { [key: string]: string } = {
    "IDENTIFIED": "Identified",
    "PROSPECTED": "Prospected",
    "ENGAGED": "Engaged",
    "MESSAGED": "Messaged",
    "APPOINTMENT_OFFERED": "Appointment Offered",
    "APPOINTMENT_SET": "Appointment Set",
    "CONFIRMED": "Confirmed"
    // The "Done" state exists in DevOps but is not mapped here
    // as there is no corresponding status in our system.
  };

  const devopsState = stateMap[lead.status];

  if (!devopsState) {
    console.warn(`No Azure DevOps state mapping found for status: ${lead.status}. Skipping update.`);
    return;
  }

  const url = `${DEVOPS_ORG_URL}/${DEVOPS_PROJECT_NAME}/_apis/wit/workitems/${lead.azure_devops_work_item_id}?api-version=7.1-preview.3`;
  const body = [
    { "op": "add", "path": "/fields/System.State", "value": devopsState }
  ];

  console.log(`Updating work item ${lead.azure_devops_work_item_id} with body:`, JSON.stringify(body, null, 2));

  const response = await fetch(url, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json-patch+json',
      'Authorization': `Basic ${btoa(":" + DEVOPS_PAT)}`
    },
    body: JSON.stringify(body)
  });

  if (!response.ok) {
    const errorText = await response.text();
    console.error(`Azure DevOps API Error (${response.status}): ${errorText}`);
    throw new Error(`Azure DevOps API Error: ${errorText}`);
  }

  console.log(`Updated work item ${lead.azure_devops_work_item_id} to state ${devopsState}`);
}

/* To invoke locally:

  1. Run `supabase start` (see: https://supabase.com/docs/reference/cli/supabase-start)
  2. Make an HTTP request:

  curl -i --location --request POST 'http://127.0.0.1:54321/functions/v1/devops-integration' \
    --header 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6ImFub24iLCJleHAiOjE5ODM4MTI5OTZ9.CRXP1A7WOeoJeXxjNni43kdQwgnWNReilDMblYTn_I0' \
    --header 'Content-Type: application/json' \
    --data '{"name":"Functions"}'

*/
