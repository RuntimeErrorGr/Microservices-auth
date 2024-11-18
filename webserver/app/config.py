from dataclasses import dataclass
import os
import dotenv


basedir = os.path.abspath(os.path.dirname(__file__))
dotenv.load_dotenv()


@dataclass
class Config:
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "webserver")
    PROJECT_ROOT: str = os.path.abspath(os.path.dirname(__file__))
    LOG_FOLDER: str = os.path.join(PROJECT_ROOT, "logs")
    FLASK_DEBUG: bool = False
