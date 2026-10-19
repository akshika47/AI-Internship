-- WedVow starter schema for Supabase/PostgreSQL.
-- Review and test in a development project before production use.
--
-- V1 note: the live demo is a static birthday invite with localStorage RSVPs.
-- Next milestone: generalize `weddings` into `events` with
--   event_type text check (event_type in ('birthday','wedding'))
-- and flexible fields (or JSON) so birthdays and weddings share one table.

create extension if not exists pgcrypto;

create table public.weddings (
  id uuid primary key default gen_random_uuid(),
  owner_id uuid not null references auth.users(id) on delete cascade,
  slug text not null unique,
  partner_one text not null,
  partner_two text not null,
  wedding_date date,
  ceremony_time text,
  venue_name text,
  venue_address text,
  story text,
  theme_key text not null default 'editorial-ivory',
  hero_image_path text,
  is_published boolean not null default false,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint weddings_slug_format check (slug ~ '^[a-z0-9]+(-[a-z0-9]+)*$')
);

create table public.rsvps (
  id uuid primary key default gen_random_uuid(),
  wedding_id uuid not null references public.weddings(id) on delete cascade,
  guest_name text not null,
  attendance text not null check (attendance in ('yes','no')),
  guest_count integer not null default 1 check (guest_count between 0 and 20),
  dietary_notes text,
  created_at timestamptz not null default now()
);

create index rsvps_wedding_id_created_at_idx
  on public.rsvps (wedding_id, created_at desc);

alter table public.weddings enable row level security;
alter table public.rsvps enable row level security;

-- Couple can manage only their own wedding records.
create policy "Owners can read their weddings"
  on public.weddings for select
  to authenticated
  using (owner_id = auth.uid());

create policy "Owners can create their weddings"
  on public.weddings for insert
  to authenticated
  with check (owner_id = auth.uid());

create policy "Owners can update their weddings"
  on public.weddings for update
  to authenticated
  using (owner_id = auth.uid())
  with check (owner_id = auth.uid());

create policy "Owners can delete their weddings"
  on public.weddings for delete
  to authenticated
  using (owner_id = auth.uid());

-- Dashboard access: owners can view/manage RSVPs only for their wedding.
create policy "Owners can read RSVPs for their weddings"
  on public.rsvps for select
  to authenticated
  using (
    exists (
      select 1 from public.weddings w
      where w.id = rsvps.wedding_id and w.owner_id = auth.uid()
    )
  );

create policy "Owners can delete RSVPs for their weddings"
  on public.rsvps for delete
  to authenticated
  using (
    exists (
      select 1 from public.weddings w
      where w.id = rsvps.wedding_id and w.owner_id = auth.uid()
    )
  );

-- Public RSVP submissions require a carefully designed server-side endpoint.
-- Do NOT add a broad anonymous INSERT policy in production: it can invite spam
-- and may expose wedding IDs. Use a server route/Edge Function with validation,
-- rate limiting, spam protection, and published-wedding checks.
