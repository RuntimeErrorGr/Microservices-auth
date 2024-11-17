package com.stefan.books_information.controllers;

import com.stefan.books_information.models.Book;
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

@RestController
@RequestMapping("books")
@RequiredArgsConstructor
public class BooksController {
    private final BooksService booksService;

    @GetMapping
    public List<Book> getAllBooks() {
        return booksService.findAllBooks();
    }

    @GetMapping("{isbn}")
    public Book getBookByIsbn(@PathVariable String isbn) {
        return booksService.findByIsbn(isbn);
    }

    @PostMapping("add")
    public Book addBook(@RequestBody Book newBook) {
        return booksService.addBook(newBook);
    }

    @PutMapping("update/{id}")
    public Book updateBook(@PathVariable Long id, @RequestBody Book updatedBook) {
        return booksService.updateBook(id, updatedBook);
    }

    @DeleteMapping("delete/{id}")
    public String deleteBook(@PathVariable Long id) {
        return booksService.deleteBook(id);
    }
}
