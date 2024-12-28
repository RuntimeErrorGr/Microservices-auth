package com.stefan.books_information.services;

import com.stefan.books_information.exceptions.BookNotFoundException;
import com.stefan.books_information.models.Book;
import com.stefan.books_information.repositories.BooksRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;

@RequiredArgsConstructor

@Service
public class BooksService {
    private final BooksRepository booksRepository;

    public List<Book> findAllBooks(){
        return booksRepository.findAll();
    }

    public Book findByIsbn(String isbn){
        return booksRepository.findByIsbn(isbn);
    }

    public String findTitleByIsbn(String isbn){
        return booksRepository.findByIsbn(isbn).getTitle();
    }

    public Book addBook(Book newBook){
        return booksRepository.save(newBook);
    }

    public Book updateBook(Long bookId, Book updatedBook){
        Book existingBook = booksRepository.findById(bookId)
                .orElseThrow(() -> new BookNotFoundException(bookId));

        existingBook.setTitle(updatedBook.getTitle());
        existingBook.setAuthor(updatedBook.getAuthor());
        existingBook.setGenre(updatedBook.getGenre());
        existingBook.setPublicationDate(updatedBook.getPublicationDate());
        existingBook.setIsbn(updatedBook.getIsbn());
        existingBook.setDescription(updatedBook.getDescription());

        return booksRepository.save(existingBook);
    }

    public String deleteBook(Long bookId){
        Book existingBook = booksRepository.findById(bookId)
                .orElseThrow(() -> new BookNotFoundException(bookId));

        booksRepository.delete(existingBook);

        return "Deleted book with ID " + bookId;
    }

}
