"""Classes for a small library: media items, books, DVDs and a collection."""


class ItemNotFoundError(Exception):
    """Raised when no item in the collection has the requested id."""


class ItemStateError(Exception):
    """Raised when an action does not fit the item's current state.

    For example, checking out an item that is already checked out, or
    removing an item that is still checked out.
    """


def check_field(name, value):
    """Check a value before it is stored in an editable field.

    Raises:
        ValueError: If title or author is not a non-empty string, or
            page_count or duration is not a positive whole number.
    """
    if name in ("title", "author"):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{name} must be a non-empty string")
    elif name in ("page_count", "duration"):
        # JSON true/false become bool, which Python also treats as int
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise ValueError(f"{name} must be a positive whole number")


class MediaItem:
    """A generic library item, such as a book or a movie.

    Attributes:
        id: The unique id given by LibraryCollection.add_item(), or None if
            the item has not been added to a collection yet.
        title: The title of the item.
        author: The person who made the item, such as an author or a director.
        is_available: True if the item can be checked out right now.
    """

    item_type = "media"
    editable_fields = ("title", "author")

    def __init__(self, title, author, is_available=True):
        self.id = None
        self.title = title
        self.author = author
        self.is_available = is_available

    def checkout(self):
        """Check the item out.

        Returns:
            "Successful checkout".

        Raises:
            ItemStateError: If the item is already checked out.
        """
        if not self.is_available:
            raise ItemStateError(f"{self.title} is already checked out")
        self.is_available = False
        return "Successful checkout"

    def return_item(self):
        """Mark the item as available again.

        Returns:
            "Successful return".

        Raises:
            ItemStateError: If the item is not checked out.
        """
        if self.is_available:
            raise ItemStateError(f"{self.title} is not checked out")
        self.is_available = True
        return "Successful return"

    def to_dict(self):
        """Return the item's data as a dictionary, e.g. for a JSON response."""
        return {
            "id": self.id,
            "type": self.item_type,
            "title": self.title,
            "author": self.author,
            "is_available": self.is_available,
        }

    def __str__(self):
        status = "Available" if self.is_available else "Checked Out"
        return f"{self.title} by {self.author} [{status}]"


class Book(MediaItem):
    """A library book, which also keeps track of its length.

    Attributes:
        page_count: The number of pages in the book.
    """

    item_type = "book"
    editable_fields = MediaItem.editable_fields + ("page_count",)

    def __init__(self, title, author, page_count, is_available=True):
        super().__init__(title, author, is_available)
        self.page_count = page_count

    def to_dict(self):
        """Return the item's data, including the page count."""
        return {**super().to_dict(), "page_count": self.page_count}

    def __str__(self):
        return f"{super().__str__()} ({self.page_count} pages)"


class DVD(MediaItem):
    """A DVD, which reminds the borrower to be careful when it is checked out.

    Attributes:
        duration: The running time of the DVD, in minutes.
    """

    item_type = "dvd"
    editable_fields = MediaItem.editable_fields + ("duration",)

    def __init__(self, title, author, duration, is_available=True):
        super().__init__(title, author, is_available)
        self.duration = duration

    def checkout(self):
        """Check the DVD out and add a care reminder to the success message.

        The checkout itself is done by MediaItem.checkout(), which raises
        ItemStateError if the DVD is already out.

        Returns:
            The MediaItem.checkout() message followed by the care reminder.
        """
        result = super().checkout()
        return f"{result}. Handle with care: Do not scratch the disc."

    def to_dict(self):
        """Return the item's data, including the duration."""
        return {**super().to_dict(), "duration": self.duration}


class LibraryCollection:
    """A collection of library items of any type.

    Attributes:
        items: The items added so far, in the order they were added.
    """

    def __init__(self):
        self.items = []
        self._next_id = 1

    def add_item(self, item):
        """Add an item to the collection and give it a unique id.

        Ids start at 1 and are never reused, even after an item is removed.

        Args:
            item: A MediaItem, or one of its subclasses such as Book or DVD.

        Returns:
            The id given to the item.
        """
        item.id = self._next_id
        self._next_id += 1
        self.items.append(item)
        return item.id

    def create_item(self, item_type, /, **fields):
        """Create a Book or DVD from its field values and add it.

        The "/" lets fields contain any name, so a wrong field is reported
        as a ValueError instead of a Python TypeError.

        Args:
            item_type: "book" or "dvd".
            **fields: title and author, plus page_count for a book or
                duration for a DVD.

        Returns:
            The new item.

        Raises:
            ValueError: If the type is unknown, a field is missing or extra,
                or a value is not valid.
        """
        if item_type not in ("book", "dvd"):
            raise ValueError("type must be 'book' or 'dvd'")
        item_class = Book if item_type == "book" else DVD
        if set(fields) != set(item_class.editable_fields):
            raise ValueError(f"a {item_type} needs exactly these fields: {', '.join(item_class.editable_fields)}")
        for name, value in fields.items():
            check_field(name, value)
        item = item_class(**fields)
        self.add_item(item)
        return item

    def get_item(self, item_id):
        """Find an item by its id.

        Raises:
            ItemNotFoundError: If no item has this id.
        """
        for item in self.items:
            if item.id == item_id:
                return item
        raise ItemNotFoundError(f"No item with id {item_id}")

    def list_items(self, available=None, item_type=None):
        """List the items, optionally filtered.

        Args:
            available: True or False to keep only available or checked-out
                items, None to keep both.
            item_type: "book", "dvd" or "media" to keep one type, None to keep
                all types.

        Returns:
            A list of items, in the order they were added.

        Raises:
            ValueError: If a filter has an unknown value.
        """
        if available is not None and not isinstance(available, bool):
            raise ValueError("available must be True, False or None")
        if item_type not in (None, "media", "book", "dvd"):
            raise ValueError("item_type must be 'book', 'dvd' or 'media'")
        return [
            item for item in self.items
            if (available is None or item.is_available == available)
            and (item_type is None or item.item_type == item_type)
        ]

    def update_item(self, item_id, /, **fields):
        """Change some editable fields of an item.

        Editable fields are title and author, plus page_count for books and
        duration for DVDs. Nothing is changed if any field is not allowed.

        Returns:
            The updated item.

        Raises:
            ItemNotFoundError: If no item has this id.
            ValueError: If no field is given, a field is id, type,
                is_available or not editable for this item, or a value is
                not valid.
        """
        item = self.get_item(item_id)
        if not fields:
            raise ValueError("no fields to update")
        for name, value in fields.items():
            if name in ("id", "type", "is_available"):
                raise ValueError(f"{name} cannot be changed")
            if name not in item.editable_fields:
                raise ValueError(f"{name} is not an editable field of a {item.item_type}")
            check_field(name, value)
        for name, value in fields.items():
            setattr(item, name, value)
        return item

    def replace_item(self, item_id, /, **fields):
        """Replace all editable fields of an item at once.

        Works like update_item(), but every editable field must be given.

        Raises:
            ItemNotFoundError: If no item has this id.
            ValueError: If an editable field is missing, or for the same
                reasons as update_item().
        """
        item = self.get_item(item_id)
        missing = [name for name in item.editable_fields if name not in fields]
        if missing:
            raise ValueError(f"missing fields: {', '.join(missing)}")
        return self.update_item(item_id, **fields)

    def remove_item(self, item_id):
        """Remove an item from the collection.

        Raises:
            ItemNotFoundError: If no item has this id.
            ItemStateError: If the item is checked out.
        """
        item = self.get_item(item_id)
        if not item.is_available:
            raise ItemStateError("Cannot delete a checked-out item")
        self.items.remove(item)

    def list_available(self):
        """List the titles of the items that can be checked out right now.

        Returns:
            A list of title strings, in the order the items were added.
        """
        return [item.title for item in self.items if item.is_available]
