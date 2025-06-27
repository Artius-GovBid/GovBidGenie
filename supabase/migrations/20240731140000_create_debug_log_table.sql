create table if not exists public.debug_log (
  id serial primary key,
  message text,
  created_at timestamptz default now()
); 