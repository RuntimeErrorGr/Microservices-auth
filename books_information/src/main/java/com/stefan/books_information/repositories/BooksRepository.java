package com.stefan.books_information.repositories;

import com.stefan.books_information.models.Book;
import com.stefan.books_information.models.Status;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface BooksRepository extends JpaRepository<Book, Long> {
    Book findByIsbn(String isbn);
    List<Book> findByStatus(Status status);
}