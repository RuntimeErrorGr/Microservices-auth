package com.stefan.books_information.dtos;

import lombok.AllArgsConstructor;
import lombok.Data;

@Data
@AllArgsConstructor
public class AddReviewPayloadDTO {
    private String bookIsbn;
    private Long userId;
    private String reviewText;
}
