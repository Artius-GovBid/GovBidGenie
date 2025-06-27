create or replace function handle_lead_update()
returns trigger as $$
declare
  body jsonb;
begin
  -- When a new lead is inserted
  if TG_OP = 'INSERT' then
    body := jsonb_build_object('type', 'INSERT', 'record', row_to_json(NEW));
  -- When a lead's status is updated
  elsif TG_OP = 'UPDATE' and NEW.status <> OLD.status then
    body := jsonb_build_object('type', 'UPDATE', 'record', row_to_json(NEW));
  else
    return null; -- Do nothing if the status hasn't changed
  end if;

  -- DEBUGGING: Log before the call
  insert into public.debug_log (message) values ('Attempting to call Edge Function...');

  -- Notify the edge function
  perform net.http_post(
    url:='https://qubdselkopzjnafxolsz.supabase.co/functions/v1/devops-integration',
    headers:='{"Content-Type": "application/json", "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InF1YmRzZWxrb3B6am5hZnhvbHN6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjI0NTk2ODUsImV4cCI6MTg4MDIzNTY4NX0.3gQ_1iY91yqLsoA1tTj5i9jHPNh8d1p9j8dY1jYyYyY"}'::jsonb,
    body:=body
  );

  -- DEBUGGING: Log after the call
  insert into public.debug_log (message) values ('Successfully called Edge Function.');

  return NEW;
end;
$$ language plpgsql; 