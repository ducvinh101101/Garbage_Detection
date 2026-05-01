from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from langchain_community.tools import DuckDuckGoSearchResults

wrapper = DuckDuckGoSearchAPIWrapper(max_results=3)
search = DuckDuckGoSearchResults(api_wrapper=wrapper)
print(search.invoke("cách tái chế nhựa PET"))
