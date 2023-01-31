CREATE OR REPLACE FUNCTION api.insert_library(jsn JSON)
    RETURNS JSON
AS $$
BEGIN
    INSERT INTO data.libraries (fscs_id, name, address) VALUES (jsn->>'fscs_id', jsn->>'name', jsn->>'address')
    ON CONFLICT DO NOTHING;
    INSERT INTO auth.users (username, api_key, role) VALUES (jsn->>'fscs_id', jsn->>'api_key', 'library')
    ON CONFLICT DO NOTHING;
    RETURN '{"result":"OK"}'::json;
END;
$$ LANGUAGE 'plpgsql' SECURITY DEFINER;

-- For testing the authenticated API.
CREATE OR REPLACE FUNCTION api.meaning()
    RETURNS JSON
AS $$
BEGIN
    RETURN json_build_object('meaning_of_life', 42);
END;
$$ LANGUAGE 'plpgsql';

DROP FUNCTION IF EXISTS api.delete_library;
CREATE OR REPLACE FUNCTION api.delete_library(jsn JSON)
	RETURNS JSON
	LANGUAGE plpgsql
AS $$
DECLARE 
	libraries_deleted INTEGER;
    users_deleted INTEGER;
	BEGIN
		DELETE FROM data.libraries WHERE data.libraries.fscs_id = jsn->>'fscs_id';
		GET DIAGNOSTICS libraries_deleted = ROW_COUNT;  
        DELETE FROM auth.users WHERE auth.users.username = jsn->>'fscs_id';
		GET DIAGNOSTICS users_deleted = ROW_COUNT;  
		RETURN json_build_object(
            'libraries_deleted', libraries_deleted, 
            'users_deleted', users_deleted
            );
	END;
$$
SECURITY DEFINER
;
  
-- https://stackoverflow.com/questions/28921355/how-do-i-check-if-a-json-key-exists-in-postgres
CREATE FUNCTION key_exists(some_json JSON, outer_key TEXT)
RETURNS boolean AS $$
BEGIN
    RETURN (some_json->outer_key) IS NOT NULL;
END;
$$ LANGUAGE plpgsql;

DROP FUNCTION IF EXISTS do_update;
CREATE OR REPLACE FUNCTION do_update(jsn JSON, key TEXT)
	RETURNS JSON
	LANGUAGE plpgsql
AS $$
DECLARE
    rows_updated INTEGER;
BEGIN
        UPDATE data.libraries SET address = jsn->>'address'
            WHERE fscs_id = jsn->>'fscs_id';
        GET DIAGNOSTICS rows_updated = ROW_COUNT;  
        RETURN json_build_object('updated', 'address', 'rows_updated', rows_updated);
END;
$$ 
SECURITY DEFINER;

DROP FUNCTION IF EXISTS api.update_library;
CREATE OR REPLACE FUNCTION api.update_library(jsn JSON)
	RETURNS JSON
	LANGUAGE plpgsql
AS $$
DECLARE
    rows_updated INTEGER;
BEGIN
    IF key_exists(jsn, 'address') = TRUE
    THEN
        RETURN do_update(jsn, 'address');
    ELSIF key_exists(jsn, 'name') = TRUE
    THEN
        RETURN do_update(jsn, 'name');
    ELSIF key_exists(jsn, 'tag') = TRUE
    THEN
        RETURN do_update(jsn, 'tag');
    ELSIF key_exists(jsn, 'api-key') = TRUE
    THEN
        UPDATE auth.users SET api_key = jsn->>'api-key'
            WHERE username = jsn->>'fscs_id';
        GET DIAGNOSTICS rows_updated = ROW_COUNT;  
        RETURN json_build_object('updated', 'api_key', 'rows_updated', rows_updated);
    END IF;
    RETURN json_build_object('updated', '');
END;
$$
SECURITY DEFINER;