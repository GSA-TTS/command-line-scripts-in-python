INSERT INTO auth.users (username, api_key, role) 
       VALUES ('admin', 'onetwothreeahahah', 'lib_admin');

-- These are for writing upload test scripts.
INSERT INTO data.libraries (fscs_id, name, address) 
       VALUES ('EN0001-001', 'ENDOR, PUBLIC LIBRARY OF', '1 Tree Drive, Endor, 10000');
INSERT INTO auth.users (username, api_key, role) 
       VALUES ('EN0001-001', 'for-testing-only', 'library');