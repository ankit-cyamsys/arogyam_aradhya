--
-- PostgreSQL database dump
--

\restrict UNB5rVaeIw5XBd9hgoUeIdpO4PYjXPmkUyZFgp5En4hvRs2VFp88o9AQkgBKEVz

-- Dumped from database version 18.6 (Debian 18.6-1.pgdg12+2)
-- Dumped by pg_dump version 18.1

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: public; Type: SCHEMA; Schema: -; Owner: -
--

-- *not* creating schema, since initdb creates it


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: admin_users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.admin_users (
    id integer NOT NULL,
    username character varying(60) NOT NULL,
    password_hash character varying(255) NOT NULL,
    name character varying(120),
    is_super boolean NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: admin_users_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.admin_users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: admin_users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.admin_users_id_seq OWNED BY public.admin_users.id;


--
-- Name: categories; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.categories (
    id integer NOT NULL,
    name character varying(120) NOT NULL,
    slug character varying(140) NOT NULL,
    description text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: categories_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.categories_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: categories_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.categories_id_seq OWNED BY public.categories.id;


--
-- Name: commission_ledger; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.commission_ledger (
    id integer NOT NULL,
    member_id integer NOT NULL,
    kind character varying(30) NOT NULL,
    amount numeric(12,2) NOT NULL,
    sp_matched numeric(12,2) NOT NULL,
    period character varying(20),
    note character varying(200),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: commission_ledger_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.commission_ledger_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: commission_ledger_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.commission_ledger_id_seq OWNED BY public.commission_ledger.id;


--
-- Name: kyc_documents; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.kyc_documents (
    id integer NOT NULL,
    member_id integer NOT NULL,
    doc_type character varying(30) NOT NULL,
    filename character varying(255) NOT NULL,
    content_type character varying(100) NOT NULL,
    data bytea NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: kyc_documents_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.kyc_documents_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: kyc_documents_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.kyc_documents_id_seq OWNED BY public.kyc_documents.id;


--
-- Name: members; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.members (
    id integer NOT NULL,
    member_id character varying(20) NOT NULL,
    segment character varying(10) NOT NULL,
    name character varying(120) NOT NULL,
    email character varying(120),
    phone character varying(20),
    password_hash character varying(255) NOT NULL,
    sponsor_id integer,
    parent_id integer,
    "position" character varying(1),
    is_active boolean NOT NULL,
    is_blocked boolean NOT NULL,
    activated_at timestamp with time zone,
    rank_level integer DEFAULT 0 NOT NULL,
    rank_bonus_paid_level integer DEFAULT 0 NOT NULL,
    week_left_sp numeric(14,2) DEFAULT '0'::numeric NOT NULL,
    week_right_sp numeric(14,2) DEFAULT '0'::numeric NOT NULL,
    left_carry numeric(14,2) NOT NULL,
    right_carry numeric(14,2) NOT NULL,
    total_left_sp numeric(14,2) NOT NULL,
    total_right_sp numeric(14,2) NOT NULL,
    total_matched_sp numeric(14,2) DEFAULT '0'::numeric NOT NULL,
    self_purchase_sp numeric(14,2) NOT NULL,
    capping_limit numeric(14,2) DEFAULT '0'::numeric NOT NULL,
    wallet_balance numeric(14,2) NOT NULL,
    total_earned numeric(14,2) NOT NULL,
    total_paid numeric(14,2) NOT NULL,
    address character varying(255),
    city character varying(80),
    state character varying(80),
    pincode character varying(10),
    pan character varying(20),
    aadhaar character varying(20),
    bank_name character varying(120),
    bank_account character varying(30),
    bank_ifsc character varying(20),
    nominee character varying(120),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: members_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.members_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: members_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.members_id_seq OWNED BY public.members.id;


--
-- Name: order_items; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.order_items (
    id integer NOT NULL,
    order_id integer NOT NULL,
    product_id integer NOT NULL,
    name character varying(200) NOT NULL,
    price numeric(12,2) NOT NULL,
    sp numeric(10,2) NOT NULL,
    quantity integer NOT NULL
);


--
-- Name: order_items_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.order_items_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: order_items_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.order_items_id_seq OWNED BY public.order_items.id;


--
-- Name: orders; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.orders (
    id integer NOT NULL,
    order_no character varying(30) NOT NULL,
    member_id integer NOT NULL,
    subtotal numeric(12,2) NOT NULL,
    total numeric(12,2) NOT NULL,
    total_sp numeric(10,2) NOT NULL,
    status character varying(20) NOT NULL,
    payment_status character varying(20) NOT NULL,
    address character varying(400),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: orders_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.orders_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: orders_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.orders_id_seq OWNED BY public.orders.id;


--
-- Name: payout_requests; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.payout_requests (
    id integer NOT NULL,
    member_id integer NOT NULL,
    amount numeric(12,2) NOT NULL,
    tds numeric(12,2) DEFAULT '0'::numeric NOT NULL,
    net numeric(12,2) DEFAULT '0'::numeric NOT NULL,
    status character varying(20) NOT NULL,
    method character varying(30),
    reference character varying(80),
    note character varying(200),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: payout_requests_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.payout_requests_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: payout_requests_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.payout_requests_id_seq OWNED BY public.payout_requests.id;


--
-- Name: products; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.products (
    id integer NOT NULL,
    name character varying(200) NOT NULL,
    slug character varying(220) NOT NULL,
    description text,
    category_id integer,
    mrp numeric(12,2) NOT NULL,
    price numeric(12,2) NOT NULL,
    cost_price numeric(12,2) NOT NULL,
    sp numeric(10,2) NOT NULL,
    stock integer NOT NULL,
    image character varying(255),
    is_active boolean NOT NULL,
    is_offer boolean NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: products_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.products_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: products_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.products_id_seq OWNED BY public.products.id;


--
-- Name: settings; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.settings (
    key character varying(60) NOT NULL,
    value text NOT NULL,
    label character varying(160),
    "group" character varying(40),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: sp_ledger; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.sp_ledger (
    id integer NOT NULL,
    member_id integer NOT NULL,
    source_member_id integer,
    order_id integer,
    leg character varying(1) NOT NULL,
    sp numeric(12,2) NOT NULL,
    note character varying(200),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: sp_ledger_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.sp_ledger_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: sp_ledger_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.sp_ledger_id_seq OWNED BY public.sp_ledger.id;


--
-- Name: weekly_payouts; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.weekly_payouts (
    id integer NOT NULL,
    member_id integer NOT NULL,
    period character varying(20) NOT NULL,
    week_label character varying(40),
    left_sp numeric(14,2) NOT NULL,
    right_sp numeric(14,2) NOT NULL,
    matching_sp numeric(14,2) NOT NULL,
    closing_sp numeric(14,2) NOT NULL,
    payout numeric(14,2) NOT NULL,
    cf_left numeric(14,2) NOT NULL,
    cf_right numeric(14,2) NOT NULL,
    status character varying(20) NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: weekly_payouts_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.weekly_payouts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: weekly_payouts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.weekly_payouts_id_seq OWNED BY public.weekly_payouts.id;


--
-- Name: admin_users id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.admin_users ALTER COLUMN id SET DEFAULT nextval('public.admin_users_id_seq'::regclass);


--
-- Name: categories id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.categories ALTER COLUMN id SET DEFAULT nextval('public.categories_id_seq'::regclass);


--
-- Name: commission_ledger id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.commission_ledger ALTER COLUMN id SET DEFAULT nextval('public.commission_ledger_id_seq'::regclass);


--
-- Name: kyc_documents id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.kyc_documents ALTER COLUMN id SET DEFAULT nextval('public.kyc_documents_id_seq'::regclass);


--
-- Name: members id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.members ALTER COLUMN id SET DEFAULT nextval('public.members_id_seq'::regclass);


--
-- Name: order_items id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.order_items ALTER COLUMN id SET DEFAULT nextval('public.order_items_id_seq'::regclass);


--
-- Name: orders id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.orders ALTER COLUMN id SET DEFAULT nextval('public.orders_id_seq'::regclass);


--
-- Name: payout_requests id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payout_requests ALTER COLUMN id SET DEFAULT nextval('public.payout_requests_id_seq'::regclass);


--
-- Name: products id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.products ALTER COLUMN id SET DEFAULT nextval('public.products_id_seq'::regclass);


--
-- Name: sp_ledger id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sp_ledger ALTER COLUMN id SET DEFAULT nextval('public.sp_ledger_id_seq'::regclass);


--
-- Name: weekly_payouts id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.weekly_payouts ALTER COLUMN id SET DEFAULT nextval('public.weekly_payouts_id_seq'::regclass);


--
-- Data for Name: admin_users; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.admin_users VALUES (1, 'admin', '$2b$12$i1DsxgSYu1Uxfg1ttvhtg.2jS/7hrKaTC/RP.LufM2gXJ7fnlF.4e', 'Administrator', true, '2026-09-24 18:08:27.920247+00', '2026-09-24 18:08:27.920247+00');


--
-- Data for Name: categories; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.categories VALUES (1, 'Immunity Boosters', 'immunity', NULL, '2026-09-24 18:08:28.690314+00', '2026-09-24 18:08:28.690314+00');
INSERT INTO public.categories VALUES (2, 'Digestive Health', 'digestive', NULL, '2026-09-24 18:08:28.690314+00', '2026-09-24 18:08:28.690314+00');
INSERT INTO public.categories VALUES (3, 'Skin Care', 'skin-care', NULL, '2026-09-24 18:08:28.690314+00', '2026-09-24 18:08:28.690314+00');
INSERT INTO public.categories VALUES (4, 'General Wellness', 'wellness', NULL, '2026-09-24 18:08:28.690314+00', '2026-09-24 18:08:28.690314+00');
INSERT INTO public.categories VALUES (5, 'Personal Care', 'personal-care', NULL, '2026-09-24 18:08:28.690314+00', '2026-09-24 18:08:28.690314+00');
INSERT INTO public.categories VALUES (6, 'Home Care', 'home-care', NULL, '2026-09-24 18:08:28.690314+00', '2026-09-24 18:08:28.690314+00');
INSERT INTO public.categories VALUES (7, 'Offer Packages', 'offers', NULL, '2026-09-24 18:08:28.690314+00', '2026-09-24 18:08:28.690314+00');


--
-- Data for Name: commission_ledger; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- Data for Name: kyc_documents; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- Data for Name: members; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.members VALUES (1, 'AA10000001', 'mlm', 'Arogyam Aradhya', NULL, '9000000001', '$2b$12$btOS8oc8N0azZSTIqG03h.P78m.h2zfL17qu8dRX3ovy.FJIAmpzG', NULL, NULL, NULL, true, false, NULL, 0, 0, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2026-09-24 18:08:31.550824+00', '2026-09-24 18:08:31.550824+00');


--
-- Data for Name: order_items; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- Data for Name: orders; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- Data for Name: payout_requests; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- Data for Name: products; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.products VALUES (1, 'Anti Addiction Drop 30ml', 'anti-addiction-drop-30ml', 'Authentic Ayurvedic formulation made with natural herbs. 100% natural & safe, no side effects, made with trusted quality ingredients.', 4, 499.00, 370.00, 0.00, 2.00, 100, '/static/products/logo.jpeg', true, false, '2026-09-24 18:08:29.930226+00', '2026-09-24 18:08:29.930226+00');
INSERT INTO public.products VALUES (2, 'Tulsi Drop 30ml', 'tulsi-drop-30ml', 'Authentic Ayurvedic formulation made with natural herbs. 100% natural & safe, no side effects, made with trusted quality ingredients.', 1, 249.00, 149.00, 0.00, 0.75, 100, '/static/products/logo.jpeg', true, false, '2026-09-24 18:08:29.930226+00', '2026-09-24 18:08:29.930226+00');
INSERT INTO public.products VALUES (3, 'Cough Syrup 200ml', 'cough-syrup-200ml', 'Authentic Ayurvedic formulation made with natural herbs. 100% natural & safe, no side effects, made with trusted quality ingredients.', 4, 249.00, 149.00, 0.00, 1.00, 100, '/static/products/cough-syrup.jpg', true, false, '2026-09-24 18:08:29.930226+00', '2026-09-24 18:08:29.930226+00');
INSERT INTO public.products VALUES (4, 'Weight Loss Syrup 500ml', 'weight-loss-syrup-500ml', 'Authentic Ayurvedic formulation made with natural herbs. 100% natural & safe, no side effects, made with trusted quality ingredients.', 4, 999.00, 700.00, 0.00, 5.00, 100, '/static/products/weightloss-syrup.jpg', true, false, '2026-09-24 18:08:29.930226+00', '2026-09-24 18:08:29.930226+00');
INSERT INTO public.products VALUES (5, 'Weight Loss Capsule 30', 'weight-loss-capsule-30', 'Authentic Ayurvedic formulation made with natural herbs. 100% natural & safe, no side effects, made with trusted quality ingredients.', 4, 999.00, 649.00, 0.00, 5.00, 100, '/static/products/weightloss-cap.jpg', true, false, '2026-09-24 18:08:29.930226+00', '2026-09-24 18:08:29.930226+00');
INSERT INTO public.products VALUES (6, 'Ortho Syrup 200ml', 'ortho-syrup-200ml', 'Authentic Ayurvedic formulation made with natural herbs. 100% natural & safe, no side effects, made with trusted quality ingredients.', 4, 299.00, 199.00, 0.00, 1.50, 100, '/static/products/ortho-syrup.jpg', true, false, '2026-09-24 18:08:29.930226+00', '2026-09-24 18:08:29.930226+00');
INSERT INTO public.products VALUES (7, 'Ortho Capsule 30', 'ortho-capsule-30', 'Authentic Ayurvedic formulation made with natural herbs. 100% natural & safe, no side effects, made with trusted quality ingredients.', 4, 299.00, 199.00, 0.00, 1.50, 100, '/static/products/ortho-cap.jpg', true, false, '2026-09-24 18:08:29.930226+00', '2026-09-24 18:08:29.930226+00');
INSERT INTO public.products VALUES (8, 'Mixberry Juice 500ml', 'mixberry-juice-500ml', 'Authentic Ayurvedic formulation made with natural herbs. 100% natural & safe, no side effects, made with trusted quality ingredients.', 4, 1699.00, 1299.00, 0.00, 10.00, 100, '/static/products/energy-stamina.jpg', true, true, '2026-09-24 18:08:29.930226+00', '2026-09-24 18:08:29.930226+00');
INSERT INTO public.products VALUES (9, 'Amla Tulsi Ginger Curcumin 800ml', 'amla-tulsi-ginger-curcumin-800ml', 'Authentic Ayurvedic formulation made with natural herbs. 100% natural & safe, no side effects, made with trusted quality ingredients.', 1, 499.00, 280.00, 0.00, 2.00, 100, '/static/products/logo.jpeg', true, false, '2026-09-24 18:08:29.930226+00', '2026-09-24 18:08:29.930226+00');
INSERT INTO public.products VALUES (10, 'Aloevera with Fiber 800ml', 'aloevera-with-fiber-800ml', 'Authentic Ayurvedic formulation made with natural herbs. 100% natural & safe, no side effects, made with trusted quality ingredients.', 2, 899.00, 425.00, 0.00, 2.50, 100, '/static/products/neem-aloevera.jpg', true, false, '2026-09-24 18:08:29.930226+00', '2026-09-24 18:08:29.930226+00');
INSERT INTO public.products VALUES (11, 'Energy & Stamina 3X Power Wellness Kit', 'energy-stamina-3x-power-wellness-kit', 'Authentic Ayurvedic formulation made with natural herbs. 100% natural & safe, no side effects, made with trusted quality ingredients.', 4, 1499.00, 1499.00, 0.00, 6.00, 100, '/static/products/energy-stamina.jpg', true, true, '2026-09-24 18:08:29.930226+00', '2026-09-24 18:08:29.930226+00');
INSERT INTO public.products VALUES (12, 'Neem Aloevera Face Wash', 'neem-aloevera-face-wash', 'Authentic Ayurvedic formulation made with natural herbs. 100% natural & safe, no side effects, made with trusted quality ingredients.', 3, 299.00, 175.00, 0.00, 0.75, 100, '/static/products/neem-facewash.jpg', true, false, '2026-09-24 18:08:29.930226+00', '2026-09-24 18:08:29.930226+00');
INSERT INTO public.products VALUES (13, 'Coffee Face Wash', 'coffee-face-wash', 'Authentic Ayurvedic formulation made with natural herbs. 100% natural & safe, no side effects, made with trusted quality ingredients.', 3, 299.00, 175.00, 0.00, 0.75, 100, '/static/products/coffee-facewash.jpg', true, false, '2026-09-24 18:08:29.930226+00', '2026-09-24 18:08:29.930226+00');
INSERT INTO public.products VALUES (14, 'Charcoal Face Wash 200ml', 'charcoal-face-wash-200ml', 'Authentic Ayurvedic formulation made with natural herbs. 100% natural & safe, no side effects, made with trusted quality ingredients.', 3, 299.00, 175.00, 0.00, 0.75, 100, '/static/products/coffee-facewash.jpg', true, false, '2026-09-24 18:08:29.930226+00', '2026-09-24 18:08:29.930226+00');
INSERT INTO public.products VALUES (15, 'Amla Shikakai Shampoo 200ml', 'amla-shikakai-shampoo-200ml', 'Authentic Ayurvedic formulation made with natural herbs. 100% natural & safe, no side effects, made with trusted quality ingredients.', 5, 299.00, 175.00, 0.00, 0.75, 100, '/static/products/aloevera-shampoo.jpg', true, false, '2026-09-24 18:08:29.930226+00', '2026-09-24 18:08:29.930226+00');
INSERT INTO public.products VALUES (16, 'Hinggoli', 'hinggoli', 'Authentic Ayurvedic formulation made with natural herbs. 100% natural & safe, no side effects, made with trusted quality ingredients.', 2, 99.00, 65.00, 0.00, 0.10, 100, '/static/products/hing-goli.jpg', true, false, '2026-09-24 18:08:29.930226+00', '2026-09-24 18:08:29.930226+00');
INSERT INTO public.products VALUES (17, 'Hing Goli Dana', 'hing-goli-dana', 'Authentic Ayurvedic formulation made with natural herbs. 100% natural & safe, no side effects, made with trusted quality ingredients.', 2, 119.00, 85.00, 0.00, 0.20, 100, '/static/products/hingoli.jpg', true, false, '2026-09-24 18:08:29.930226+00', '2026-09-24 18:08:29.930226+00');
INSERT INTO public.products VALUES (18, 'Pain Guard Roll-On', 'pain-guard-roll-on', 'Authentic Ayurvedic formulation made with natural herbs. 100% natural & safe, no side effects, made with trusted quality ingredients.', 4, 299.00, 199.00, 0.00, 1.00, 100, '/static/products/pain-rolon.jpg', true, false, '2026-09-24 18:08:29.930226+00', '2026-09-24 18:08:29.930226+00');
INSERT INTO public.products VALUES (19, 'Cough Syrup 100ml', 'cough-syrup-100ml', 'Authentic Ayurvedic formulation made with natural herbs. 100% natural & safe, no side effects, made with trusted quality ingredients.', 4, 149.00, 149.00, 0.00, 0.25, 100, '/static/products/cough-syrup-100.jpg', true, false, '2026-09-24 18:08:29.930226+00', '2026-09-24 18:08:29.930226+00');
INSERT INTO public.products VALUES (20, 'Giloy Papaya Wheatgrass', 'giloy-papaya-wheatgrass', 'Authentic Ayurvedic formulation made with natural herbs. 100% natural & safe, no side effects, made with trusted quality ingredients.', 1, 525.00, 299.00, 0.00, 2.00, 100, '/static/products/giloy-papaya.jpg', true, false, '2026-09-24 18:08:29.930226+00', '2026-09-24 18:08:29.930226+00');
INSERT INTO public.products VALUES (21, 'Livzyme', 'livzyme', 'Authentic Ayurvedic formulation made with natural herbs. 100% natural & safe, no side effects, made with trusted quality ingredients.', 2, 249.00, 149.00, 0.00, 1.00, 100, '/static/products/livzyme.jpg', true, false, '2026-09-24 18:08:29.930226+00', '2026-09-24 18:08:29.930226+00');
INSERT INTO public.products VALUES (22, 'Seetone', 'seetone', 'Authentic Ayurvedic formulation made with natural herbs. 100% natural & safe, no side effects, made with trusted quality ingredients.', 4, 249.00, 149.00, 0.00, 1.00, 100, '/static/products/seetone.jpg', true, false, '2026-09-24 18:08:29.930226+00', '2026-09-24 18:08:29.930226+00');
INSERT INTO public.products VALUES (23, 'Neem Soap', 'neem-soap', 'Authentic Ayurvedic formulation made with natural herbs. 100% natural & safe, no side effects, made with trusted quality ingredients.', 5, 90.00, 45.00, 0.00, 0.10, 100, '/static/products/neem-soap.jpg', true, false, '2026-09-24 18:08:29.930226+00', '2026-09-24 18:08:29.930226+00');
INSERT INTO public.products VALUES (24, 'Herbal Shampoo', 'herbal-shampoo', 'Authentic Ayurvedic formulation made with natural herbs. 100% natural & safe, no side effects, made with trusted quality ingredients.', 5, 349.00, 249.00, 0.00, 1.00, 100, '/static/products/aloevera-shampoo.jpg', true, false, '2026-09-24 18:08:29.930226+00', '2026-09-24 18:08:29.930226+00');
INSERT INTO public.products VALUES (25, 'Gas Go', 'gas-go', 'Authentic Ayurvedic formulation made with natural herbs. 100% natural & safe, no side effects, made with trusted quality ingredients.', 2, 249.00, 149.00, 0.00, 1.00, 100, '/static/products/gas-go.jpg', true, false, '2026-09-24 18:08:29.930226+00', '2026-09-24 18:08:29.930226+00');
INSERT INTO public.products VALUES (26, 'Eye Drop', 'eye-drop', 'Authentic Ayurvedic formulation made with natural herbs. 100% natural & safe, no side effects, made with trusted quality ingredients.', 4, 125.00, 75.00, 0.00, 0.25, 100, '/static/products/logo.jpeg', true, false, '2026-09-24 18:08:29.930226+00', '2026-09-24 18:08:29.930226+00');
INSERT INTO public.products VALUES (27, 'Sanitary Pads', 'sanitary-pads', 'Authentic Ayurvedic formulation made with natural herbs. 100% natural & safe, no side effects, made with trusted quality ingredients.', 5, 249.00, 149.00, 0.00, 0.50, 100, '/static/products/sanitary-pad.jpg', true, false, '2026-09-24 18:08:29.930226+00', '2026-09-24 18:08:29.930226+00');
INSERT INTO public.products VALUES (28, 'Smart Bag', 'smart-bag', 'Authentic Ayurvedic formulation made with natural herbs. 100% natural & safe, no side effects, made with trusted quality ingredients.', 6, 999.00, 700.00, 0.00, 2.50, 100, '/static/products/logo.jpeg', true, false, '2026-09-24 18:08:29.930226+00', '2026-09-24 18:08:29.930226+00');
INSERT INTO public.products VALUES (29, 'Starter Offer Pack', 'starter-offer-pack', 'Business offer package — includes products worth the pack value.', 7, 5000.00, 5000.00, 0.00, 40.00, 1000, '/static/products/offer-5000.jpg', true, true, '2026-09-24 18:08:29.930226+00', '2026-09-24 18:08:29.930226+00');
INSERT INTO public.products VALUES (30, 'Silver Offer Pack', 'silver-offer-pack', 'Business offer package — includes products worth the pack value.', 7, 12500.00, 12500.00, 0.00, 100.00, 1000, '/static/products/offer-12500.jpg', true, true, '2026-09-24 18:08:29.930226+00', '2026-09-24 18:08:29.930226+00');
INSERT INTO public.products VALUES (31, 'Gold Offer Pack', 'gold-offer-pack', 'Business offer package — includes products worth the pack value.', 7, 25000.00, 25000.00, 0.00, 200.00, 1000, '/static/products/offer-25000.jpg', true, true, '2026-09-24 18:08:29.930226+00', '2026-09-24 18:08:29.930226+00');
INSERT INTO public.products VALUES (32, 'Platinum Offer Pack', 'platinum-offer-pack', 'Business offer package — includes products worth the pack value.', 7, 50000.00, 50000.00, 0.00, 400.00, 1000, '/static/products/offer-50000.jpg', true, true, '2026-09-24 18:08:29.930226+00', '2026-09-24 18:08:29.930226+00');


--
-- Data for Name: settings; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.settings VALUES ('matching_per_sp', '10.0', '₹ per matched SP (1:1 — 25:25 = ₹250, 50:50 = ₹500)', 'matching', '2026-09-24 18:08:26.905342+00', '2026-09-24 18:08:26.905342+00');
INSERT INTO public.settings VALUES ('matching_ratio', '1:1', 'Left:Right matching ratio', 'matching', '2026-09-24 18:08:26.905342+00', '2026-09-24 18:08:26.905342+00');
INSERT INTO public.settings VALUES ('capping_25sp', '50000.0', 'Weekly matching cap (₹) if first purchase ≥25 SP', 'matching', '2026-09-24 18:08:26.905342+00', '2026-09-24 18:08:26.905342+00');
INSERT INTO public.settings VALUES ('capping_50sp', '100000.0', 'Weekly matching cap (₹) if first purchase ≥50 SP', 'matching', '2026-09-24 18:08:26.905342+00', '2026-09-24 18:08:26.905342+00');
INSERT INTO public.settings VALUES ('capping_100sp', '200000.0', 'Weekly matching cap (₹) if first purchase ≥100 SP', 'matching', '2026-09-24 18:08:26.905342+00', '2026-09-24 18:08:26.905342+00');
INSERT INTO public.settings VALUES ('dsa_percent', '40.0', 'Direct-seller (DSA) commission % of sale (on taxable value)', 'direct', '2026-09-24 18:08:26.905342+00', '2026-09-24 18:08:26.905342+00');
INSERT INTO public.settings VALUES ('gst_rate', '5.0', 'GST rate % on products', 'gst', '2026-09-24 18:08:26.905342+00', '2026-09-24 18:08:26.905342+00');
INSERT INTO public.settings VALUES ('price_gst_inclusive', 'false', 'Are DP/MRP prices GST-inclusive?', 'gst', '2026-09-24 18:08:26.905342+00', '2026-09-24 18:08:26.905342+00');
INSERT INTO public.settings VALUES ('company_legal_name', 'Arogyam Aradhya Herbs', 'Legal business name on invoice', 'gst', '2026-09-24 18:08:26.905342+00', '2026-09-24 18:08:26.905342+00');
INSERT INTO public.settings VALUES ('gstin', '09EJFPP4671A1Z5', 'Company GSTIN', 'gst', '2026-09-24 18:08:26.905342+00', '2026-09-24 18:08:26.905342+00');
INSERT INTO public.settings VALUES ('company_address', 'Varanasi, Uttar Pradesh', 'Company address on invoice', 'gst', '2026-09-24 18:08:26.905342+00', '2026-09-24 18:08:26.905342+00');
INSERT INTO public.settings VALUES ('company_state', 'Uttar Pradesh', 'Company state (place of supply)', 'gst', '2026-09-24 18:08:26.905342+00', '2026-09-24 18:08:26.905342+00');
INSERT INTO public.settings VALUES ('company_state_code', '09', 'GST state code (UP = 09)', 'gst', '2026-09-24 18:08:26.905342+00', '2026-09-24 18:08:26.905342+00');
INSERT INTO public.settings VALUES ('hsn_default', '30049011', 'Default HSN/SAC code for products', 'gst', '2026-09-24 18:08:26.905342+00', '2026-09-24 18:08:26.905342+00');
INSERT INTO public.settings VALUES ('invoice_prefix', 'INV', 'Invoice number prefix', 'gst', '2026-09-24 18:08:26.905342+00', '2026-09-24 18:08:26.905342+00');
INSERT INTO public.settings VALUES ('activation_sp', '25.0', 'Self-purchase SP (cumulative) to green an ID', 'eligibility', '2026-09-24 18:08:26.905342+00', '2026-09-24 18:08:26.905342+00');
INSERT INTO public.settings VALUES ('payout_min', '500.0', 'Minimum wallet balance to request payout (₹)', 'payout', '2026-09-24 18:08:26.905342+00', '2026-09-24 18:08:26.905342+00');
INSERT INTO public.settings VALUES ('tds_percent', '5.0', 'TDS deduction on payout %', 'payout', '2026-09-24 18:08:26.905342+00', '2026-09-24 18:08:26.905342+00');
INSERT INTO public.settings VALUES ('payout_day', 'Tuesday', 'Weekly payout closing day', 'payout', '2026-09-24 18:08:26.905342+00', '2026-09-24 18:08:26.905342+00');
INSERT INTO public.settings VALUES ('company_name', 'Arogyam Aradhya', 'Company name', 'site', '2026-09-24 18:08:26.905342+00', '2026-09-24 18:08:26.905342+00');
INSERT INTO public.settings VALUES ('support_phone', '+91 00000 00000', 'Support phone', 'site', '2026-09-24 18:08:26.905342+00', '2026-09-24 18:08:26.905342+00');
INSERT INTO public.settings VALUES ('support_email', 'support@arogyamaradhya.com', 'Support email', 'site', '2026-09-24 18:08:26.905342+00', '2026-09-24 18:08:26.905342+00');
INSERT INTO public.settings VALUES ('address', 'Varanasi, Uttar Pradesh', 'Company address', 'site', '2026-09-24 18:08:26.905342+00', '2026-09-24 18:08:26.905342+00');
INSERT INTO public.settings VALUES ('whatsapp_number', '919839227978', 'Company WhatsApp number (orders)', 'site', '2026-09-24 18:08:26.905342+00', '2026-09-24 18:08:26.905342+00');
INSERT INTO public.settings VALUES ('whatsapp_message', 'Welcome to Arogyam Aradhya! Here is my order detail and invoice. Please guide me for payment to the Admin account so I get all benefits.', 'WhatsApp order intro message', 'site', '2026-09-24 18:08:26.905342+00', '2026-09-24 18:08:26.905342+00');


--
-- Data for Name: sp_ledger; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- Data for Name: weekly_payouts; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- Name: admin_users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.admin_users_id_seq', 1, true);


--
-- Name: categories_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.categories_id_seq', 7, true);


--
-- Name: commission_ledger_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.commission_ledger_id_seq', 1, false);


--
-- Name: kyc_documents_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.kyc_documents_id_seq', 1, false);


--
-- Name: members_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.members_id_seq', 1, true);


--
-- Name: order_items_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.order_items_id_seq', 1, false);


--
-- Name: orders_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.orders_id_seq', 1, false);


--
-- Name: payout_requests_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.payout_requests_id_seq', 1, false);


--
-- Name: products_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.products_id_seq', 32, true);


--
-- Name: sp_ledger_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.sp_ledger_id_seq', 1, false);


--
-- Name: weekly_payouts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.weekly_payouts_id_seq', 1, false);


--
-- Name: admin_users admin_users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.admin_users
    ADD CONSTRAINT admin_users_pkey PRIMARY KEY (id);


--
-- Name: categories categories_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT categories_pkey PRIMARY KEY (id);


--
-- Name: commission_ledger commission_ledger_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.commission_ledger
    ADD CONSTRAINT commission_ledger_pkey PRIMARY KEY (id);


--
-- Name: kyc_documents kyc_documents_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.kyc_documents
    ADD CONSTRAINT kyc_documents_pkey PRIMARY KEY (id);


--
-- Name: members members_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.members
    ADD CONSTRAINT members_pkey PRIMARY KEY (id);


--
-- Name: order_items order_items_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.order_items
    ADD CONSTRAINT order_items_pkey PRIMARY KEY (id);


--
-- Name: orders orders_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_pkey PRIMARY KEY (id);


--
-- Name: payout_requests payout_requests_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payout_requests
    ADD CONSTRAINT payout_requests_pkey PRIMARY KEY (id);


--
-- Name: products products_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_pkey PRIMARY KEY (id);


--
-- Name: settings settings_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.settings
    ADD CONSTRAINT settings_pkey PRIMARY KEY (key);


--
-- Name: sp_ledger sp_ledger_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sp_ledger
    ADD CONSTRAINT sp_ledger_pkey PRIMARY KEY (id);


--
-- Name: kyc_documents uq_member_doctype; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.kyc_documents
    ADD CONSTRAINT uq_member_doctype UNIQUE (member_id, doc_type);


--
-- Name: weekly_payouts weekly_payouts_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.weekly_payouts
    ADD CONSTRAINT weekly_payouts_pkey PRIMARY KEY (id);


--
-- Name: ix_admin_users_username; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_admin_users_username ON public.admin_users USING btree (username);


--
-- Name: ix_categories_slug; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_categories_slug ON public.categories USING btree (slug);


--
-- Name: ix_commission_ledger_member_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_commission_ledger_member_id ON public.commission_ledger USING btree (member_id);


--
-- Name: ix_kyc_documents_member_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_kyc_documents_member_id ON public.kyc_documents USING btree (member_id);


--
-- Name: ix_members_email; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_members_email ON public.members USING btree (email);


--
-- Name: ix_members_member_id; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_members_member_id ON public.members USING btree (member_id);


--
-- Name: ix_members_parent_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_members_parent_id ON public.members USING btree (parent_id);


--
-- Name: ix_members_phone; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_members_phone ON public.members USING btree (phone);


--
-- Name: ix_members_segment; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_members_segment ON public.members USING btree (segment);


--
-- Name: ix_members_sponsor_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_members_sponsor_id ON public.members USING btree (sponsor_id);


--
-- Name: ix_order_items_order_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_order_items_order_id ON public.order_items USING btree (order_id);


--
-- Name: ix_orders_member_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_orders_member_id ON public.orders USING btree (member_id);


--
-- Name: ix_orders_order_no; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_orders_order_no ON public.orders USING btree (order_no);


--
-- Name: ix_payout_requests_member_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_payout_requests_member_id ON public.payout_requests USING btree (member_id);


--
-- Name: ix_products_category_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_products_category_id ON public.products USING btree (category_id);


--
-- Name: ix_products_slug; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_products_slug ON public.products USING btree (slug);


--
-- Name: ix_sp_ledger_member_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_sp_ledger_member_id ON public.sp_ledger USING btree (member_id);


--
-- Name: ix_weekly_payouts_member_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_weekly_payouts_member_id ON public.weekly_payouts USING btree (member_id);


--
-- Name: ix_weekly_payouts_period; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_weekly_payouts_period ON public.weekly_payouts USING btree (period);


--
-- Name: commission_ledger commission_ledger_member_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.commission_ledger
    ADD CONSTRAINT commission_ledger_member_id_fkey FOREIGN KEY (member_id) REFERENCES public.members(id);


--
-- Name: kyc_documents kyc_documents_member_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.kyc_documents
    ADD CONSTRAINT kyc_documents_member_id_fkey FOREIGN KEY (member_id) REFERENCES public.members(id);


--
-- Name: members members_parent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.members
    ADD CONSTRAINT members_parent_id_fkey FOREIGN KEY (parent_id) REFERENCES public.members(id);


--
-- Name: members members_sponsor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.members
    ADD CONSTRAINT members_sponsor_id_fkey FOREIGN KEY (sponsor_id) REFERENCES public.members(id);


--
-- Name: order_items order_items_order_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.order_items
    ADD CONSTRAINT order_items_order_id_fkey FOREIGN KEY (order_id) REFERENCES public.orders(id);


--
-- Name: order_items order_items_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.order_items
    ADD CONSTRAINT order_items_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(id);


--
-- Name: orders orders_member_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_member_id_fkey FOREIGN KEY (member_id) REFERENCES public.members(id);


--
-- Name: payout_requests payout_requests_member_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payout_requests
    ADD CONSTRAINT payout_requests_member_id_fkey FOREIGN KEY (member_id) REFERENCES public.members(id);


--
-- Name: products products_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.categories(id);


--
-- Name: sp_ledger sp_ledger_member_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sp_ledger
    ADD CONSTRAINT sp_ledger_member_id_fkey FOREIGN KEY (member_id) REFERENCES public.members(id);


--
-- Name: sp_ledger sp_ledger_order_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sp_ledger
    ADD CONSTRAINT sp_ledger_order_id_fkey FOREIGN KEY (order_id) REFERENCES public.orders(id);


--
-- Name: sp_ledger sp_ledger_source_member_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sp_ledger
    ADD CONSTRAINT sp_ledger_source_member_id_fkey FOREIGN KEY (source_member_id) REFERENCES public.members(id);


--
-- Name: weekly_payouts weekly_payouts_member_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.weekly_payouts
    ADD CONSTRAINT weekly_payouts_member_id_fkey FOREIGN KEY (member_id) REFERENCES public.members(id);


--
-- PostgreSQL database dump complete
--

\unrestrict UNB5rVaeIw5XBd9hgoUeIdpO4PYjXPmkUyZFgp5En4hvRs2VFp88o9AQkgBKEVz

