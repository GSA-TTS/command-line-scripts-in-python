GRANT web_anon TO authenticator;
GRANT lib_admin TO authenticator;

GRANT SELECT, INSERT ON api.libraries TO lib_admin;
GRANT SELECT, INSERT ON data.libraries TO lib_admin;
GRANT SELECT, INSERT ON auth.users TO lib_admin;

GRANT USAGE ON SCHEMA api TO web_anon;
GRANT USAGE ON SCHEMA data TO web_anon;

GRANT EXECUTE ON FUNCTION api.login(text, text) to web_anon;

GRANT USAGE ON SCHEMA api TO lib_admin;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA api TO lib_admin;

