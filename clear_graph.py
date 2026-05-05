from storage.graph_store import MemoryGraphStore
graph = MemoryGraphStore()
graph.clear_all()
graph.close()
print("done")