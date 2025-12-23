FROM maven:3.8-openjdk-17 AS builder

WORKDIR /app
COPY pom.xml .
COPY src ./src

RUN mvn clean package

# This stage is just to make the artifact easily accessible
FROM alpine:latest
COPY --from=builder /app/target/role-auto-assigner-1.0.0.jar /role-auto-assigner-1.0.0.jar
CMD ["sh", "-c", "cp /role-auto-assigner-1.0.0.jar /out/role-auto-assigner.jar"]
