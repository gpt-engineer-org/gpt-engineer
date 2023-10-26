from code_vector_repository import CodeVectorRepository
from dotenv import load_dotenv

def main():
    load_dotenv()

    vector_repository = CodeVectorRepository()

    vector_repository.load_from_directory("../example-big")
    response = vector_repository.query("What file would i change to add new steps to the code generation process?")
    print(response)

if __name__ == "__main__":
    main()