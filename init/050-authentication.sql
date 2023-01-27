-- We put things inside the auth schema to hide
-- them from public view. Certain public procs/views will
-- refer to helpers and tables inside.

create or replace function
auth.check_role_exists() returns trigger as $$
begin
  if not exists (select 1 from pg_roles as r where r.rolname = new.role) then
    raise foreign_key_violation using message =
      'unknown database role: ' || new.role;
    return null;
  end if;
  return new;
end
$$ language plpgsql;

drop trigger if exists ensure_user_role_exists on auth.users;
create constraint trigger ensure_user_role_exists
  after insert or update on auth.users
  for each row
  execute procedure auth.check_role_exists();

create extension if not exists pgcrypto;

create or replace function
auth.encrypt_pass() returns trigger as $$
begin
  if tg_op = 'INSERT' or new.api_key <> old.api_key then
    new.api_key = crypt(new.api_key, gen_salt('bf'));
  end if;
  return new;
end
$$ language plpgsql;

drop trigger if exists encrypt_pass on auth.users;
create trigger encrypt_pass
  before insert or update on auth.users
  for each row
  execute procedure auth.encrypt_pass();

CREATE OR REPLACE FUNCTION auth.user_role(username text, api_key text)
 RETURNS name
 LANGUAGE plpgsql
AS $function$
begin
  	return (
  		select role from auth.users
   			where users.username = user_role.username
     			and users.api_key = crypt(user_role.api_key, users.api_key)
			);
end;
$function$
;

-- add type
CREATE TYPE auth.jwt_token AS (
  token text
);

-- login should be on your exposed schema
create or replace function
api.login(username text, api_key text) returns auth.jwt_token as $$
declare
  _role name;
  result auth.jwt_token;
begin
  -- check email and password
  select auth.user_role(login.username, login.api_key) into _role;
  if _role is null then
    raise invalid_password using message = 'invalid user or password';
  end if;

  select sign(
      row_to_json(r), current_setting('app.jwt_secret')
    ) as token
    from (
      select _role as role, login.username as username,
         extract(epoch from now())::integer + 60*60 as exp
    ) r
    into result;
  return result;
end;
$$ language plpgsql security definer;

-- the names "anon" and "authenticator" are configurable and not
-- sacred, we simply choose them for clarity
