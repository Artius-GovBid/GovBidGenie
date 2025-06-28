DROP TRIGGER IF EXISTS on_lead_change ON public.leads CASCADE;
DROP TRIGGER IF EXISTS on_lead_update ON public.leads CASCADE;
DROP TRIGGER IF EXISTS on_lead_update_or_insert ON public.leads CASCADE;
DROP FUNCTION IF EXISTS handle_lead_update() CASCADE; 