package com.stefan.books_information.controllers;

import com.stefan.books_information.models.Book;
import com.stefan.books_information.models.Rating;
import com.stefan.books_information.services.BooksService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("books")
@RequiredArgsConstructor
public class BooksController {
    private final BooksService booksService;

    @GetMapping
    public List<Book> getAllBooks() {
        return booksService.findAllBooks();
    }

    @GetMapping("pending")
    public List<Book> getPendingBooks() {
        return booksService.findPendingBooks();
    }

    @GetMapping("approved")
    public List<Book> getApprovedBooks() {
        return booksService.findApprovedBooks();
    }

    @GetMapping("rejected")
    public List<Book> getRejectedBooks() {
        return booksService.findRejectedBooks();
    }

    @GetMapping("{isbn}")
    public Book getBookByIsbn(@PathVariable String isbn) {
        return booksService.findByIsbn(isbn);
    }

    @GetMapping("/ratings/{isbn}")
    public List<Rating> getBookRatingsByIsbn(@PathVariable String isbn) {
        return booksService.findRatingsByIsbn(isbn);
    }

    @GetMapping("/title/{isbn}")
    public Map<String, String> getBookTitleByIsbn(@PathVariable String isbn) {
        return booksService.findTitleByIsbn(isbn);
    }

    @PostMapping("add")
    public Book addBook(@RequestBody Book newBook) {
        return booksService.addBook(newBook);
    }

    @PutMapping("update/{id}")
    public Book updateBook(@PathVariable Long id, @RequestBody Book updatedBook) {
        return booksService.updateBook(id, updatedBook);
    }

    @GetMapping("approve/{id}")
    public Book approveBook(@PathVariable Long id) {
        return booksService.approveBook(id);
    }

    @GetMapping("reject/{id}")
    public Book rejectBook(@PathVariable Long id) {
        return booksService.rejectBook(id);
    }

    @DeleteMapping("delete/{id}")
    public String deleteBook(@PathVariable Long id) {
        return booksService.deleteBook(id);
    }
}
