SELECT
  c.relrowsecurity AS rls_enabled,
  c.relforcerowsecurity AS rls_forced,
  NOT has_table_privilege('anon', c.oid, 'SELECT') AS anonymous_read_blocked,
  NOT has_table_privilege('anon', c.oid, 'INSERT') AS anonymous_insert_blocked,
  NOT has_table_privilege('anon', c.oid, 'UPDATE') AS anonymous_update_blocked,
  NOT has_table_privilege('anon', c.oid, 'DELETE') AS anonymous_delete_blocked,
  (has_table_privilege('authenticated', c.oid, 'SELECT') AND has_table_privilege('authenticated', c.oid, 'INSERT') AND has_table_privilege('authenticated', c.oid, 'UPDATE')) AS user_table_access,
  EXISTS (SELECT 1 FROM pg_trigger t WHERE t.tgrelid = c.oid AND t.tgname = 'gradlife_workspace_version' AND t.tgenabled IN ('O','A') AND NOT t.tgisinternal) AS version_trigger_enabled,
  (SELECT jsonb_agg(jsonb_build_object('name', p.policyname, 'operation', p.cmd, 'roles', p.roles, 'using', p.qual, 'check', p.with_check)) FROM pg_policies p WHERE p.schemaname = 'public' AND p.tablename = 'gradlife_workspaces') AS policies
FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE n.nspname = 'public' AND c.relname = 'gradlife_workspaces';
