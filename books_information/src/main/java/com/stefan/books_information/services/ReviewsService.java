package com.stefan.books_information.services;

import com.stefan.books_information.dtos.AddReviewPayloadDTO;
import com.stefan.books_information.models.Review;
import com.stefan.books_information.models.Status;
import com.stefan.books_information.repositories.BooksRepository;
import com.stefan.books_information.repositories.ReviewsRepository;
import com.stefan.books_information.repositories.UserRepository;
import com.stefan.books_information.exceptions.UserNotFoundException;
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

    public List<Review> findAllReviews(){
        return reviewsRepository.findAll();
    }

    public List<Review> findPendingReviews(){
        return reviewsRepository.findByStatus(Status.PENDING);
    }

    public List<Review> findApprovedReviews(){
        return reviewsRepository.findByStatus(Status.APPROVED);
    }

    public List<Review> findRejectedReviews(){
        return reviewsRepository.findByStatus(Status.REJECTED);
    }

    public List<Review> findPendingReviewsByBookIsbn(String bookIsbn){
        return reviewsRepository.findByStatus(Status.PENDING).stream().filter(review -> review.getBook().getIsbn().equals(bookIsbn)).toList();
    }

    public List<Review> findApprovedReviewsByBookIsbn(String bookIsbn){
        return reviewsRepository.findByStatus(Status.APPROVED).stream().filter(review -> review.getBook().getIsbn().equals(bookIsbn)).toList();
    }
    
    public List<Review> findRejectedReviewsByBookIsbn(String bookIsbn){
        return reviewsRepository.findByStatus(Status.REJECTED).stream().filter(review -> review.getBook().getIsbn().equals(bookIsbn)).toList();
    }

    public Review addReview(AddReviewPayloadDTO addReviewPayloadDTO){
        Review review = new Review();
        review.setBook(booksRepository.findByIsbn(addReviewPayloadDTO.getBookIsbn()));
        review.setUser(userRepository.findByKeycloakId(addReviewPayloadDTO.getKeycloakId()).orElseThrow(() -> new UserNotFoundException(addReviewPayloadDTO.getKeycloakId())));
        review.setReviewText(addReviewPayloadDTO.getReviewText());
        review.setReviewDate(LocalDateTime.now());
        review.setStatus(Status.PENDING);
        reviewsRepository.save(review);
        return review;
    }

    public Review approveReview(Long id){
        Review reviewToBeApproved = reviewsRepository.findById(id).orElseThrow();
        reviewToBeApproved.setStatus(Status.APPROVED);
        reviewsRepository.save(reviewToBeApproved);
        return reviewToBeApproved;
    }

    public Review rejectReview(Long id){
        Review reviewToBeRejected = reviewsRepository.findById(id).orElseThrow();
        reviewToBeRejected.setStatus(Status.REJECTED);
        reviewsRepository.save(reviewToBeRejected);
        return reviewToBeRejected;
    }

    public String deleteReview(Long id) {
        Review reviewToBeDeleted = reviewsRepository.findById(id).orElseThrow();

        reviewsRepository.delete(reviewToBeDeleted);

        return "Deleted review with ID: " + id;
    }
}
