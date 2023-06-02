from sentence_transformers import SentenceTransformer
#test = ["This is an example sentence", "Each sentence is converted"]

model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
#embeddings = model.encode(test)
#print(embeddings)

def embed(sentences):
    return model.encode(sentences)