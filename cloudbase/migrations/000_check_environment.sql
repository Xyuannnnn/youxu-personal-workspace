SELECT
  EXISTS (SELECT 1 FROM pg_proc p JOIN pg_namespace n ON n.oid = p.pronamespace WHERE n.nspname = 'auth' AND p.proname = 'uid' AND p.pronargs = 0) AS has_uid_function,
  EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'anon') AS has_anon_role,
  EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'authenticated') AS has_authenticated_role,
  to_regclass('public.gradlife_workspaces') IS NOT NULL AS workspace_table_exists;
