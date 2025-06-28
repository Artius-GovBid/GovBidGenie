-- Function to handle lead updates and trigger Edge Function with logging
create or replace function handle_lead_update()
returns trigger as $$
declare
  v_project_url text;
  v_service_role_key text;
  v_url text;
  body jsonb;
begin
  insert into public.debug_log (message) values ('Trigger started for OP: ' || TG_OP);

  -- Fetch secrets from Supabase Vault
  select decrypted_secret into v_project_url from vault.decrypted_secrets where name = 'SUPABASE_PROJECT_URL';
  if v_project_url is null then
    insert into public.debug_log (message) values ('Failed to get SUPABASE_PROJECT_URL from vault.');
  else
    insert into public.debug_log (message) values ('Successfully fetched SUPABASE_PROJECT_URL.');
  end if;

  select decrypted_secret into v_service_role_key from vault.decrypted_secrets where name = 'SUPABASE_SERVICE_ROLE_KEY';
  if v_service_role_key is null then
    insert into public.debug_log (message) values ('Failed to get SUPABASE_SERVICE_ROLE_KEY from vault.');
  else
    insert into public.debug_log (message) values ('Successfully fetched SUPABASE_SERVICE_ROLE_KEY.');
  end if;

  if v_project_url is null or v_service_role_key is null then
    insert into public.debug_log (message) values ('Exiting trigger due to missing secrets.');
    return null;
  end if;

  v_url := v_project_url || '/functions/v1/devops-integration';
  insert into public.debug_log (message) values ('Constructed URL: ' || v_url);

  -- Determine the body of the request based on the operation
  if TG_OP = 'INSERT' then
    body := jsonb_build_object('type', 'INSERT', 'record', row_to_json(NEW));
  elsif TG_OP = 'UPDATE' and NEW.status <> OLD.status then
    body := jsonb_build_object('type', 'UPDATE', 'record', row_to_json(NEW));
  else
    insert into public.debug_log (message) values ('No relevant change detected, exiting.');
    return null; -- Do nothing if the status hasn't changed
  end if;

  insert into public.debug_log (message) values ('Body constructed. Attempting http_post.');

  -- Call the Edge Function
  perform net.http_post(
    url:=v_url,
    headers:=jsonb_build_object(
      'Content-Type', 'application/json',
      'Authorization', 'Bearer ' || v_service_role_key
    ),
    body:=body
  );

  insert into public.debug_log (message) values ('http_post call performed. Trigger finished.');

  return NEW;
end;
$$ language plpgsql security definer; 