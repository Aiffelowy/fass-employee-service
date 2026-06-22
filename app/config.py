from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "employee-service";

    KAFKA_BOOTSTRAP_SERVERS: str = "kafka:9092";
    KAFKA_CONSUME_TOPIC: str = "employee.account-activated,employee.activation-expired"
    KAFKA_PRODUCE_TOPIC: str = "employee.profile-created";
    KAFKA_GROUP_ID: str = "employee-service-group";

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    class Config:
        env_file = ".env";

settings = Settings();
