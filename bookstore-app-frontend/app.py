import streamlit as st
import requests
import pandas as pd
import os

API_HOST = os.getenv("API_HOST", "backend")
API_PORT = os.getenv("API_PORT", "5000")
API_URL = f"http://{API_HOST}:{API_PORT}/books"

st.set_page_config(page_title="Bookstore Management", page_icon="📚", layout="wide")

st.title("📚 Bookstore Management System")

st.sidebar.title("Navigation")
page = st.sidebar.selectbox("Choose a page", ["View Books", "Add Book", "Manage Inventory"])

def fetch_books():
    try:
        response = requests.get(API_URL)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to fetch books: {response.status_code}")
            return []
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {e}")
        return []

if page == "Add Book":
    st.header("Add a New Book")

    with st.form("add_book"):
        col1, col2 = st.columns(2)

        with col1:
            title = st.text_input("Book Title", "")
            author = st.text_input("Author", "")
            isbn = st.text_input("ISBN", "")

        with col2:
            genre = st.selectbox("Genre", [
                "Fiction", "Non-Fiction", "Mystery", "Romance", "Science Fiction",
                "Fantasy", "Biography", "History", "Self-Help", "Technical", "Other"
            ])
            price = st.number_input("Price ($)", min_value=0.0, step=0.01, format="%.2f")
            quantity = st.number_input("Quantity", min_value=0, step=1)

        description = st.text_area("Description", "")

        submitted = st.form_submit_button("Add Book")

        if submitted:
            if title and author and isbn:
                try:
                    response = requests.post(API_URL, json={
                        "title": title,
                        "author": author,
                        "isbn": isbn,
                        "genre": genre,
                        "price": price,
                        "quantity": quantity,
                        "description": description
                    })

                    if response.status_code == 201:
                        st.success("Book added successfully!")
                        st.rerun()
                    else:
                        st.error(f"Failed to add book: {response.json().get('error', 'Unknown error')}")
                except requests.exceptions.RequestException as e:
                    st.error(f"Connection error: {e}")
            else:
                st.error("Please fill in Title, Author, and ISBN fields.")

elif page == "View Books":
    st.header("Book Inventory")

    books = fetch_books()

    if books:
        books_df = pd.DataFrame(books)

        display_df = books_df.rename(columns={
            '_id': 'ID',
            'title': 'Title',
            'author': 'Author',
            'isbn': 'ISBN',
            'genre': 'Genre',
            'price': 'Price ($)',
            'quantity': 'Stock',
            'description': 'Description'
        })

        if 'Price ($)' in display_df.columns:
            display_df['Price ($)'] = display_df['Price ($)'].apply(lambda x: f"${x:.2f}")

        st.dataframe(
            display_df[['Title', 'Author', 'Genre', 'Price ($)', 'Stock', 'ISBN']],
            hide_index=True,
            use_container_width=True
        )

        st.subheader("Search Books")
        search_term = st.text_input("Search by title or author:")

        if search_term:
            filtered_books = [
                book for book in books
                if search_term.lower() in book['title'].lower()
                or search_term.lower() in book['author'].lower()
            ]

            if filtered_books:
                st.write(f"Found {len(filtered_books)} book(s):")
                for book in filtered_books:
                    with st.expander(f"📖 {book['title']} by {book['author']}"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Genre:** {book['genre']}")
                            st.write(f"**ISBN:** {book['isbn']}")
                            st.write(f"**Price:** ${book['price']:.2f}")
                        with col2:
                            st.write(f"**Stock:** {book['quantity']}")
                            if book['description']:
                                st.write(f"**Description:** {book['description']}")
            else:
                st.write("No books found matching your search.")
    else:
        st.write("No books found in the inventory.")

elif page == "Manage Inventory":
    st.header("Manage Books")

    books = fetch_books()

    if books:
        st.subheader("Edit or Delete Books")

        for book in books:
            with st.expander(f"📚 {book['title']} by {book['author']}"):
                col1, col2, col3 = st.columns([2, 1, 1])

                with col1:
                    st.write(f"**Genre:** {book['genre']}")
                    st.write(f"**ISBN:** {book['isbn']}")
                    st.write(f"**Price:** ${book['price']:.2f}")
                    st.write(f"**Stock:** {book['quantity']}")
                    if book['description']:
                        st.write(f"**Description:** {book['description']}")

                with col2:
                    if st.button("✏️ Edit", key=f"edit_{book['_id']}"):
                        st.session_state[f"editing_{book['_id']}"] = True

                with col3:
                    if st.button("🗑️ Delete", key=f"delete_{book['_id']}"):
                        try:
                            response = requests.delete(f"{API_URL}/{book['_id']}")
                            if response.status_code == 200:
                                st.success("Book deleted successfully!")
                                st.rerun()
                            else:
                                st.error("Failed to delete book")
                        except requests.exceptions.RequestException as e:
                            st.error(f"Connection error: {e}")

                if st.session_state.get(f"editing_{book['_id']}", False):
                    st.write("---")
                    st.write("**Edit Book Details:**")

                    with st.form(f"edit_form_{book['_id']}"):
                        edit_col1, edit_col2 = st.columns(2)

                        with edit_col1:
                            new_title = st.text_input("Title", book['title'], key=f"title_{book['_id']}")
                            new_author = st.text_input("Author", book['author'], key=f"author_{book['_id']}")
                            new_isbn = st.text_input("ISBN", book['isbn'], key=f"isbn_{book['_id']}")

                        with edit_col2:
                            new_genre = st.selectbox("Genre", [
                                "Fiction", "Non-Fiction", "Mystery", "Romance", "Science Fiction",
                                "Fantasy", "Biography", "History", "Self-Help", "Technical", "Other"
                            ], index=["Fiction", "Non-Fiction", "Mystery", "Romance", "Science Fiction",
                                     "Fantasy", "Biography", "History", "Self-Help", "Technical", "Other"].index(book['genre']) if book['genre'] in ["Fiction", "Non-Fiction", "Mystery", "Romance", "Science Fiction", "Fantasy", "Biography", "History", "Self-Help", "Technical", "Other"] else 0, key=f"genre_{book['_id']}")
                            new_price = st.number_input("Price ($)", value=book['price'], min_value=0.0, step=0.01, format="%.2f", key=f"price_{book['_id']}")
                            new_quantity = st.number_input("Quantity", value=book['quantity'], min_value=0, step=1, key=f"quantity_{book['_id']}")

                        new_description = st.text_area("Description", book.get('description', ''), key=f"desc_{book['_id']}")

                        col_save, col_cancel = st.columns(2)

                        with col_save:
                            save_changes = st.form_submit_button("💾 Save Changes")

                        with col_cancel:
                            cancel_edit = st.form_submit_button("❌ Cancel")

                        if save_changes:
                            try:
                                response = requests.put(f"{API_URL}/{book['_id']}", json={
                                    "title": new_title,
                                    "author": new_author,
                                    "isbn": new_isbn,
                                    "genre": new_genre,
                                    "price": new_price,
                                    "quantity": new_quantity,
                                    "description": new_description
                                })

                                if response.status_code == 200:
                                    st.success("Book updated successfully!")
                                    st.session_state[f"editing_{book['_id']}"] = False
                                    st.rerun()
                                else:
                                    st.error("Failed to update book")
                            except requests.exceptions.RequestException as e:
                                st.error(f"Connection error: {e}")

                        if cancel_edit:
                            st.session_state[f"editing_{book['_id']}"] = False
                            st.rerun()
    else:
        st.write("No books found in the inventory.")

st.sidebar.markdown("---")
st.sidebar.info("📚 Simple Bookstore Management System")

try:
    health_response = requests.get(f"http://{API_HOST}:{API_PORT}/health")
    if health_response.status_code == 200:
        st.sidebar.success("🟢 Backend Connected")
    else:
        st.sidebar.error("🔴 Backend Issues")
except:
    st.sidebar.error("🔴 Backend Offline")