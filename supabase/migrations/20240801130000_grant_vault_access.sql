-- Grant the postgres role access to the Supabase Vault
grant usage on schema vault to postgres;
grant select on all tables in schema vault to postgres; 