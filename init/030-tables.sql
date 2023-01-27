SET default_tablespace = '';
SET default_table_access_method = heap;

CREATE TABLE IF NOT EXISTS
data.libraries (
    uniqueid SERIAL PRIMARY KEY,
    fscs_id character varying(16),
    name character varying,
    address character varying
);

CREATE TABLE IF NOT EXISTS
auth.users (
    username   text primary key check ( username ~* '^[a-zA-Z0-9\-]+$' ),
    api_key   text not null check (length(api_key) < 512),
    role      text not null check (length(role) < 512)
);