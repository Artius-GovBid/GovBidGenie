-- This table is being created to appease a "ghost" trigger
-- in the local Supabase environment that cannot be deleted.
-- It allows the application to run despite the faulty trigger.
CREATE TABLE IF NOT EXISTS public.debug_log (
    id SERIAL PRIMARY KEY,
    message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
); 