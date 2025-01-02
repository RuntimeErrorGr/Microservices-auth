package com.stefan.books_information.services;
import java.util.HashMap;
import java.util.Map;
import com.stefan.books_information.exceptions.BookNotFoundException;
import com.stefan.books_information.models.Book;
import com.stefan.books_information.models.Rating;
import com.stefan.books_information.models.Status;
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

    public List<Book> findPendingBooks(){
        return booksRepository.findByStatus(Status.PENDING);
    }

    public List<Book> findApprovedBooks(){
        return booksRepository.findByStatus(Status.APPROVED);
    }

    public List<Book> findRejectedBooks(){
        return booksRepository.findByStatus(Status.REJECTED);
    }

    public Book findByIsbn(String isbn){
        return booksRepository.findByIsbn(isbn);
    }

    public Map<String, String> findTitleByIsbn(String isbn) {
        Book book = booksRepository.findByIsbn(isbn);
        Map<String, String> result = new HashMap<>();
        result.put(book.getBookId().toString(), book.getTitle());
        return result;
    }

    public List<Rating> findRatingsByIsbn(String isbn) {
        return booksRepository.findByIsbn(isbn).getRatings();
    }

    public Book addBook(Book newBook){
        if (newBook.getStatus() == null){
            newBook.setStatus(Status.PENDING);
        }
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

    public Book approveBook(Long bookId){
        Book existingBook = booksRepository.findById(bookId)
                .orElseThrow(() -> new BookNotFoundException(bookId));

        existingBook.setStatus(Status.APPROVED);

        return booksRepository.save(existingBook);
    }

    public Book rejectBook(Long bookId){
        Book existingBook = booksRepository.findById(bookId)
                .orElseThrow(() -> new BookNotFoundException(bookId));

        existingBook.setStatus(Status.REJECTED);

        return booksRepository.save(existingBook);
    }

    public String deleteBook(Long bookId){
        Book existingBook = booksRepository.findById(bookId)
                .orElseThrow(() -> new BookNotFoundException(bookId));

        booksRepository.delete(existingBook);

        return "Deleted book with ID " + bookId;
    }

}
