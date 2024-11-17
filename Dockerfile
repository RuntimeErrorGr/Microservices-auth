FROM maven:3.8.7-eclipse-temurin-19 AS build
COPY src /home/app/src
COPY pom.xml /home/app
RUN mvn -f /home/app/pom.xml clean package

FROM eclipse-temurin:19-jdk-alpine
COPY --from=build /home/app/target/books_information-0.0.1-SNAPSHOT.war /books_information.war
EXPOSE 8080
CMD ["java", "-jar", "/books_information.war"]