from scholarly import scholarly

def search_papers(topic):
    search_query = scholarly.search_pubs(topic)
    papers = []
    try:
        for i in range(5):
            paper = next(search_query)
            papers.append(paper["bib"])
    except StopIteration:
        pass

    return papers


papers = search_papers('GPT-4')
for paper in papers:
    print(paper['title'])
    print(paper["abstract"])
    print(paper.keys())
    print("\n")
