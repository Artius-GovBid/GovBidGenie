-- Function to handle lead updates and trigger Edge Function with logging
create or replace function handle_lead_update()
returns trigger as $$
declare
  v_project_url text;
  v_service_role_key text;
  v_url text;
  body jsonb;
begin
  -- Fetch secrets from Supabase Vault
  select decrypted_secret into v_project_url from vault.decrypted_secrets where name = 'SUPABASE_PROJECT_URL';
  select decrypted_secret into v_service_role_key from vault.decrypted_secrets where name = 'SUPABASE_SERVICE_ROLE_KEY';

  if v_project_url is null or v_service_role_key is null then
    return null;
  end if;

  v_url := v_project_url || '/functions/v1/devops-sync';

  -- Determine the body of the request based on the operation
  if TG_OP = 'INSERT' then
    body := jsonb_build_object('type', 'INSERT', 'record', row_to_json(NEW));
  elsif TG_OP = 'UPDATE' and NEW.status <> OLD.status then
    body := jsonb_build_object('type', 'UPDATE', 'record', row_to_json(NEW));
  else
    return null; -- Do nothing if the status hasn't changed
  end if;

  -- Call the Edge Function
  perform net.http_post(
    url:=v_url,
    headers:=jsonb_build_object(
      'Content-Type', 'application/json',
      'Authorization', 'Bearer ' || v_service_role_key
    ),
    body:=body
  );

  return NEW;
end;
$$ language plpgsql security definer; 