import argparse
import asyncio
import logging
from aiopath import AsyncPath
from aioshutil import copyfile

# Налаштування логування
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


async def read_folder(path: AsyncPath, output: AsyncPath) -> None:
    """
    Асинхронна функція, яка рекурсивно читає всі файли у вихідній папці
    та її підпапках. Для кожного файлу створюється асинхронне завдання
    копіювання.
    """
    tasks = []
    async for item in path.rglob("*"):
        if await item.is_file():
            tasks.append(copy_file(item, output))
    await asyncio.gather(*tasks)


async def copy_file(file: AsyncPath, output: AsyncPath) -> None:
    """
    Асинхронна функція для копіювання файлу у відповідну папку на основі
    його розширення. Якщо розширення відсутнє, файл копіюється до папки
    "other".
    """
    try:
        extension_name = file.suffix[1:] if file.suffix else "other"
        extension_folder = output / extension_name
        await extension_folder.mkdir(exist_ok=True, parents=True)
        await copyfile(file, extension_folder / file.name)
        logging.info(f"Файл {file.name} скопійовано до {extension_folder}")
    except Exception as e:
        logging.error(f"Помилка копіювання файлу {file.name}: {e}")


async def main():
    """
    Головна асинхронна функція для обробки аргументів командного рядка
    та запуску читання папки.
    """
    parser = argparse.ArgumentParser(
        description="Асинхронне сортування файлів за розширеннями."
    )
    parser.add_argument("source", type=str, help="Шлях до вихідної папки")
    parser.add_argument("output", type=str, help="Шлях до цільової папки")
    args = parser.parse_args()

    source = AsyncPath(args.source)
    output = AsyncPath(args.output)

    # Перевірка існування вихідної папки
    if not (await source.exists() and await source.is_dir()):
        logging.error("Вказана вихідна папка не існує або не є директорією.")
        return

    # Запуск асинхронного читання та копіювання файлів
    await read_folder(source, output)


if __name__ == "__main__":
    asyncio.run(main())
