package com.stefan.books_information.repositories;

import com.stefan.books_information.models.Book;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface BooksRepository extends JpaRepository<Book, Long> {
    Book findByIsbn(String isbn);
}
