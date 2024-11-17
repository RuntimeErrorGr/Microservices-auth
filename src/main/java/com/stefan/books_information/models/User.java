package com.stefan.books_information.models;

import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import lombok.Data;

@Data
@Entity
@Table(name = "users", schema = "public")
public class User {

    @Id
    private Long userId;
    private String username;
    private String email;
    private java.sql.Timestamp registeredAt;
}
