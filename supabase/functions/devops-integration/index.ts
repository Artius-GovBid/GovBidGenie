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
  const record = payload.record;

  try {
    if (payload.type === "INSERT") {
      // Logic for new leads
      console.log(`New lead created: ${record.business_name} (ID: ${record.id})`);
      await handleNewLead(record);
    } else if (payload.type === "UPDATE") {
      // Logic for lead status updates
      console.log(`Lead updated: ${record.id}`);
      await handleUpdatedLead(record);
    }

    return new Response("Webhook processed successfully", { status: 200 });
  } catch (error) {
    console.error("Error processing webhook:", error.message);
    return new Response(`Webhook Error: ${error.message}`, { status: 400 });
  }
})

// Function to handle creating a new work item in Azure DevOps
async function handleNewLead(lead: any) {
  const url = `${DEVOPS_ORG_URL}/${DEVOPS_PROJECT_NAME}/_apis/wit/workitems/$User%20Story?api-version=7.1-preview.3`;
  const body = [
    { "op": "add", "path": "/fields/System.Title", "value": lead.business_name },
    { "op": "add", "path": "/fields/System.Description", "value": `Initial lead created for opportunity ID: ${lead.opportunity_id}` }
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

  const url = `${DEVOPS_ORG_URL}/_apis/wit/workitems/${lead.azure_devops_work_item_id}?api-version=7.1-preview.3`;
  const body = [
    { "op": "add", "path": "/fields/System.State", "value": lead.status }
  ];

  const response = await fetch(url, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json-patch+json',
      'Authorization': `Basic ${btoa(":" + DEVOPS_PAT)}`
    },
    body: JSON.stringify(body)
  });

  if (!response.ok) {
    throw new Error(`Azure DevOps API Error: ${await response.text()}`);
  }

  console.log(`Updated work item ${lead.azure_devops_work_item_id} to state ${lead.status}`);
}

/* To invoke locally:

  1. Run `supabase start` (see: https://supabase.com/docs/reference/cli/supabase-start)
  2. Make an HTTP request:

  curl -i --location --request POST 'http://127.0.0.1:54321/functions/v1/devops-integration' \
    --header 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6ImFub24iLCJleHAiOjE5ODM4MTI5OTZ9.CRXP1A7WOeoJeXxjNni43kdQwgnWNReilDMblYTn_I0' \
    --header 'Content-Type: application/json' \
    --data '{"name":"Functions"}'

*/
