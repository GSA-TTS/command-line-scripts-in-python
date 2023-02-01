DROP TABLE IF EXISTS env;
DROP TABLE IF EXISTS env_tmp;
CREATE TEMP TABLE env_tmp(e text);
CREATE TEMP TABLE env(k text, v text);
COPY env_tmp ( e ) FROM PROGRAM 'env';
INSERT INTO env
SELECT (regexp_split_to_array(e,'={1,1}'))[1],
  (regexp_match(e, '={1,1}(.*)'))[1]
FROM env_tmp;

SELECT * FROM env;

-- This lets us pass this in as a secret from the environment.
-- The values can either be sourced in (locally) or with GH Actions secrets.
-- The latter means that when we run remotely, these can be set up securely.
-- (And, it gets the code more ready for production use.)
INSERT INTO auth.users (username, api_key, role) 
       VALUES ( (SELECT v FROM env WHERE k = 'ADMIN_USERNAME'),  (SELECT v FROM env WHERE k = 'ADMIN_PASSWORD'), 'lib_admin');

-- These are for writing upload test scripts.
INSERT INTO data.libraries (fscs_id, name, address) 
       VALUES ('EN0001-001', 'ENDOR, PUBLIC LIBRARY OF', '1 Tree Drive, Endor, 10000');
INSERT INTO auth.users (username, api_key, role) 
       VALUES ('EN0001-001', 'for-testing-only', 'library');