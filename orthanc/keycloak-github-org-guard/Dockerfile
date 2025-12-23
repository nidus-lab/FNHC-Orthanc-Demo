FROM maven:3.8-openjdk-17 AS builder

WORKDIR /app
COPY pom.xml .
COPY src ./src

RUN mvn clean package

# This stage is just to make the artifact easily accessible
FROM alpine:latest
COPY --from=builder /app/target/github-org-guard-1.0.0.jar /github-org-guard-1.0.0.jar
CMD ["cp", "/github-org-guard-1.0.0.jar", "/out/github-org-guard.jar"]
