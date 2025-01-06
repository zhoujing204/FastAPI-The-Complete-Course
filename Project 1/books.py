import logging
from fastapi import Body, FastAPI, HTTPException

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='app.log',  # Saves logs to app.log file
    filemode='a'  # 'a' for append mode
)

logger = logging.getLogger(__name__)
app = FastAPI()


BOOKS = [
    {'title': 'Title1', 'author': 'Author1', 'category': 'science'},
    {'title': 'Title2', 'author': 'Author2', 'category': 'science'},
    {'title': 'Title3', 'author': 'Author3', 'category': 'history'},
    {'title': 'Title4', 'author': 'Author4', 'category': 'math'},
    {'title': 'Title5', 'author': 'Author5', 'category': 'math'},
    {'title': 'Title6', 'author': 'Author2', 'category': 'math'}
]


@app.get("/books")
async def read_all_books():
    logger.debug("Read all books")
    return BOOKS


@app.get("/books/title/{book_title}")
async def read_book(book_title: str):
    for book in BOOKS:
        if book.get('title').casefold() == book_title.casefold():
            return book


@app.get("/books/category/{category}")
async def read_category_by_query(category: str):
    books_to_return = []
    for book in BOOKS:
        if book.get('category').casefold() == category.casefold():
            books_to_return.append(book)
        logger.debug(books_to_return)
    return books_to_return


# Get all books from a specific author using path or query parameters
@app.get("/books/byauthor/")
async def read_books_by_author_path(author: str):
    books_to_return = []
    for book in BOOKS:
        if book.get('author').casefold() == author.casefold():
            books_to_return.append(book)

    return books_to_return


@app.get("/books/{book_author}/")
async def read_author_category_by_query(book_author: str, category: str):
    books_to_return = []
    for book in BOOKS:
        if book.get('author').casefold() == book_author.casefold() and \
                book.get('category').casefold() == category.casefold():
            books_to_return.append(book)

    return books_to_return


@app.post("/books/create_book")
async def create_book(new_book=Body()):
    BOOKS.append(new_book)


@app.put("/books/update_book")
async def update_book(updated_book=Body()):
    for i in range(len(BOOKS)):
        if BOOKS[i].get('title').casefold() == updated_book.get('title').casefold():
            BOOKS[i] = updated_book

@app.put("/books/update_book/{title}")
async def update_book(title: str, updated_book=Body()):
    for i in range(len(BOOKS)):
        if BOOKS[i].get('title').casefold() == title.casefold():
            # Keep the original title to prevent title mismatch
            updated_book['title'] = title
            BOOKS[i] = updated_book
            return {"message": "Book updated successfully", "book": BOOKS[i]}

    raise HTTPException(status_code=404, detail="Book not found")


@app.delete("/books/delete_book/{book_title}")
async def delete_book(book_title: str):
    for i in range(len(BOOKS)):
        if BOOKS[i].get('title').casefold() == book_title.casefold():
            # Remove the book from the list when found the first book title match
            BOOKS.pop(i)
            break


from fastapi import Query



@app.get("/books/search")
async def search_books(
    title: str | None = Query(None),
    author: str | None = Query(None),
    category: str | None = Query(None)
):

    """querying books by any combination of conditions
    using optional query parameters"""
    filtered_books = BOOKS.copy()

    if title:
        filtered_books = [
            book for book in filtered_books
            if book.get('title').casefold() == title.casefold()
        ]

    if author:
        filtered_books = [
            book for book in filtered_books
            if book.get('author').casefold() == author.casefold()
        ]

    if category:
        filtered_books = [
            book for book in filtered_books
            if book.get('category').casefold() == category.casefold()
        ]

    return filtered_books