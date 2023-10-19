from llama_index import VectorStoreIndex, SimpleDirectoryReader, ServiceContext
from llama_index import StorageContext, load_index_from_storage
from llama_index.indices.base import BaseIndex
from llama_index.llms import OpenAI
from ChatGUI import ChatGUI
import tkinter as tk
import openai
import os


def connect_to_openai() -> None:
    """
    Connects to the OpenAI API using the key in the keys folder.
    :return:
    """
    path_to_key = "..\keys\openai_key.txt"
    # open file with key
    with open(path_to_key, "r") as file:
        my_key = file.read()

    openai.api_key = my_key


def data_directory_changed() -> bool:
    """
    Checks if the data directory has changed since the last time the index was created.
    * The check is based on the files names.
    :return: bool
    """
    files = os.listdir("data")
    try:
        with open("storage/current_data_directory.txt", "r") as file:
            current_files = file.readlines()
            current_files = [f.strip() for f in current_files]
            if files == current_files:
                return False
    except FileNotFoundError:
        pass
    return True


def save_current_data_directory() -> None:
    """
    Saves the names of the files of the current data directory, for later comparison.
    :return: None
    """
    data_files = os.listdir("data")
    with open("storage/current_data_directory.txt", "w") as file:
        for f in data_files:
            file.write(f + "\n")


def save_index(index: VectorStoreIndex) -> None:
    """
    Saves the index to storage
    :param index: index to save
    :return: None
    """
    index.storage_context.persist(persist_dir='storage')


def load_index() -> BaseIndex:
    """
    Loads the index from storage
    :return: BaseIndex
    """
    storage_context = StorageContext.from_defaults(persist_dir='storage')
    index = load_index_from_storage(storage_context)
    return index

def load_gpt4(temperature) -> ServiceContext:
    """
    Loads the GPT-4 model
    :return: ServiceContext
    """
    llm = OpenAI(temperature=temperature, model="gpt-4")
    service_context = ServiceContext.from_defaults(llm=llm)
    return service_context

def load_gpt3_5(temperature) -> ServiceContext:
    """
    Loads the GPT-3.5 model
    :return: ServiceContext
    """
    llm = OpenAI(temperature=temperature, model="gpt-3.5-turbo")
    service_context = ServiceContext.from_defaults(llm=llm)
    return service_context


def main():
    gpt4 = True
    temperature = 0.1

    connect_to_openai()

    if data_directory_changed():
        # Load the documents
        documents = SimpleDirectoryReader("data").load_data()
        if gpt4:
            service_context = load_gpt4(temperature)
        else:
            service_context = load_gpt3_5(temperature) # Load gpt-3.5-turbo

        # Create the index
        index = VectorStoreIndex.from_documents(documents, service_context=service_context)
        # Save the index for later use.
        save_index(index)
        save_current_data_directory()
    else:
        # Load the last index with the last model used
        index = load_index()

    # Create the query engine
    # For shorter answers, set 'similarity_top_k' to lower value.
    query_engine = index.as_query_engine(similarity_top_k=5)

    # Create the chat GUI
    root = tk.Tk()
    chat_gui = ChatGUI(root, query_engine)
    # Start the mainloop
    root.mainloop()


if __name__ == '__main__':
    print('Starting...')
    main()
    print('Done')
