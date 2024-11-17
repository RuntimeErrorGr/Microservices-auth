package com.stefan.books_information.models;


import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.Table;
import lombok.Data;

@Data
@Entity
@Table(name = "ratings", schema = "public")
public class Rating {

    @Id
    private Long ratingId;
    @ManyToOne
    @JoinColumn(name = "book_id")
    private Book book;
    private Long userId;
    private Long rating;
    private java.sql.Timestamp ratedAt;

}
