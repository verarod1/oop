import json
import os


class FileManager:
    @staticmethod
    def save_project(filename: str, data: dict) -> bool:
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print(f"Файл успешно сохранен: {filename}")
            return True
        except Exception as e:
            print(f"Ошибка записи файла: {e}")
            raise e

    @staticmethod
    def load_project(filename: str) -> dict:
        if not os.path.exists(filename):
            raise FileNotFoundError(f"Файл не найден: {filename}")

        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            raise ValueError("Файл поврежден или имеет неверный формат")
        except Exception as e:
            print(f"Ошибка чтения файла: {e}")
            raise e