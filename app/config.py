from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "employee-service";

    KAFKA_BOOTSTRAP_SERVERS: str = "kafka:9092";
    KAFKA_CONSUME_TOPIC: str = "employee.account-activated,employee.activation-expired"
    KAFKA_PRODUCE_TOPIC: str = "employee.profile-created";
    KAFKA_GROUP_ID: str = "employee-service-group";

    DATABASE_URL :str;

    class Config:
        env_file = ".env";
        extra = "ignore";

settings = Settings();
