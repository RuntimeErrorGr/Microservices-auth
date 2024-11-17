package com.stefan.books_information.controllers;

import com.stefan.books_information.dtos.AddReviewPayloadDTO;
import com.stefan.books_information.models.Review;
import com.stefan.books_information.services.ReviewsService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController

@RequestMapping("reviews")
@RequiredArgsConstructor
public class ReviewsController {
    private final ReviewsService reviewsService;

    @GetMapping("by-isbn/{isbn}")
    public List<Review> getReviewsByBookIsbn(@PathVariable String isbn){
        return reviewsService.findReviewsByBookIsbn(isbn);
    }

    @PostMapping("add")
    public Review addReview(@RequestBody AddReviewPayloadDTO addReviewPayloadDTO){
        return reviewsService.addReview(addReviewPayloadDTO);
    }

    @DeleteMapping("delete/{id}")
    public String deleteReview(@PathVariable Long id){
        return reviewsService.deleteReview(id);
    }
}
