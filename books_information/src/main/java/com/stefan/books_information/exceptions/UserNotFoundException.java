package com.stefan.books_information.exceptions;

public class UserNotFoundException extends RuntimeException {
    public UserNotFoundException(String keycloakId) {
        super("User with keycloak ID " + keycloakId + " not found.");
    }
}