-- Private shop schema. No tables or credentials are exposed through PostgREST.
create schema juicecraft;
create role juicecraft_app nologin;
grant usage on schema juicecraft to juicecraft_app;
revoke all on schema juicecraft from public, anon, authenticated;
create table juicecraft.admin (id integer primary key check(id=1),hash text not null,changed integer not null default 0);
create table juicecraft.attempts (key text primary key,count integer not null,until bigint not null);
create table juicecraft.sessions (token text primary key,expires bigint not null);
create index sessions_expiry on juicecraft.sessions(expires);
create table juicecraft.settings(id integer primary key check(id=1),name text not null,phone text not null,address text not null,footer text not null);
create table juicecraft.masters(id text primary key,kind text not null check(kind in ('brand','category','prepared')),name text not null,active integer not null default 1,unique(kind,name));
create table juicecraft.products(id text primary key,name text not null,kind text not null check(kind in ('packaged','prepared')),category text not null references juicecraft.masters(id),brand text references juicecraft.masters(id),variant text not null default '',price bigint not null check(price>=0),cost double precision not null default 0 check(cost>=0),qty integer not null default 0 constraint nonnegative_stock check(qty>=0),low integer not null default 5 check(low>=0),active integer not null default 1);
create table juicecraft.sales(id text primary key,number integer not null unique,date text not null,time text not null,payment text not null,total bigint not null,cost bigint not null,packaged bigint not null,prepared bigint not null,units integer not null,status text not null default 'completed',reason text,shop text not null);
create index sales_date on juicecraft.sales(date);
create table juicecraft.lines(id text primary key,sale text not null references juicecraft.sales(id),product text not null references juicecraft.products(id),name text not null,brand text,category text not null,kind text not null,price bigint not null,cost double precision not null,qty integer not null check(qty>0));
create index lines_sale on juicecraft.lines(sale);
create table juicecraft.movements(id text primary key,product text not null references juicecraft.products(id),date text not null,time text not null,type text not null,qty integer not null,cost double precision not null,note text not null,sale text references juicecraft.sales(id));
create index movements_date on juicecraft.movements(date);
create index movements_product on juicecraft.movements(product);
create table juicecraft.expenses(id text primary key,date text not null,category text not null,amount bigint not null check(amount>=0),note text not null);
create index expenses_date on juicecraft.expenses(date);
do $$ declare t text; begin
 foreach t in array array['admin','attempts','sessions','settings','masters','products','sales','lines','movements','expenses'] loop
  execute format('alter table juicecraft.%I enable row level security',t);
  execute format('revoke all on juicecraft.%I from public, anon, authenticated',t);
  execute format('grant select, insert, update, delete on juicecraft.%I to juicecraft_app',t);
  execute format('create policy edge_backend_only on juicecraft.%I to juicecraft_app using (true) with check (true)',t);
 end loop;
end $$;

GRANT juicecraft_app TO postgres WITH SET TRUE;
