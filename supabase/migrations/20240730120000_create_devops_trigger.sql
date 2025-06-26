-- Enable necessary extensions
create extension if not exists http with schema extensions;
create extension if not exists pg_tle with schema extensions;

-- Grant usage to the authenticated role
grant usage on schema extensions to authenticated;

-- Use TLE to install the secrets-manager extension
select pgtle.install_extension(
  'supabase-secrets-manager',
  '1.0.0',
  'SQL functions for managing secrets',
  'create extension if not exists "supabase-secrets-manager" with schema extensions'
);

-- Grant execute on the new function to the authenticated role
grant execute on function extensions."get_secret"(text) to authenticated;


-- Store the service role key securely in the Vault
-- NOTE: This key is only set once and will not be visible again.
-- The key is passed in during the migration and not stored in plaintext in the file.
select extensions.create_secret('service_role_key', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhpYXhia2lwdnJneHVicmN5Ym5hIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MDc0Nzg3NywiZXhwIjoyMDY2MzIzODc3fQ.2AayDil2pBWpvi5HUbipDRw4I5ZAgO0gV90N1PaU6D0');


-- Create the trigger function
create or replace function create_devops_work_item()
returns trigger
language plpgsql
security definer -- The function will run with the privileges of the user that created it
as $$
declare
  -- Safely retrieve the secret from the Vault
  service_key text := extensions.get_secret('service_role_key');
  project_url text := 'https://xiaxbkipvrgxubrcybna.supabase.co/functions/v1/devops-integration';
  response_id bigint;
begin
  -- Make a POST request to the Edge Function
  select
    id
  from
    http((
      'POST',
      project_url,
      array[http_header('Authorization', 'Bearer ' || service_key)],
      'application/json',
      json_build_object(
        'opportunity_title', new.opportunity_title,
        'agency_name', new.agency_name,
        'contact_email', new.contact_email
      )::text
    ))
  into
    response_id;

  return new;
end;
$$;


-- Create the trigger on the leads table
create trigger on_appointment_set
  after update on leads
  for each row
  when (new.status = 'APPOINTMENT_SET' and old.status <> 'APPOINTMENT_SET')
  execute function create_devops_work_item(); 