-- Ensure schema is public
SET search_path = public;

-- Create users table
CREATE TABLE public.users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    keycloak_id VARCHAR(36) NOT NULL
);

-- Create books table
CREATE TABLE public.books (
    book_id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(255) NOT NULL,
    genre VARCHAR(100),
    publication_date DATE,
    isbn VARCHAR(20) UNIQUE,
    status SMALLINT DEFAULT 0 CHECK (status >= 0 AND status <= 2),
    description TEXT
);

-- Create ratings table
CREATE TABLE public.ratings (
    rating_id SERIAL PRIMARY KEY,
    book_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    rating SMALLINT CHECK (rating >= 1 AND rating <= 5),
    rated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT ratings_book_id_fkey FOREIGN KEY (book_id) REFERENCES public.books (book_id) ON DELETE CASCADE,
    CONSTRAINT ratings_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users (user_id) ON DELETE CASCADE
);

-- Create reviews table
CREATE TABLE public.reviews (
    review_id SERIAL PRIMARY KEY,
    book_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    status SMALLINT DEFAULT 0 CHECK (status >= 0 AND status <= 2),
    review_text TEXT,
    review_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT reviews_book_id_fkey FOREIGN KEY (book_id) REFERENCES public.books (book_id) ON DELETE CASCADE,
    CONSTRAINT reviews_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users (user_id) ON DELETE CASCADE
);

-- Insert initial data into users table
INSERT INTO public.users (username, email, registered_at, keycloak_id)
VALUES
    ('book-lover', 'book-lover@example.com', '2024-11-17 14:45:11', 'dummy-keycloak-id-0000-0000-00000000'),
    ('avid-reader', 'avid-reader@example.com', '2024-11-17 14:45:11', 'dummy-keycloak-id-0000-0000-00000000'),
    ('book-user', 'book-user@example.com', '2025-01-01 14:45:11', 'dummy-keycloak-id-0000-0000-00000000');

-- Insert initial data into books table
INSERT INTO public.books (title, author, genre, publication_date, isbn, description, status)
VALUES 
    ('The Great Gatsby', 'F. Scott Fitzgerald', 'Fiction', '1925-04-10', '9780743273565', 'A novel set in the Jazz Age.', 1),
    ('To Kill a Mockingbird', 'Harper Lee', 'Fiction', '1960-07-11', '9780060935467', 'A tale of racial injustice and childhood innocence.', 1);

-- Insert initial data into ratings table
INSERT INTO public.ratings (book_id, user_id, rating, rated_at)
VALUES
    (1, 1, 5, '2024-11-17 14:45:11'),
    (2, 2, 4, '2024-11-17 14:45:11');

-- Insert initial data into reviews table
INSERT INTO public.reviews (book_id, user_id, review_text, review_date, status)
VALUES
    (1, 1, 'An amazing read with deep symbolism.', '2024-11-17 14:45:11', 1),
    (2, 2, 'A must-read for everyone.', '2024-11-17 14:45:11', 1);

-- Update sequences
SELECT pg_catalog.setval('public.books_book_id_seq', COALESCE(MAX(book_id), 1), TRUE) FROM public.books;
SELECT pg_catalog.setval('public.ratings_rating_id_seq', COALESCE(MAX(rating_id), 1), TRUE) FROM public.ratings;
SELECT pg_catalog.setval('public.reviews_review_id_seq', COALESCE(MAX(review_id), 1), TRUE) FROM public.reviews;
SELECT pg_catalog.setval('public.users_user_id_seq', COALESCE(MAX(user_id), 1), TRUE) FROM public.users;
