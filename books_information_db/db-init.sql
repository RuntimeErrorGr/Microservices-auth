CREATE DATABASE book_reviews;

-- public.books definition

-- Drop table

-- DROP TABLE public.books;

CREATE TABLE public.books (
	book_id serial4 NOT NULL,
	title varchar(255) NOT NULL,
	author varchar(255) NOT NULL,
	genre varchar(100) NULL,
	publication_date date NULL,
	isbn varchar(20) NULL,
	description text NULL,
	CONSTRAINT books_isbn_key UNIQUE (isbn),
	CONSTRAINT books_pkey PRIMARY KEY (book_id)
);


-- public.users definition

-- Drop table

-- DROP TABLE public.users;

CREATE TABLE public.users (
	user_id serial4 NOT NULL,
	username varchar(50) NOT NULL,
	email varchar(255) NOT NULL,
	registered_at timestamp NULL DEFAULT CURRENT_TIMESTAMP,
	CONSTRAINT users_email_key UNIQUE (email),
	CONSTRAINT users_pkey PRIMARY KEY (user_id),
	CONSTRAINT users_username_key UNIQUE (username)
);


-- public.ratings definition

-- Drop table

-- DROP TABLE public.ratings;

CREATE TABLE public.ratings (
	rating_id serial4 NOT NULL,
	book_id int4 NOT NULL,
	user_id int4 NOT NULL,
	rating int2 NULL,
	rated_at timestamp NULL DEFAULT CURRENT_TIMESTAMP,
	CONSTRAINT ratings_pkey PRIMARY KEY (rating_id),
	CONSTRAINT ratings_rating_check CHECK (((rating >= 1) AND (rating <= 5))),
	CONSTRAINT ratings_book_id_fkey FOREIGN KEY (book_id) REFERENCES public.books(book_id) ON DELETE CASCADE,
	CONSTRAINT ratings_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id) ON DELETE CASCADE
);


-- public.reviews definition

-- Drop table

-- DROP TABLE public.reviews;

CREATE TABLE public.reviews (
	review_id serial4 NOT NULL,
	book_id int4 NOT NULL,
	user_id int4 NOT NULL,
	review_text text NULL,
	review_date timestamp NULL DEFAULT CURRENT_TIMESTAMP,
	CONSTRAINT reviews_pkey PRIMARY KEY (review_id),
	CONSTRAINT reviews_book_id_fkey FOREIGN KEY (book_id) REFERENCES public.books(book_id) ON DELETE CASCADE,
	CONSTRAINT reviews_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id) ON DELETE CASCADE
);

INSERT INTO public.books
(book_id, title, author, genre, publication_date, isbn, description)
VALUES(1, 'The Great Gatsby', 'F. Scott Fitzgerald', 'Fiction', '1925-04-10', '9780743273565', 'A novel set in the Jazz Age.');
INSERT INTO public.books
(book_id, title, author, genre, publication_date, isbn, description)
VALUES(2, 'To Kill a Mockingbird', 'Harper Lee', 'Fiction', '1960-07-11', '9780060935467', 'A tale of racial injustice and childhood innocence.');

INSERT INTO public.reviews
(review_id, book_id, user_id, review_text, review_date)
VALUES(1, 1, 1, 'An amazing read with deep symbolism.', '2024-11-17 14:45:11.574');
INSERT INTO public.reviews
(review_id, book_id, user_id, review_text, review_date)
VALUES(2, 2, 2, 'A must-read for everyone.', '2024-11-17 14:45:11.574');

INSERT INTO public.ratings
(rating_id, book_id, user_id, rating, rated_at)
VALUES(1, 1, 1, 5, '2024-11-17 14:45:11.579');
INSERT INTO public.ratings
(rating_id, book_id, user_id, rating, rated_at)
VALUES(2, 2, 2, 4, '2024-11-17 14:45:11.579');

INSERT INTO public.users
(user_id, username, email, registered_at)
VALUES(1, 'booklover', 'booklover@example.com', '2024-11-17 14:45:11.568');
INSERT INTO public.users
(user_id, username, email, registered_at)
VALUES(2, 'avidreader', 'avidreader@example.com', '2024-11-17 14:45:11.568');
