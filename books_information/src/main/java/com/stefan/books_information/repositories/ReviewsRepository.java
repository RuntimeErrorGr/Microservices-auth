package com.stefan.books_information.repositories;

import com.stefan.books_information.models.Review;
import com.stefan.books_information.models.Status;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface ReviewsRepository extends JpaRepository<Review, Long> {
    List<Review> findReviewsByBook_Isbn(String bookIsbn);
    List<Review> findByStatus(Status status);
}
