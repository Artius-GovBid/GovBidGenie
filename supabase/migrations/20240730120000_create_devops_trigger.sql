-- Create a function to invoke our Edge Function
create or replace function on_lead_change()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
  -- Make a request to our Edge Function
  perform
    net.http_post(
      url:='https://xiaxbkipvrgxubrcybna.functions.supabase.co/devops-integration',
      headers:='{"Content-Type": "application/json"}'::jsonb,
      body:=json_build_object('record', new, 'type', TG_OP)::jsonb
    );
  return new;
end;
$$;

-- Create a trigger that fires after every lead insert or update
create or replace trigger on_lead_change_trigger
after insert or update of status on leads
for each row
execute function on_lead_change(); 