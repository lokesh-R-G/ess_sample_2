from typing import List, Dict

class DependencyEngine:
    @staticmethod
    def topological_sort(components: List[str], dependencies: Dict[str, List[str]]) -> List[str]:
        # Perform Kahn's algorithm or DFS to find calculation order and detect cycles
        in_degree = {u: 0 for u in components}
        adj = {u: [] for u in components}
        
        for u in components:
            for v in dependencies.get(u, []):
                if v in components: # Only consider dependencies within the graph
                    adj[v].append(u)
                    in_degree[u] += 1
                    
        queue = [u for u in components if in_degree[u] == 0]
        order = []
        
        while queue:
            u = queue.pop(0)
            order.append(u)
            for v in adj[u]:
                in_degree[v] -= 1
                if in_degree[v] == 0:
                    queue.append(v)
                    
        if len(order) != len(components):
            raise ValueError("Circular reference detected in component dependencies")
            
        return order
