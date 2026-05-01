from googlesearch import search

def test_google_search():
    query = "cách tái chế nhựa PET"
    # Lấy top 3 kết quả
    results = search(query, num_results=3, lang="vi")
    for r in results:
        print(r)

if __name__ == "__main__":
    test_google_search()
