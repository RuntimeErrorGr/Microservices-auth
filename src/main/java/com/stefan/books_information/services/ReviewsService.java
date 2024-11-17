package com.stefan.books_information.services;

import com.stefan.books_information.dtos.AddReviewPayloadDTO;
import com.stefan.books_information.models.Review;
import com.stefan.books_information.repositories.BooksRepository;
import com.stefan.books_information.repositories.ReviewsRepository;
import com.stefan.books_information.repositories.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;


@RequiredArgsConstructor

@Service
public class ReviewsService {
    private final ReviewsRepository reviewsRepository;
    private final BooksRepository booksRepository;
    private final UserRepository userRepository;

    public List<Review> findReviewsByBookIsbn(String bookIsbn){
        return reviewsRepository.findReviewsByBook_Isbn(bookIsbn);
    }

    public Review addReview(AddReviewPayloadDTO addReviewPayloadDTO){
        Review review = new Review();
        review.setBook(booksRepository.findByIsbn(addReviewPayloadDTO.getBookIsbn()));
        review.setUser(userRepository.findById(addReviewPayloadDTO.getUserId()).orElseThrow());
        review.setReviewText(addReviewPayloadDTO.getReviewText());
        review.setReviewDate(LocalDateTime.now());

        reviewsRepository.save(review);
        return review;
    }

    public String deleteReview(Long id) {
        Review reviewToBeDeleted = reviewsRepository.findById(id).orElseThrow();

        reviewsRepository.delete(reviewToBeDeleted);

        return "Deleted review with ID: " + id;
    }
}
