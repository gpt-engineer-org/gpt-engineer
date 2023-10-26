from code_vector_repository import CodeVectorRepository
from dotenv import load_dotenv

def main():
    load_dotenv()

    vector_repository = CodeVectorRepository()

    vector_repository.load_from_directory("../example-big")
    chunks = vector_repository.relevent_code_chunks("I would like to add additional steps to the code development process")

    print(f'chunks recieved: {chunks.__len__()}')
    for chunk in chunks:
        print(chunk.get_text)


if __name__ == "__main__":
    main()