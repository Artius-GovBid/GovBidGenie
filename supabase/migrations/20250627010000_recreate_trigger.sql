-- Attaches the trigger to the leads table.
-- This ensures that handle_lead_update() is called on every insert or update.
create trigger on_lead_update_or_insert
after insert or update on leads
for each row execute function handle_lead_update(); 