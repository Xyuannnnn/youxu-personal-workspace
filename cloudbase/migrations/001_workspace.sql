-- GradLife PostgreSQL bootstrap, not yet applied.
-- Execute only in the intended CloudBase PG environment after review.
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
-- Every UPDATE must submit old version + 1; the caller must also filter by
-- the previous version. Row locking makes stale writes fail atomically.
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
