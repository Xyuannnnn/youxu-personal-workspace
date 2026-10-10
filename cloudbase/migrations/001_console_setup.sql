BEGIN;
CREATE TABLE public.gradlife_workspaces (
  owner_id text PRIMARY KEY DEFAULT auth.uid(),
  payload jsonb NOT NULL DEFAULT '{}'::jsonb CHECK (jsonb_typeof(payload) = 'object'),
  version bigint NOT NULL DEFAULT 1 CHECK (version > 0),
  updated_at timestamptz NOT NULL DEFAULT now()
);
ALTER TABLE public.gradlife_workspaces ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.gradlife_workspaces FORCE ROW LEVEL SECURITY;
REVOKE ALL ON public.gradlife_workspaces FROM PUBLIC, anon;
GRANT SELECT, INSERT, UPDATE ON public.gradlife_workspaces TO authenticated;
CREATE POLICY gradlife_owner_select ON public.gradlife_workspaces
  FOR SELECT TO authenticated USING (owner_id = auth.uid());
CREATE POLICY gradlife_owner_insert ON public.gradlife_workspaces
  FOR INSERT TO authenticated WITH CHECK (owner_id = auth.uid());
CREATE POLICY gradlife_owner_update ON public.gradlife_workspaces
  FOR UPDATE TO authenticated USING (owner_id = auth.uid()) WITH CHECK (owner_id = auth.uid());
CREATE FUNCTION public.gradlife_guard_workspace_version() RETURNS trigger
LANGUAGE plpgsql SECURITY INVOKER SET search_path = pg_catalog AS $$
BEGIN
  IF NEW.owner_id IS DISTINCT FROM OLD.owner_id THEN
    RAISE EXCEPTION 'workspace owner cannot change' USING ERRCODE = '42501';
  END IF;
  IF NEW.version <> OLD.version + 1 THEN
    RAISE EXCEPTION 'workspace version conflict' USING ERRCODE = '40001';
  END IF;
  NEW.updated_at := now();
  RETURN NEW;
END;
$$;
CREATE TRIGGER gradlife_workspace_version
BEFORE UPDATE ON public.gradlife_workspaces
FOR EACH ROW EXECUTE FUNCTION public.gradlife_guard_workspace_version();
COMMIT;

SELECT c.relname AS table_name, c.relrowsecurity AS rls_enabled, c.relforcerowsecurity AS rls_forced, (SELECT count(*) FROM pg_policies p WHERE p.schemaname = 'public' AND p.tablename = 'gradlife_workspaces') AS policy_count FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace WHERE n.nspname = 'public' AND c.relname = 'gradlife_workspaces';
