--
-- Name: books; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.books (
    book_id integer NOT NULL,
    title character varying(255) NOT NULL,
    author character varying(255) NOT NULL,
    genre character varying(100),
    publication_date date,
    isbn character varying(20),
    status smallint DEFAULT 0,
    description text,
    CONSTRAINT status_check CHECK (
        (
            (status >= 0)
            AND (status <= 2)
        )
    )
);

ALTER TABLE public.books OWNER TO postgres;

--
-- Name: books_book_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.books_book_id_seq AS integer START
WITH
    1 INCREMENT BY 1 NO MINVALUE NO MAXVALUE CACHE 1;

ALTER SEQUENCE public.books_book_id_seq OWNER TO postgres;

--
-- Name: books_book_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.books_book_id_seq OWNED BY public.books.book_id;

--
-- Name: ratings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.ratings (
    rating_id integer NOT NULL,
    book_id integer NOT NULL,
    user_id integer NOT NULL,
    rating smallint,
    rated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT ratings_rating_check CHECK (
        (
            (rating >= 1)
            AND (rating <= 5)
        )
    )
);

ALTER TABLE public.ratings OWNER TO postgres;

--
-- Name: ratings_rating_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.ratings_rating_id_seq AS integer START
WITH
    1 INCREMENT BY 1 NO MINVALUE NO MAXVALUE CACHE 1;

ALTER SEQUENCE public.ratings_rating_id_seq OWNER TO postgres;

--
-- Name: ratings_rating_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.ratings_rating_id_seq OWNED BY public.ratings.rating_id;

--
-- Name: reviews; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.reviews (
    review_id integer NOT NULL,
    book_id integer NOT NULL,
    user_id integer NOT NULL,
    status smallint DEFAULT 0,
    review_text text,
    review_date timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT reviews_status_check CHECK (
        (
            (status >= 0)
            AND (status <= 2)
        )
    )
);

ALTER TABLE public.reviews OWNER TO postgres;

--
-- Name: reviews_review_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.reviews_review_id_seq AS integer START
WITH
    1 INCREMENT BY 1 NO MINVALUE NO MAXVALUE CACHE 1;

ALTER SEQUENCE public.reviews_review_id_seq OWNER TO postgres;

--
-- Name: reviews_review_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.reviews_review_id_seq OWNED BY public.reviews.review_id;

--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    user_id integer NOT NULL,
    username character varying(50) NOT NULL,
    email character varying(255) NOT NULL,
    registered_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    keycloak_id character varying(36) NOT NULL
);

ALTER TABLE public.users OWNER TO postgres;

--
-- Name: users_user_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_user_id_seq AS integer START
WITH
    1 INCREMENT BY 1 NO MINVALUE NO MAXVALUE CACHE 1;

ALTER SEQUENCE public.users_user_id_seq OWNER TO postgres;

--
-- Name: users_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_user_id_seq OWNED BY public.users.user_id;

--
-- Name: books book_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.books ALTER COLUMN book_id SET DEFAULT nextval('public.books_book_id_seq'::regclass);

--
-- Name: ratings rating_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ratings ALTER COLUMN rating_id SET DEFAULT nextval('public.ratings_rating_id_seq'::regclass);

--
-- Name: reviews review_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reviews ALTER COLUMN review_id SET DEFAULT nextval('public.reviews_review_id_seq'::regclass);

--
-- Name: users user_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN user_id SET DEFAULT nextval('public.users_user_id_seq'::regclass);

--
-- Data for Name: books; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.books (
    book_id,
    title,
    author,
    genre,
    publication_date,
    isbn,
    description,
    status
)
FROM stdin;

1	The Great Gatsby	F. Scott Fitzgerald	Fiction	1925-04-10	9780743273565	A novel set in the Jazz Age.	1
2	To Kill a Mockingbird	Harper Lee	Fiction	1960-07-11	9780060935467	A tale of racial injustice and childhood innocence.	1
\.

--
-- Data for Name: ratings; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.ratings (
    rating_id,
    book_id,
    user_id,
    rating,
    rated_at
)
FROM stdin;

1	1	1	5	2024-11-17 14:45:11.579271
2	2	2	4	2024-11-17 14:45:11.579271
\.

--
-- Data for Name: reviews; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.reviews (
    review_id,
    book_id,
    user_id,
    review_text,
    review_date,
    status
)
FROM stdin;

1	1	1	An amazing read with deep symbolism.	2024-11-17 14:45:11.574058	1
2	2	2	A must-read for everyone.	2024-11-17 14:45:11.574058	1
\.

--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (
    user_id,
    username,
    email,
    registered_at
)
FROM stdin;

1	book-lover	book-lover@example.com	2024-11-17 14:45:11.568427
2	avid-reader	avid-reader@example.com	2024-11-17 14:45:11.568427
3   book-user	book-user@example.com	2025-01-01 14:45:11.000000 
\.

--
-- Name: books_book_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval ( 'public.books_book_id_seq', 3, true );

--
-- Name: ratings_rating_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval ( 'public.ratings_rating_id_seq', 2, true );

--
-- Name: reviews_review_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval ( 'public.reviews_review_id_seq', 4, true );

--
-- Name: users_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval ( 'public.users_user_id_seq', 2, true );

--
-- Name: books books_isbn_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.books
ADD CONSTRAINT books_isbn_key UNIQUE (isbn);

--
-- Name: books books_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.books
ADD CONSTRAINT books_pkey PRIMARY KEY (book_id);

--
-- Name: ratings ratings_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ratings
ADD CONSTRAINT ratings_pkey PRIMARY KEY (rating_id);

--
-- Name: reviews reviews_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reviews
ADD CONSTRAINT reviews_pkey PRIMARY KEY (review_id);

--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
ADD CONSTRAINT users_email_key UNIQUE (email);

--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
ADD CONSTRAINT users_pkey PRIMARY KEY (user_id);

--
-- Name: users users_username_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
ADD CONSTRAINT users_username_key UNIQUE (username);

--
-- Name: ratings ratings_book_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ratings
ADD CONSTRAINT ratings_book_id_fkey FOREIGN KEY (book_id) REFERENCES public.books (book_id) ON DELETE CASCADE;

--
-- Name: ratings ratings_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ratings
ADD CONSTRAINT ratings_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users (user_id) ON DELETE CASCADE;

--
-- Name: reviews reviews_book_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reviews
ADD CONSTRAINT reviews_book_id_fkey FOREIGN KEY (book_id) REFERENCES public.books (book_id) ON DELETE CASCADE;

--
-- Name: reviews reviews_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reviews
ADD CONSTRAINT reviews_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users (user_id) ON DELETE CASCADE;

--
-- Add keycloak_id column to users table
--
ALTER TABLE public.users
ADD COLUMN keycloak_id character varying(36) NOT NULL;

--
-- Populate keycloak_id for existing users
--
UPDATE public.users
SET
    keycloak_id = '59d5303e-997c-4995-a5a5-a456968700d9'
WHERE
    username = 'book-lover';

UPDATE public.users
SET
    keycloak_id = 'dummy-keycloak-id-0000-0000-000000000000'
WHERE
    username = 'avid-reader';

--
-- Ensure keycloak_id is mandatory for all users
--
ALTER TABLE public.users ALTER COLUMN keycloak_id;

--
-- Updated table structure for users
--
--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (
    user_id,
    username,
    email,
    registered_at,
    keycloak_id
)
FROM stdin;

1	book-lover	book-lover@example.com	2024-11-17 14:45:11.568427	59d5303e-997c-4995-a5a5-a456968700d9
2	avid-reader	avid-reader@example.com	2024-11-17 14:45:11.568427	dummy-keycloak-id-0000-0000-000000000000
3	book-user	book-user@example.com	2025-01-01 14:45:11.000000	40949a41-7432-40db-bb25-90dd7c55f2e8
\.

-- PostgreSQL database dump complete
--