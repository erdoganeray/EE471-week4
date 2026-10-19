from custom_classes import DVD, Book, ItemNotFoundError, ItemStateError, LibraryCollection


def print_separator():
    print("*" * 40)


def main():
    library = LibraryCollection()

    print_separator()
    print("add_item(): each item gets the next id")
    dune_id = library.add_item(Book("Dune", "Frank Herbert", page_count=412))
    interstellar_id = library.add_item(DVD("Interstellar", "Christopher Nolan", duration=169))
    hobbit_id = library.add_item(Book("The Hobbit", "J.R.R. Tolkien", page_count=310))
    print(f"Dune: {dune_id}, Interstellar: {interstellar_id}, The Hobbit: {hobbit_id}")

    print_separator()
    print("get_item() and to_dict():")
    print(library.get_item(dune_id))
    print(library.get_item(dune_id).to_dict())
    print(library.get_item(interstellar_id).to_dict())

    print_separator()
    print("checkout() and return_item():")
    print(library.get_item(dune_id).checkout())
    print(library.get_item(interstellar_id).checkout())  # DVD: message includes the reminder
    print(library.get_item(dune_id).return_item())

    print_separator()
    print("list_items() and list_available():")
    print("All:", [item.title for item in library.list_items()])
    print("Available:", [item.title for item in library.list_items(available=True)])
    print("DVDs:", [item.title for item in library.list_items(item_type="dvd")])
    print("list_available():", library.list_available())

    print_separator()
    print("update_item():")
    updated = library.update_item(hobbit_id, title="The Hobbit (Illustrated)", page_count=320)
    print(updated.to_dict())

    print_separator()
    print("remove_item(): ids are never reused")
    library.remove_item(hobbit_id)
    new_id = library.add_item(Book("1984", "George Orwell", page_count=328))
    print(f"Removed id {hobbit_id}; the next item got id {new_id}")

    print_separator()
    print("Errors:")
    try:
        library.get_item(99)
    except ItemNotFoundError as error:
        print("ItemNotFoundError:", error)

    try:
        library.get_item(interstellar_id).checkout()
    except ItemStateError as error:
        print("ItemStateError:", error)

    try:
        library.get_item(dune_id).return_item()
    except ItemStateError as error:
        print("ItemStateError:", error)

    try:
        library.remove_item(interstellar_id)
    except ItemStateError as error:
        print("ItemStateError:", error)

    try:
        library.update_item(dune_id, is_available=False)
    except ValueError as error:
        print("ValueError:", error)

    try:
        library.list_items(item_type="vinyl")
    except ValueError as error:
        print("ValueError:", error)
    print_separator()


if __name__ == "__main__":
    main()
