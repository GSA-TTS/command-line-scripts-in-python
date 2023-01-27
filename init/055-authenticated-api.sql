CREATE OR REPLACE FUNCTION api.insert_library(jsn JSON)
    RETURNS JSON
AS $$
BEGIN
    INSERT INTO data.libraries (fscs_id, name, address) VALUES (jsn->>'fscs_id', jsn->>'name', jsn->>'address');
    INSERT INTO auth.users (username, api_key, role) VALUES (jsn->>'fscs_id', jsn->>'api_key', 'library');
    RETURN '{"result":"OK"}'::json;
END;
$$ LANGUAGE 'plpgsql' SECURITY DEFINER;

CREATE OR REPLACE FUNCTION api.meaning(JSON)
    RETURNS INTEGER
AS $$
BEGIN
    RETURN 42;
END;
$$ LANGUAGE 'plpgsql';